# no-requests

**Author:** gatopeich ~ https://github.com/gatopeich/no-requests

A lightweight, safe, dependency-free HTTP client for Python 3, inspired by `requests`, but with no dependencies outside the standard library.

## Features

- Only the most-used API: `get`, `post`, `put`, `delete`
- No dependencies outside Python 3 standard library
- Default timeout is 9 seconds
- Warns (but does not fail) on non-SSL (non-HTTPS) requests
- Simple `Response` object with `.status_code`, `.headers`, `.url`, `.content`, `.text`, `.json()`

## Usage

```python
import norequests as requests

resp = requests.get('https://httpbin.org/get')
print(resp.status_code)
print(resp.json())
```

## How to use no-requests in place of requests

If you want to replace the `requests` module in your project with `no-requests`, you can do so by adding the following line to your `requirements.txt`:

```
requests @ git+https://github.com/gatopeich/no-requests.git
```

This will install `no-requests` as if it were `requests`, letting you import it as usual:

```python
import requests

resp = requests.get('https://example.com')
print(resp.status_code)
```

**Note:**  
This works because the package provides a `requests`-like API and will be installed as the `requests` package in your environment, overriding the original. Be sure to remove any other lines referring to `requests` in your `requirements.txt` to avoid conflicts.

## License

MIT
