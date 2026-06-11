.DEFAULT_GOAL = help

ASSETS_DIR = assets
SOURCE_DIR = .
BUILD_DIR = _build/html


.PHONY: demo
demo: ## Generate demo GIF
	uv run --with asciinema \
		asciinema rec -c "python -m richer_prompt" assets/demo.cast
	uvx --from asciinema-gif-generator \
		agg --cols 95 --rows 12 --theme github-dark assets/demo.cast assets/demo.gif

.PHONY: build
build: ## Build Sphinx docs
	uv run --group docs sphinx-build -W --keep-going -b html $(SOURCE_DIR) $(BUILD_DIR)

.PHONY: serve
serve: ## Serve Sphinx docs locally with live reload
	uv run --group docs sphinx-autobuild $(SOURCE_DIR) $(BUILD_DIR)

.PHONY: clean
clean: ## Remove build artifacts
	rm -rf $(BUILD_DIR)

.PHONY: help
help: ## Show this help message
	@printf "\033[32mUsage:\033[0m \033[36mmake <COMMAND>\033[0m\n"
	@echo ""
	@printf "\033[32mCommands:\033[0m\n"
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F ':.*## ' '{ printf "  \033[36m%-7s\033[0m %s\n", $$1, $$2 }'
