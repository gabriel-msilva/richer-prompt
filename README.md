# richer-prompt

[![CI - Test, Build and Release](https://github.com/gabriel-msilva/richer-prompt/actions/workflows/test-build-release.yaml/badge.svg)](https://github.com/gabriel-msilva/richer-prompt/actions/workflows/test-build-release.yaml)
![PyPI - Version](https://img.shields.io/pypi/v/richer-prompt)
![PyPI - License](https://img.shields.io/pypi/l/richer-prompt)

_richer-prompt_ provides interactive terminal prompts built on top of [Rich](https://github.com/Textualize/rich).

**Visit the documentation**: [richer-prompt.readthedocs.io](https://richer-prompt.readthedocs.io/)

![richer-prompt demo](docs/assets/demo.gif)

## Installation

You can install `richer-prompt` from PyPI with `pip` or your favorite package manager:

```sh
pip install richer-prompt
```

```sh
uv install richer-prompt
```

## Demo

To check if `richer-prompt` was installed correctly, and to see a quick demo of its capabilities,
run the following from the command line:

```sh
python -m richer_prompt
```

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

- Generated HTML output is written to `_build/html`.
- The demo GIF records the current terminal and this is not exactly reproduced.
