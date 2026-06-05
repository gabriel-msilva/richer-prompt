from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))

project = "richer-prompt"
author = "Gabriel Mello Silva"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "sphinx_inline_tabs",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_theme_options = {
    "source_repository": "https://github.com/gabriel-msilva/richer-prompt/",
    "source_branch": "main",
    "source_directory": "docs/",
}

autosummary_generate = True
autoclass_content = "class"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
