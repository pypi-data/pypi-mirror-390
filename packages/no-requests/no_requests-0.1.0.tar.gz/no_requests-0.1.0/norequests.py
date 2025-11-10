# no-requests: A lightweight, dependency-free HTTP client
# See https://github.com/gatopeich/no-requests

import urllib.request
import urllib.parse
import json
import warnings

class Response:
    def __init__(self, resp):
        self.status_code = resp.getcode()
        self.headers = dict(resp.getheaders())
        self._raw = resp.read()
        self.url = resp.geturl()

    @property
    def content(self):
        return self._raw

    @property
    def text(self):
        return self._raw.decode('utf-8', errors='replace')

    def json(self):
        return json.loads(self.text)

def _request(method, url, *, params=None, data=None, json_=None, headers=None, timeout=9):
    if not url.startswith("https://"):
        warnings.warn("You are making a non-SSL request. This is insecure!", UserWarning)
    if params:
        url += '?' + urllib.parse.urlencode(params)
    if json_ is not None:
        data = json.dumps(json_).encode('utf-8')
        headers = headers or {}
        headers['Content-Type'] = 'application/json'
    elif isinstance(data, dict):
        data = urllib.parse.urlencode(data).encode('utf-8')
        headers = headers or {}
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    req = urllib.request.Request(url, method=method.upper(), data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return Response(resp)

def get(url, *, params=None, headers=None, timeout=9):
    return _request('GET', url, params=params, headers=headers, timeout=timeout)

def post(url, *, data=None, json=None, headers=None, timeout=9):
    return _request('POST', url, data=data, json_=json, headers=headers, timeout=timeout)

def put(url, *, data=None, json=None, headers=None, timeout=9):
    return _request('PUT', url, data=data, json_=json, headers=headers, timeout=timeout)

def delete(url, *, headers=None, timeout=9):
    return _request('DELETE', url, headers=headers, timeout=timeout)
