# -*- coding: utf-8 -*-
"""Docstring-coverage ratchet: every public module / top-level function /
class (and public methods of public classes) in the API-documented modules
must carry a docstring. LaTeX parser/speaker/lexer internals and nested
closures are deliberately out of scope."""

import ast
import pathlib

import indic_normalizer

PKG = pathlib.Path(indic_normalizer.__file__).parent

MODULES = [
    "__init__.py",
    "normalizer.py",
    "config.py",
    "numerals.py",
    "numbers/__init__.py",
    "numbers/core.py",
    "lexicon/__init__.py",
    "lexicon/base.py",
    "lexicon/tables.py",
    "preprocess/__init__.py",
    "preprocess/artifacts.py",
    "preprocess/brackets.py",
    "preprocess/scripts.py",
    "classes/__init__.py",
    "classes/base.py",
    "classes/handlers.py",
    "latex/__init__.py",
    "latex/chemistry.py",
]


def _missing_in(relpath):
    tree = ast.parse((PKG / relpath).read_text())
    missing = []
    if not ast.get_docstring(tree):
        missing.append(f"{relpath}: <module>")
    for node in tree.body:  # top level only: nested closures are out of scope
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if node.name.startswith("_"):
                continue
            if not ast.get_docstring(node):
                missing.append(f"{relpath}: {node.name}")
            if isinstance(node, ast.ClassDef):
                for sub in node.body:
                    if (isinstance(sub, ast.FunctionDef)
                            and not sub.name.startswith("_")
                            and not ast.get_docstring(sub)):
                        missing.append(f"{relpath}: {node.name}.{sub.name}")
    return missing


def test_public_api_has_docstrings():
    missing = []
    for rel in MODULES:
        missing += _missing_in(rel)
    assert not missing, "public objects without docstrings:\n  " + "\n  ".join(missing)
