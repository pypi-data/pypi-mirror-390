from __future__ import annotations

import importlib.metadata
from typing import Any

project = "Pigreads"
copyright = "2024, Desmond Kabus"
author = "Desmond Kabus"
version = release = importlib.metadata.version("pigreads")

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinx_click",
    "sphinx_lfs_content",
    "sphinxcontrib.autodoc_pydantic",
]

source_suffix = [".rst", ".md"]
exclude_patterns = [
    "_build",
    "**.ipynb_checkpoints",
    "Thumbs.db",
    ".DS_Store",
    ".env",
    ".venv",
]

html_logo = "../logo.png"
html_favicon = "favicon.ico"
html_theme = "furo"

html_theme_options: dict[str, Any] = {
    "source_repository": "https://gitlab.com/pigreads/pigreads",
    "source_branch": "main",
    "source_directory": "docs/",
}

myst_enable_extensions = [
    "colon_fence",
]

intersphinx_mapping = {
    "click": ("https://click.palletsprojects.com/en/stable", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "pydantic": ("https://docs.pydantic.dev/latest", None),
    "python": ("https://docs.python.org/3", None),
    "pyopencl": ("https://documen.tician.de/pyopencl", None),  # codespell: disable
}

nitpick_ignore = [
    ("py:class", "numpy.int32"),  # TODO: remove when possible
    ("py:class", "numpy.int64"),  # TODO: remove when possible
    ("py:class", "numpy.float32"),  # TODO: remove when possible
    ("py:class", "numpy.float64"),  # TODO: remove when possible
    ("py:class", "_io.StringIO"),
    ("py:class", "_io.BytesIO"),
    ("py:class", "pathlib._local.Path"),
    ("py:class", "pybind11_builtins.pybind11_object"),
]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "no-value": True,
    "special-members": "__call__",
}

always_document_param_types = True
typehints_fully_qualified = False
typehints_defaults = "braces-after"
typehints_document_rtype = True

autodoc_pydantic_model_show_json = False
autodoc_pydantic_settings_show_json = False
autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_model_signature_prefix = "schema"
autodoc_pydantic_field_doc_policy = "docstring"


def include_marked_members(_app, _what, _name, obj, skip, _options):
    doc = obj.__doc__
    if isinstance(doc, str) and ".. include in docs" in doc:
        return False
    return skip


def setup(app):
    app.connect("autodoc-skip-member", include_marked_members)
