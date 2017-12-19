PYTHON = python
FILE_WITH_VERSION = eazysvn.py
FILE_WITH_CHANGELOG = CHANGES.rst

.PHONY: default
default:
	@echo "Nothing to build here"

.PHONY: check test
check test:
	py.test eazysvn.py tests.py

.PHONY: coverage
coverage:
	tox -e coverage,coverage3 -- -p
	coverage combine
	coverage report -m --fail-under=100

include release.mk
