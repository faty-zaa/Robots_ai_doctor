
UV       = uv
PYTHON   = python
SRC      = src
MAIN     = main.py
TESTS    = tests

.PHONY: install run check lint format test clean help

install:
	@$(UV) sync ||  true

run:
	@$(UV) run $(PYTHON) $(MAIN) ||  true

check:
	@$(UV) run mypy $(SRC) $(MAIN) ||  true

lint:
	@$(UV) run flake8 $(SRC) $(MAIN) ||  true

format:
	@$(UV) run black $(SRC) $(MAIN) ||  true

test:
	@$(UV) run pytest $(TESTS) ||  true

clean:
	@cleanpy . || true

help:
	@echo "Available commands:"
	@echo "  make install  - Install project dependencies"
	@echo "  make run      - Run RoboDoctor"
	@echo "  make check    - Run mypy type checking"
	@echo "  make lint     - Run flake8 linting"
	@echo "  make format   - Format code with Black"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Remove generated cache files"
