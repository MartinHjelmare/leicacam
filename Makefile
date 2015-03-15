.PHONY: help clean clean-pyc clean-build list test test-all coverage docs release sdist

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "testall - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
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
	flake8 leicacam test

test:
	tox

coverage:
	coverage run --source leicacam setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

api-docs:
	sphinx-apidoc -Mf -o docs/ leicacam

docs:
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

release: clean rst
	python setup.py sdist upload
	python setup.py bdist_wheel upload

rst:
	if type pandoc; then pandoc --from=markdown --to=rst README.md -o README.rst; fi

sdist: clean rst
	python setup.py sdist
	python setup.py bdist_wheel upload
	ls -l dist
