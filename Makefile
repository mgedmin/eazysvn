.PHONY: all
all:
	@echo "Nothing to build here"

.PHONY: test
test:                           ##: run tests
	tox p

.PHONY: coverage
coverage:                       ##: measure test coverage
	tox -e coverage
	coverage report -m --fail-under=100

.PHONY: lint
lint:                           ##: run all the linters
	tox p -e flake8,isort,check-manifest,check-python-versions



FILE_WITH_VERSION = eazysvn.py
include release.mk
