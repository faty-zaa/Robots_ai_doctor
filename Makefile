
.PHONY: install run model check clean help

UV = uv

install:
	@$(UV) sync

model:
	ollama pull gemma3:4b

run:
	@$(UV) run python3 web.py

check:
	@$(UV) run python -m compileall -q src

clean:
	@cleanpy .

help:
	@echo "RoboDoctor - Available commands:"
	@echo "  make install  - Install dependencies"
	@echo "  make model    - Download the Ollama model"
	@echo "  make run      - Launch the application"
	@echo "  make check    - Check Python syntax"
	@echo "  make clean    - Clean Python cache files"
