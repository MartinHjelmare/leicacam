#!/usr/bin/env python
"""Set up package."""
import os
from setuptools import setup


README = open('README.md').read()

with open(os.path.join('leicacam', 'VERSION')) as version_file:
    VERSION = version_file.read().strip()

setup(
    name='leicacam',
    version=VERSION,
    description='Control Leica microscopes with python',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Arve Seljebu',
    author_email='arve.seljebu@gmail.com',
    url='https://github.com/arve0/leicacam',
    packages=[
        'leicacam',
    ],
    package_dir={'leicacam': 'leicacam'},
    package_data={'leicacam': ['VERSION']},
    include_package_data=True,
    install_requires=[
        'pydebug'
    ],
    extras_require={
        'asyncio':  ['async_timeout'],
    },
    license='MIT',
    zip_safe=False,
    keywords='leicacam',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
