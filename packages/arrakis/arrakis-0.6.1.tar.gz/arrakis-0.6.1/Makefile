.PHONY: help
help :
	@echo
	@echo 'Commands:'
	@echo
	@echo '  make test                  run tests'
	@echo '  make lint                  run linter'
	@echo '  make format                run code formatter'
	@echo '  make check                 run static type checker'
	@echo

.PHONY: test
test :
	pytest -v --cov=arrakis --cov-report=term-missing .

.PHONY: lint
lint :
	ruff check

.PHONY: format
format :
	ruff format
	ruff check --fix

.PHONY: check
check :
	mypy .

.PHONY: all
all : format lint check test
