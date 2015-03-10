leicacam
========

|build-status-image| |pypi-version| |wheel|

Overview
--------

Control Leica microscopes with python

Installation
------------

Install using ``pip``...

.. code:: bash

    pip install leicacam

Example
-------

TODO: Write example.

API reference
-------------

API reference is at http://leicacam.rtfd.org.

Development
-----------

Install dependencies and link development version of leicacam to pip:

.. code:: bash

    pip install -r dev-requirements.txt
    ./setup.py develop

Testing
~~~~~~~

.. code:: bash

    tox

Build documentation locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To build the documentation, you'll need sphinx:

.. code:: bash

    pip install -r docs/requirements.txt

To build the documentation:

.. code:: bash

    make docs

.. |build-status-image| image:: https://secure.travis-ci.org/arve0/leicacam.png?branch=master
   :target: http://travis-ci.org/arve0/leicacam?branch=master
.. |pypi-version| image:: https://pypip.in/version/leicacam/badge.svg
   :target: https://pypi.python.org/pypi/leicacam
.. |wheel| image:: https://pypip.in/wheel/leicacam/badge.png
   :target: https://pypi.python.org/pypi/leicacam
