import sys
from pathlib import Path

from richer_prompt import __version__

DOCS_PATH = Path(__file__).resolve().parent
sys.path.insert(0, DOCS_PATH.as_posix())

project = "richer-prompt"
author = "Gabriel Mello Silva"
release = __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "sphinx_inline_tabs",
    "ext.snapshot",  # custom extension for rendering prompt snapshots
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_theme_options = {
    "source_repository": "https://github.com/gabriel-msilva/richer-prompt/",
    "source_branch": "main",
    "source_directory": "docs",
}

autosummary_generate = True
autoclass_content = "class"
autodoc_default_options = {"members": True, "undoc-members": False}

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
