PYTHON := venv/bin/python

.PHONY: help
help:
	@echo "clean - remove all generated data"
	@echo "lint - check style with flake8"
	@echo "dist - package"
	@echo "tag - set a tag with the current version number"
	@echo "release-check - check release tag"

.PHONY: ALL
ALL: runserver

.PHONY: clean
clean:
	find . -name *.pyc -delete
	find . -name __pycache__ -type d -delete
	rm -rf venv build

venv:
	python3 -m virtualenv venv
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -r dev_requirements.txt

.PHONY: runserver
runserver: venv
	$(PYTHON) manage.py migrate
	$(PYTHON) manage.py runserver

.PHONY : lint
lint: venv
	$(PYTHON) -m flake8

test: venv
	$(PYTHON) -m pytest

.PHONY: dist
dist: #clean venv
	$(PYTHON) setup.py sdist bdist_wheel
	ls -l dist

.PHONY: tag
tag:
	$(PYTHON) setup.py tag

.PHONY: release-check
release-check:
	$(PYTHON) setup.py release_check
