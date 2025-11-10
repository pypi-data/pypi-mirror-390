GIT_ROOT ?= $(shell git rev-parse --show-toplevel)

format:	## Run code autoformatter (black).
	black .

lint:	## Run linters: pre-commit, black, isort, autoflake, etc.
	pre-commit install && pre-commit run --all-files

test:	## Run tests.
	pytest tests
