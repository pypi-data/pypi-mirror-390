# imp2importlib
![Python Versions](https://img.shields.io/pypi/pyversions/imp2importlib)
[![LatestVersionInPypi](https://img.shields.io/pypi/v/imp2importlib.svg?style=flat)](https://pypi.python.org/pypi/imp2importlib)
[![GithubActionResult](https://github.com/waketzheng/imp2importlib/workflows/ci/badge.svg)](https://github.com/waketzheng/imp2importlib/actions?query=workflow:ci)
![Mypy coverage](https://img.shields.io/badge/mypy-100%25-green.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Fixes `ModuleNotFoundError: No module named 'imp'` for Python3.12+

## Install

```
pip install imp2importlib
```

## Usage
```
from imp import load_source
```
