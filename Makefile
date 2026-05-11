.PHONY: help
help: ## Show this help message
	@printf "\033[32mUsage:\033[0m \033[36mmake <COMMAND>\033[0m\n"
	@echo ""
	@printf "\033[32mCommands:\033[0m\n"
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F ':.*## ' '{ printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2 }'

.PHONY: setup
setup: ## Install dependencies and pre-commit hooks
ifeq (,$(wildcard uv.lock))
	uv lock
endif

	uv sync --frozen
	uv run pre-commit install

.PHONY: tests
tests: ## Run tests with pytest
	uv run pytest

.PHONY: pre-commit
pre-commit: ## Run pre-commit checks on all files
	uv run pre-commit run --all-files
