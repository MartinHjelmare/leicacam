# leicacam

[![build-badge]][build]
[![pypi-version]][pypi]
[![wheel]][pypi]
[![Documentation Status][docs-build-badge]][docs]

## Overview

Control Leica microscopes with python

## Installation

- **The latest version of leicacam requires Python 3.10+**
- If you need to keep using Python 2.7, pin your version of leicacam to 0.3.0.

Install using `pip`:

```bash
pip3 install leicacam
```

## Example

### Communicate with microscope

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

See available commands in the API reference: [http://leicacam.rtfd.org](http://leicacam.rtfd.org).

## Development

Install dependencies and link development version of leicacam to pip:

```bash
pip install -r requirements_dev.txt
```

### Code formatting

We use black code formatter to automatically format the code.

```bash
black ./
```

### Testing

```bash
tox
```

### Build documentation locally

To build the documentation:

```bash
pip install -r docs/requirements.txt
make docs
```

[build-badge]: https://github.com/MartinHjelmare/leicacam/workflows/Test/badge.svg
[build]: https://github.com/MartinHjelmare/leicacam/actions
[pypi-version]: https://img.shields.io/pypi/v/leicacam.svg
[pypi]: https://pypi.org/project/leicacam/
[wheel]: https://img.shields.io/pypi/wheel/leicacam.svg
[docs-build-badge]: https://readthedocs.org/projects/leicacam/badge/?version=latest
[docs]: https://leicacam.readthedocs.io/en/latest/?badge=latest
