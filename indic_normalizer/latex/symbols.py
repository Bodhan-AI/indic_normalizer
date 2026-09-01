"""Lookup tables for LaTeX-to-speech.

Pure-Python, English-only. All tables map a LaTeX command name (without the
leading backslash) to its spoken English rendering.
"""

from __future__ import annotations

# --------------------------------------------------------------------------
# Greek letters
# --------------------------------------------------------------------------
GREEK = {
    "alpha": "alpha",
    "beta": "beta",
    "gamma": "gamma",
    "delta": "delta",
    "epsilon": "epsilon",
    "varepsilon": "epsilon",
    "zeta": "zeta",
    "eta": "eta",
    "theta": "theta",
    "vartheta": "theta",
    "iota": "iota",
    "kappa": "kappa",
    "lambda": "lambda",
    "mu": "mu",
    "nu": "nu",
    "xi": "xi",
    "omicron": "omicron",
    "pi": "pi",
    "varpi": "pi",
    "rho": "rho",
    "varrho": "rho",
    "sigma": "sigma",
    "varsigma": "sigma",
    "tau": "tau",
    "upsilon": "upsilon",
    "phi": "phi",
    "varphi": "phi",
    "chi": "chi",
    "psi": "psi",
    "omega": "omega",
    # Capitals
    "Gamma": "capital gamma",
    "Delta": "capital delta",
    "Theta": "capital theta",
    "Lambda": "capital lambda",
    "Xi": "capital xi",
    "Pi": "capital pi",
    "Sigma": "capital sigma",
    "Upsilon": "capital upsilon",
    "Phi": "capital phi",
    "Psi": "capital psi",
    "Omega": "capital omega",
}

# --------------------------------------------------------------------------
# Relations
# --------------------------------------------------------------------------
RELATIONS = {
    "neq": "not equal to",
    "ne": "not equal to",
    "leq": "less than or equal to",
    "le": "less than or equal to",
    "geq": "greater than or equal to",
    "ge": "greater than or equal to",
    "ll": "much less than",
    "gg": "much greater than",
    "approx": "approximately",
    "approxeq": "approximately equal to",
    "simeq": "approximately equal to",
    "sim": "similar to",
    "cong": "congruent to",
    "equiv": "equivalent to",
    "propto": "proportional to",
    "in": "in",
    "notin": "not in",
    "ni": "contains",
    "subset": "subset of",
    "subseteq": "subset of or equal to",
    "supset": "superset of",
    "supseteq": "superset of or equal to",
    "cup": "union",
    "cap": "intersection",
    "perp": "perpendicular to",
    "parallel": "parallel to",
    "mid": "divides",
    "models": "models",
    "vdash": "proves",
    "doteq": "approaches the limit",
}

# --------------------------------------------------------------------------
# Binary operators
# --------------------------------------------------------------------------
OPERATORS = {
    "pm": "plus or minus",
    "mp": "minus or plus",
    "times": "times",
    "cdot": "times",
    "ast": "times",
    "div": "divided by",
    "setminus": "minus",
    "oplus": "circle plus",
    "otimes": "circle times",
    "odot": "circle dot",
    "wedge": "and",
    "vee": "or",
    "land": "and",
    "lor": "or",
    "star": "star",
    "bullet": "dot",
    "circ": "composed with",
    "cup": "union",
    "cap": "intersection",
}

# --------------------------------------------------------------------------
# Arrows
# --------------------------------------------------------------------------
ARROWS = {
    "to": "goes to",
    "rightarrow": "goes to",
    "longrightarrow": "goes to",
    "Rightarrow": "implies",
    "implies": "implies",
    "Longrightarrow": "implies",
    "leftarrow": "left arrow",
    "Leftarrow": "is implied by",
    "gets": "gets",
    "leftrightarrow": "if and only if",
    "Leftrightarrow": "if and only if",
    "iff": "if and only if",
    "mapsto": "maps to",
    "uparrow": "up arrow",
    "downarrow": "down arrow",
    "hookrightarrow": "maps into",
}

# --------------------------------------------------------------------------
# Miscellaneous symbols
# --------------------------------------------------------------------------
MISC = {
    "infty": "infinity",
    "partial": "partial",
    "nabla": "del",
    "forall": "for all",
    "exists": "there exists",
    "nexists": "there does not exist",
    "emptyset": "empty set",
    "varnothing": "empty set",
    "ell": "l",
    "hbar": "h bar",
    "Re": "real part",
    "Im": "imaginary part",
    "aleph": "aleph",
    "angle": "angle",
    "triangle": "triangle",
    "prime": "prime",
    "degree": "degrees",
    "neg": "not",
    "lnot": "not",
    "top": "top",
    "bot": "bottom",
    "cdots": "dot dot dot",
    "ldots": "dot dot dot",
    "dots": "dot dot dot",
    "vdots": "vertical dots",
    "ddots": "diagonal dots",
    "backslash": "backslash",
    "%": "percent",
    "&": "and",
    "#": "number",
    "$": "dollar",
    "{": "open brace",
    "}": "close brace",
}

