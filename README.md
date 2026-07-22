# richer-prompt

[![CI - Test, Build and Release](https://github.com/gabriel-msilva/richer-prompt/actions/workflows/test-build-release.yaml/badge.svg)](https://github.com/gabriel-msilva/richer-prompt/actions/workflows/test-build-release.yaml)
![PyPI - Version](https://img.shields.io/pypi/v/richer-prompt)
![PyPI - License](https://img.shields.io/pypi/l/richer-prompt)

**Beautiful, Rich-native interactive prompts for Python.**

_richer-prompt_ provides interactive terminal prompts built on top of [Rich](https://github.com/Textualize/rich).

**Visit the documentation**: [richer-prompt.readthedocs.io](https://richer-prompt.readthedocs.io/)

![richer-prompt demo](docs/assets/demo.gif)

_richer-prompt_ is designed for applications that already use `rich` and want interactive
prompts that integrate naturally with the rest of their terminal output.
Instead of introducing a separate rendering system or requiring a full TUI framework,
it extends the `rich` experience with beautiful, composable prompts.

- **Focused**: provides high-quality interactive prompts without requiring a full TUI framework.
- **Rich-native**: designed to blend seamlessly with `rich`'s rendering, colors, and layout.
- **Beautiful by default**: polished prompts inspired by Claude Code without manual styling.
- **Fully typed**: modern type hints for better editor support and safer code.

## Installation

You can install `richer-prompt` from PyPI with `pip` or your favorite package manager:

```sh
pip install richer-prompt
```

```sh
uv add richer-prompt
```

## Demo

To check if `richer-prompt` was installed correctly, and to see a quick demo of its capabilities,
run the following from the command line:

```sh
python -m richer_prompt
```

## Quickstart

> [!TIP]
> See the [documentation](https://richer-prompt.readthedocs.io/) for the full guide and API reference.

Every prompt shares the same API as
[`rich.prompt.Prompt`](https://rich.readthedocs.io/en/stable/prompt.html):
call an instance for a reusable prompt, or use the `.ask()` class method for a one-off prompt.
Use `Choice` objects to add labels and descriptions to the options:

```python
from richer_prompt import Choice, Select, Tabs

# One-off prompt
Select.ask("Select a color:", choices=["Red", "Green", "Blue"])

# Reusable prompt instance
confirm_action = Tabs(
    "Do you want to continue?",
    choices=[
        Choice(value=False, label="No"),
        Choice(value=True, label="Yes", description="This action cannot be undone"),
    ]
)
confirm_action()
```

`richer-prompt` provides four prompt types: `Select`, `MultiSelect`, `Tabs`, and `Form`.

## Development

The development environment requires [uv](https://docs.astral.sh/uv/getting-started/installation/) installed.
[Makefile](./Makefile) has useful commands for development:

```console
$ make help
Usage: make <COMMAND>

Commands:
  setup        Install dependencies and pre-commit hooks
  tests        Run tests with pytest
  pre-commit   Run pre-commit checks on all files
  help         Show this help message
```

## Documentation

The documentation files are located in [docs/](./docs/) directory
and written with [Sphinx](https://www.sphinx-doc.org/en/).

```console
$ make -C docs help
Usage: make <COMMAND>

Commands:
  demo    Generate demo GIF
  build   Build Sphinx docs
  serve   Serve Sphinx docs locally with live reload
  clean   Remove build artifacts
  help    Show this help message
```

Notes:

- Generated HTML output is written to `docs/_build/html` (ignore by Git).
- The demo GIF records the current terminal and this is not exactly reproduced.
