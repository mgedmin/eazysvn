.PHONY: all
all:
	@echo "Nothing to build here"

.PHONY: test
test:                           ##: run tests
	tox -p auto

.PHONY: coverage
coverage:                       ##: measure test coverage
	tox -e coverage,coverage3 -- -p
	coverage combine
	coverage report -m --fail-under=100


FILE_WITH_VERSION = eazysvn.py
include release.mk
