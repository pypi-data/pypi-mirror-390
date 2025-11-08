.PHONY: help install-lint lint lint-fix format format-fix

help:
	@echo "Usage: make <target>"
	@echo "Targets:"
	@echo "  install-lint   Install ruff (via uv if available, else pip)"
	@echo "  lint           Run ruff checks"
	@echo "  format         Check formatting (no changes)"
	@echo "  format-fix     Auto-format files"

install-lint:
	@if command -v uv >/dev/null 2>&1; then \
		if [ -n "$$VIRTUAL_ENV" ]; then \
			uv pip install ruff; \
		else \
			uv pip install --system ruff; \
		fi; \
	else \
		pip install ruff; \
	fi

lint:
	python -m ruff check .

lint-fix:
	python -m ruff check --fix .

format:
	python -m ruff format --check .

format-fix:
	python -m ruff format .


