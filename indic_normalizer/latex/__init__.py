"""Pure-Python, English-only LaTeX-to-speech engine.

Public API
----------
    latex_to_speech(expr, verbosity="natural") -> str
    convert_spans(text, verbosity="natural") -> str
    LATEX_SPAN_PATTERN  (compiled re.Pattern)
"""

from __future__ import annotations

import re

from .parser import parse
from .speak import Speaker
from . import chemistry

__all__ = [
    "latex_to_speech",
    "convert_spans",
    "LATEX_SPAN_PATTERN",
]

def _strip_fallback(expr):
    """Best-effort degraded reading when parsing fails."""
    from .speak import _speak_number_str

    # Drop backslash commands, keep their names dropped entirely.
    s = re.sub(r"\\[A-Za-z]+", " ", expr)
    s = re.sub(r"[{}$^_&\\]", " ", s)
    out = []
    for tok in re.findall(r"\d+\.\d+|\d+|[A-Za-z]+|[+\-=<>]", s):
        if tok[0].isdigit():
            out.append(_speak_number_str(tok))
        elif tok in ("+", "-", "=", "<", ">"):
            out.append(
                {"+": "plus", "-": "minus", "=": "equals",
                 "<": "less than", ">": "greater than"}[tok]
            )
        else:
            out.append(tok)
    return re.sub(r"\s+", " ", " ".join(out)).strip()


def latex_to_speech(expr, verbosity="natural"):
    """Convert raw LaTeX (without delimiters) to spoken English.

    Never raises: on failure, degrades to a stripped reading.
    """
    if expr is None:
        return ""
    try:
        tree = parse(expr)
        out = Speaker(verbosity).speak(tree)
        out = _scrub_markup(out)
        if out:
            return out
        return _scrub_markup(_strip_fallback(expr))
    except Exception:
        try:
            return _scrub_markup(_strip_fallback(expr))
        except Exception:
            return ""


def _scrub_markup(out):
    """Spoken output must never leak LaTeX markup, whatever the parser did.
    Also collapses stacked grouping markers from adjacent constructs."""
    out = re.sub(r"[\\{}$^_~&]", " ", out)
    out = re.sub(r"\s+", " ", out).strip()
    return re.sub(r"\b(the quantity)( the quantity)+\b", r"\1", out)


# --------------------------------------------------------------------------
# Span detection in mixed text
# --------------------------------------------------------------------------
# Group numbering (fixed across the whole alternation):
#   1: env name        2: env body
#   3: $$...$$
#   4: \[...\]
#   5: \(...\)
#   6: \ce{...}
#   7: $...$
LATEX_SPAN_PATTERN = re.compile(
    r"\\begin\{([A-Za-z*]+)\}(.*?)\\end\{\1\}"      # 1,2
    r"|\$\$(.+?)\$\$"                                 # 3
    r"|\\\[(.+?)\\\]"                                 # 4
    r"|\\\((.+?)\\\)"                                 # 5
    r"|\\ce\{([^{}]*)\}"                              # 6
    r"|\$(?![\d\s])(.+?)\$",                          # 7
    re.DOTALL,
)

# A bare $...$ span is math only if its content looks mathy; otherwise the $
# is almost certainly currency (or a shell variable) and the span must be left
# for the later semiotic-class handlers. The span pattern above already
# refuses to OPEN at "$<digit>"; this gates what it still captures.
_MATHY = re.compile(r"[\\^_={}]")


def _is_math_content(s):
    if _MATHY.search(s):
        return True
    # short spaceless expressions with a letter variable: $n$, $x+y$, $a/b$
    return " " not in s and len(s) <= 20 and re.search(r"[A-Za-z]", s) is not None


def convert_spans(text, verbosity="natural"):
    """Replace every LaTeX span in ``text`` with its spoken reading.

    Each span becomes ``" <spoken> "`` (space-padded). Non-LaTeX text is
    untouched. Never raises.
    """
    if text is None:
        return ""

    def _repl(m):
        try:
            if m.group(1) is not None:  # environment
                spoken = latex_to_speech(m.group(0), verbosity)
            elif m.group(3) is not None:  # $$...$$
                spoken = latex_to_speech(m.group(3), verbosity)
            elif m.group(4) is not None:  # \[...\]
                spoken = latex_to_speech(m.group(4), verbosity)
            elif m.group(5) is not None:  # \(...\)
                spoken = latex_to_speech(m.group(5), verbosity)
            elif m.group(6) is not None:  # \ce{...}
                spoken = chemistry.read_ce(m.group(6))
            elif m.group(7) is not None:  # $...$
                if not _is_math_content(m.group(7)):
                    return m.group(0)  # currency / prose: leave untouched
                spoken = latex_to_speech(m.group(7), verbosity)
            else:
                spoken = latex_to_speech(m.group(0), verbosity)
        except Exception:
            spoken = _strip_fallback(m.group(0))
        return " " + spoken + " "

    try:
        return LATEX_SPAN_PATTERN.sub(_repl, text)
    except Exception:
        return text
