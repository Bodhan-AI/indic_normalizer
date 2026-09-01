"""Pre-handler text cleanup: artifact stripping, bracket/tag handling, and
script detection."""

from .artifacts import clean_controls, strip_escapes
from .brackets import protect_tags, restore_tags, strip_parentheses
from .scripts import char_script, dominant_script

__all__ = [
    "clean_controls",
    "strip_escapes",
    "protect_tags",
    "restore_tags",
    "strip_parentheses",
    "char_script",
    "dominant_script",
]
