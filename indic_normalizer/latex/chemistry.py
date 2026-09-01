"""Chemistry: mhchem \\ce{...} rendering plus a bare-formula heuristic.

Element symbols are read letter-by-letter (uppercase letters spoken as the
letter), digit counts as English cardinals, per the approved examples::

    \\ce{H2O}            -> "H two O"
    \\ce{2H2 + O2 -> 2H2O} -> "two H two plus O two yields two H two O"
    \\ce{SO4^2-}         -> "S O four two minus"
"""

from __future__ import annotations

import re


def _cardinal(n):
    # Local import avoids a circular dependency at module load time.
    from .speak import num_to_words

    return num_to_words(int(n))


_STATES = {
    "s": "solid",
    "l": "liquid",
    "g": "gas",
    "aq": "aqueous",
}


def _speak_chem(s):
    """Core reader shared by ce{} spans and bare formulas."""
    out = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]

        if c.isspace():
            i += 1
            continue

        # Digit run -> cardinal (coefficient or count)
        if c.isdigit():
            j = i
            while j < n and s[j].isdigit():
                j += 1
            out.append(_cardinal(s[i:j]))
            i = j
            continue

        # Reaction arrows and equilibrium
        if s.startswith("<=>", i) or s.startswith("<->", i):
            out.append("in equilibrium with")
            i += 3
            continue
        if s.startswith("->", i) or s.startswith("\\rightarrow", i):
            out.append("yields")
            i += 2 if s.startswith("->", i) else len("\\rightarrow")
            continue
        if s.startswith("<-", i):
            out.append("is produced from")
            i += 2
            continue

        if c == "+":
            out.append("plus")
            i += 1
            continue

        # Bond "=" or "#": ignore (double / triple bonds)
        if c in "=#":
            i += 1
            continue

        # Charge / superscript
        if c == "^":
            i += 1
            j = i
            while j < n and (s[j].isdigit() or s[j] in "+-"):
                j += 1
            token = s[i:j]
            out.append(_speak_charge(token))
            i = j if j > i else i + 1
            continue

        # Subscript marker _2 -> count
        if c == "_":
            i += 1
            continue

        # Parenthesised state or group
        if c == "(":
            close = s.find(")", i)
            if close != -1:
                inner = s[i + 1:close].strip().lower()
                if inner in _STATES:
                    out.append(_STATES[inner])
                    i = close + 1
                    # optional following count handled by main loop
                    continue
                # Ordinary group: read its contents inline
                out.append(_speak_chem(s[i + 1:close]))
                i = close + 1
                continue
            i += 1
            continue
        if c == ")":
            i += 1
            continue

        # A run of letters -> spell out each letter
        if c.isalpha():
            j = i
            while j < n and s[j].isalpha():
                j += 1
            for ch in s[i:j]:
                out.append(ch)
            i = j
            continue

        # Standalone + / - charge
        if c == "-":
            out.append("minus")
            i += 1
            continue

        # Anything else: skip
        i += 1

    text = " ".join(t for t in out if t)
    return re.sub(r"\s+", " ", text).strip()


def _speak_charge(token):
    """Render a charge token like '2-' or '+' or '3+'."""
    m = re.match(r"^(\d*)([+-]?)$", token)
    if not m:
        return token
    digits, sign = m.group(1), m.group(2)
    parts = []
    if digits:
        parts.append(_cardinal(digits))
    if sign == "+":
        parts.append("plus")
    elif sign == "-":
        parts.append("minus")
    return " ".join(parts)


def read_ce(inner):
    """Read the contents of a \\ce{...} span."""
    try:
        return _speak_chem(inner)
    except Exception:
        return re.sub(r"[^A-Za-z0-9 ]", " ", inner).strip()


# --------------------------------------------------------------------------
# Bare-formula heuristic
# --------------------------------------------------------------------------
_FORMULA_RE = re.compile(r"^([A-Z][a-z]?\d*)+$")


def looks_like_formula(token):
    """Return True if ``token`` looks like a chemical formula.

    Guards against firing on ordinary words / all-caps acronyms (NASA, IPL):
    requires either a digit or at least two element groups with a lowercase
    letter present.
    """
    if not token or not _FORMULA_RE.match(token):
        return False
    groups = re.findall(r"[A-Z][a-z]?\d*", token)
    has_digit = any(ch.isdigit() for ch in token)
    has_lower = any(ch.islower() for ch in token)
    if has_digit:
        return True
    # No digits: only accept multi-element formulas containing a lowercase
    # letter (e.g. NaCl), never all-caps acronyms.
    return len(groups) >= 2 and has_lower


def read_formula(token):
    """Read a bare chemical formula token (e.g. ``H2O``)."""
    return _speak_chem(token)
