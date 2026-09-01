"""Tokenizer for LaTeX math source.

Produces a flat list of ``Token`` objects. Never raises on malformed input;
unknown constructs simply become CHAR or COMMAND tokens.
"""

from __future__ import annotations


class Token:
    __slots__ = ("type", "value", "raw")

    def __init__(self, type_, value=None, raw=None):
        self.type = type_
        self.value = value
        self.raw = raw if raw is not None else (value if value is not None else "")

    def __repr__(self):  # pragma: no cover - debug helper
        return "Token(%s, %r)" % (self.type, self.value)


_SINGLE = {
    "{": "LBRACE",
    "}": "RBRACE",
    "^": "CARET",
    "_": "UNDERSCORE",
    "&": "AMP",
    "(": "LPAREN",
    ")": "RPAREN",
    "[": "LBRACK",
    "]": "RBRACK",
}


def _is_letter(c):
    return ("a" <= c <= "z") or ("A" <= c <= "Z")


def tokenize(s):
    """Tokenize a LaTeX source string into a list of Token objects."""
    toks = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]

        # Comment: skip to end of line
        if c == "%":
            j = i + 1
            while j < n and s[j] != "\n":
                j += 1
            i = j
            continue

        # Backslash-initiated command
        if c == "\\":
            # Line break \\
            if i + 1 < n and s[i + 1] == "\\":
                toks.append(Token("DBACKSLASH", "\\\\", "\\\\"))
                i += 2
                continue
            # Named command \abc
            if i + 1 < n and _is_letter(s[i + 1]):
                j = i + 1
                while j < n and _is_letter(s[j]):
                    j += 1
                name = s[i + 1:j]
                toks.append(Token("COMMAND", name, "\\" + name))
                i = j
                continue
            # Single-char command \, \{ \} \| \! \; \: \  etc.
            if i + 1 < n:
                ch = s[i + 1]
                toks.append(Token("COMMAND", ch, "\\" + ch))
                i += 2
                continue
            # Trailing lone backslash
            toks.append(Token("CHAR", "\\", "\\"))
            i += 1
            continue

        # Whitespace collapses to a single SPACE token
        if c.isspace():
            j = i
            while j < n and s[j].isspace():
                j += 1
            toks.append(Token("SPACE", " ", s[i:j]))
            i = j
            continue

        # Structural single characters
        if c in _SINGLE:
            toks.append(Token(_SINGLE[c], c, c))
            i += 1
            continue

        # Everything else -> CHAR
        toks.append(Token("CHAR", c, c))
        i += 1

    return toks
