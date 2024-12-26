#!/usr/bin/env python
"""Set up package."""

from pathlib import Path

from setuptools import find_packages, setup

PROJECT_DIR = Path(__file__).parent.resolve()
VERSION = (PROJECT_DIR / "leicacam" / "VERSION").read_text(encoding="utf-8").strip()

README_FILE = PROJECT_DIR / "README.md"
LONG_DESCRIPTION = README_FILE.read_text(encoding="utf-8")


setup(
    name="leicacam",
    version=VERSION,
    description="Control Leica microscopes with python",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Arve Seljebu",
    author_email="arve.seljebu@gmail.com",
    url="https://github.com/MartinHjelmare/leicacam",
    packages=find_packages(exclude=["test", "test.*"]),
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=["async_timeout", "pydebug"],
    license="MIT",
    zip_safe=False,
    keywords="leicacam",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
