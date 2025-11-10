from setuptools import setup

setup(
    name="no-requests",
    version="0.1.0",
    py_modules=["norequests"],
    description="A lightweight, dependency-free, requests-like HTTP client with safe defaults",
    author="gatopeich",
    python_requires=">=3.6",
    url="https://github.com/gatopeich/no-requests",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
)