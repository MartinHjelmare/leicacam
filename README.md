# leicacam

[![build-status-image]][travis]
[![pypi-version]][pypi]
[![wheel]][pypi]

## Overview

Control Leica microscopes with python

## Installation

Install using `pip`...

```bash
pip install leicacam
```

## Example

TODO: Write example.

## API reference

API reference is at http://leicacam.rtfd.org.

## Development
Install dependencies and link development version of leicacam to pip:
```bash
pip install -r dev-requirements.txt
./setup.py develop
```

### Testing
```bash
tox
```

### Build documentation locally
To build the documentation, you'll need sphinx:
```bash
pip install -r docs/requirements.txt
```

To build the documentation:
```bash
make docs
```



[build-status-image]: https://secure.travis-ci.org/arve0/leicacam.png?branch=master
[travis]: http://travis-ci.org/arve0/leicacam?branch=master
[pypi-version]: https://pypip.in/version/leicacam/badge.svg
[pypi]: https://pypi.python.org/pypi/leicacam
[wheel]: https://pypip.in/wheel/leicacam/badge.png