# Symbols that can begin an operand (so functions may take them as arguments).
OPERAND_SYMS = {
    "infty",
    "partial",
    "nabla",
    "hbar",
    "ell",
    "emptyset",
    "varnothing",
    "aleph",
}

# --------------------------------------------------------------------------
# Named functions
# --------------------------------------------------------------------------
FUNCTIONS = {
    "sin": "sine",
    "cos": "cosine",
    "tan": "tangent",
    "cot": "cotangent",
    "sec": "secant",
    "csc": "cosecant",
    "sinh": "hyperbolic sine",
    "cosh": "hyperbolic cosine",
    "tanh": "hyperbolic tangent",
    "coth": "hyperbolic cotangent",
    "arcsin": "arc sine",
    "arccos": "arc cosine",
    "arctan": "arc tangent",
    "log": "log",
    "lg": "log",
    "ln": "natural log",
    "exp": "exp",
    "det": "determinant",
    "dim": "dimension",
    "ker": "kernel",
    "deg": "degree",
    "gcd": "gcd",
    "arg": "argument",
    "max": "maximum",
    "min": "minimum",
    "sup": "supremum",
    "inf": "infimum",
    "Pr": "probability",
}

# --------------------------------------------------------------------------
# Big operators (take optional lower/upper bounds and a body)
# --------------------------------------------------------------------------
BIGOPS = {
    "int": "integral",
    "iint": "double integral",
    "iiint": "triple integral",
    "oint": "contour integral",
    "sum": "sum",
    "prod": "product",
    "coprod": "coproduct",
    "bigcup": "union",
    "bigcap": "intersection",
    "bigoplus": "direct sum",
    "bigotimes": "tensor product",
    "bigvee": "logical or",
    "bigwedge": "logical and",
    "lim": "limit",
    "limsup": "limit superior",
    "liminf": "limit inferior",
}

# --------------------------------------------------------------------------
# Accents / decorations -> (spoken word, position)
#   position "pre"  => "vector v"
#   position "post" => "x hat"
# --------------------------------------------------------------------------
ACCENTS = {
    "vec": ("vector", "pre"),
    "overrightarrow": ("vector", "pre"),
    "overarrow": ("vector", "pre"),
    "hat": ("hat", "post"),
    "widehat": ("hat", "post"),
    "bar": ("bar", "post"),
    "overline": ("bar", "post"),
    "dot": ("dot", "post"),
    "ddot": ("double dot", "post"),
    "dddot": ("triple dot", "post"),
    "tilde": ("tilde", "post"),
    "widetilde": ("tilde", "post"),
    "check": ("check", "post"),
    "breve": ("breve", "post"),
    "acute": ("acute", "post"),
    "grave": ("grave", "post"),
    "mathring": ("ring", "post"),
    "underline": ("underlined", "post"),
}

# --------------------------------------------------------------------------
# Text-mode wrappers: read inner content verbatim
# --------------------------------------------------------------------------
TEXT_CMDS = {
    "text",
    "textrm",
    "textbf",
    "textit",
    "textsf",
    "texttt",
    "textnormal",
    "mathrm",
    "mathbf",
    "mathit",
    "mathsf",
    "mathtt",
    "mathcal",
    "mathbb",
    "mathfrak",
    "mathscr",
    "operatorname",
    "emph",
    "mbox",
    "hbox",
}

# --------------------------------------------------------------------------
# Spacing macros -> collapse to a single space (dropped in output)
# --------------------------------------------------------------------------
SPACING = {",", ";", ":", "!", " ", "quad", "qquad", "thinspace", "medspace",
           "thickspace", "enspace", "hspace", "vspace"}

# Fraction commands
FRAC_CMDS = {"frac", "dfrac", "tfrac", "cfrac"}


def _merge(*dicts):
    out = {}
    for d in dicts:
        out.update(d)
    return out


# Combined symbol table used for 0-argument command lookup.
SYMBOLS = _merge(GREEK, RELATIONS, OPERATORS, ARROWS, MISC)


def lookup_symbol(name):
    """Return the spoken form of a 0-arg command, or None if unknown."""
    return SYMBOLS.get(name)
