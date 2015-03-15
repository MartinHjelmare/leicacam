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

**communicate with microscope**
```python
from leicacam import CAM

cam = CAM()   # initiate and connect, default localhost:8895

# some commands are created as short hands
# start matrix scan
response = cam.start_scan()
print(response)

# but you could also create your own command with a list of tuples
command = [('cmd', 'enableall'),
           ('value', 'true')]
response = cam.send(command)
print(response)

# or even send it as a bytes string (note the b)
command = b'/cmd:enableall /value:true'
response = cam.send(command)
print(response)
```

## Documentation

See available commands in the API reference: http://leicacam.rtfd.org.

## Development
Install dependencies and link development version of leicacam to pip:
```bash
pip install -r dev-requirements.txt
./setup.py develop
```

### Testing
```bash
pip install tox
tox
```

### Build documentation locally
To build the documentation:
```bash
make docs
```



[build-status-image]: https://secure.travis-ci.org/arve0/leicacam.png?branch=master
[travis]: http://travis-ci.org/arve0/leicacam?branch=master
[pypi-version]: https://pypip.in/version/leicacam/badge.svg
[pypi]: https://pypi.python.org/pypi/leicacam
[wheel]: https://pypip.in/wheel/leicacam/badge.png
