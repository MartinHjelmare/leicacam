.PHONY: help clean clean-build clean-pyc lint test test-all coverage api-docs docs release test-release sdist

help:
	@echo "clean - run both clean-build and clean-pyc"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8, pylint and pydocstyle"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "api-docs - generate leicacam rst file for Sphinx HTML documentation"
	@echo "release - package and upload a release to PyPI"
	@echo "test-release - package and upload a release to test PyPI"
	@echo "sdist - package"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:
	tox -e lint

test:
	pytest -v test/

test-all:
	tox

coverage:
	pytest -v --cov-report term-missing --cov=leicacam test/

api-docs:
	sphinx-apidoc -MfT -o docs/ leicacam

docs:
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

release: clean
	python setup.py sdist bdist_wheel
	twine upload dist/*

test-release: clean
	python setup.py sdist bdist_wheel
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

sdist: clean
	python setup.py sdist bdist_wheel
	ls -l dist
