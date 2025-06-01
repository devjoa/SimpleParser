
.PHONY: test
test:
	@python -m unittest tests.test_simpleparser

.PHONY: build
build:
	@python -m build
