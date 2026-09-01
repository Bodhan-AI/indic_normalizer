# Sphinx configuration for indic_normalizer.
#
# Build:  sphinx-build -b html docs docs/_build/html

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "indic_normalizer"
author = "TTS Team"
copyright = "2026, TTS Team"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autodoc_member_order = "bysource"
# undoc-members is NOT global: it would double-document dataclass attributes
# already described in napoleon "Attributes:" sections (e.g. NormalizerConfig).
# The handlers module opts in explicitly in api.rst instead.
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
}
autosummary_generate = True

html_theme = "sphinx_rtd_theme"
html_static_path = []
templates_path = []
exclude_patterns = ["_build"]
