"""Walk an expression tree and produce spoken English."""

from __future__ import annotations

import re

from . import symbols as S
from .environments import speak_environment


# --------------------------------------------------------------------------
# Number -> words (self-contained; do NOT import the package number engine)
# --------------------------------------------------------------------------
_ONES = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen",
]
_TENS = [
    "", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
    "eighty", "ninety",
]
_ORD = {
    1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth",
    6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth",
    11: "eleventh", 12: "twelfth",
}
_DENOM = {
    2: "half", 3: "third", 4: "quarter", 5: "fifth", 6: "sixth",
    7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth",
}


def _below_hundred(n):
    if n < 20:
        return _ONES[n]
    t = _TENS[n // 10]
    r = n % 10
    return t + (" " + _ONES[r] if r else "")


def _below_thousand(n):
    if n < 100:
        return _below_hundred(n)
    h = _ONES[n // 100] + " hundred"
    r = n % 100
    return h + (" " + _below_hundred(r) if r else "")


def num_to_words(n):
    """Cardinal words for an integer 0..999,999; larger -> digit by digit."""
    n = int(n)
    if n < 0:
        return "minus " + num_to_words(-n)
    if n < 1000:
        return _below_thousand(n)
    if n < 1000000:
        th = n // 1000
        r = n % 1000
        return _below_thousand(th) + " thousand" + (
            " " + _below_thousand(r) if r else ""
        )
    return " ".join(_ONES[int(d)] for d in str(n))


def _speak_number_str(s):
    if "." in s:
        intp, frac = s.split(".", 1)
        left = num_to_words(int(intp)) if intp else "zero"
        digits = " ".join(_ONES[int(d)] for d in frac if d.isdigit())
        return left + " point " + digits
    if not s:
        return ""
    return num_to_words(int(s))


def ordinal(n):
    if n in _ORD:
        return _ORD[n]
    return num_to_words(n) + "th"


def _pluralize(word):
    if word == "half":
        return "halves"
    return word + "s"


# --------------------------------------------------------------------------
# Punctuation spoken forms
# --------------------------------------------------------------------------
_PUNCT = {
    "+": "plus",
    "-": "minus",
    "=": "equals",
    "<": "less than",
    ">": "greater than",
    "/": "over",
    "!": "factorial",
    ",": ",",
    ";": ";",
    ":": "",
    ".": "",
    "'": "prime",
    "*": "times",
}


def _collapse(s):
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s+([,;])", r"\1", s)
    return s.strip()


# --------------------------------------------------------------------------
# Speaker
# --------------------------------------------------------------------------
class Speaker:
    def __init__(self, verbosity="natural"):
        self.explicit = verbosity == "explicit"
        self.in_limit = False

    def numword(self, n):
        return num_to_words(n)

    # -- dispatch ---------------------------------------------------------
    def speak(self, node):
        if node is None:
            return ""
        method = getattr(self, "_s_" + node.kind, None)
        if method is None:
            return ""
        return method(node)

    def _s_seq(self, node):
        parts = [self.speak(it) for it in node.items]
        return _collapse(" ".join(p for p in parts if p))

    def _s_group(self, node):
        return self.speak(node.body)

    def _s_ident(self, node):
        return node.name

    def _s_num(self, node):
        return _speak_number_str(node.value)

    def _s_punct(self, node):
        v = node.value
        if v in _PUNCT:
            return _PUNCT[v]
        return v

    def _s_sym(self, node):
        name = node.name
        if self.in_limit and name in ("to", "rightarrow", "longrightarrow"):
            return "approaches"
        return S.lookup_symbol(name) or ""

    def _s_text(self, node):
        return node.value

    def _s_chem(self, node):
        from .chemistry import read_ce

        return read_ce(node.value)

    # -- fractions --------------------------------------------------------
    def _s_frac(self, node):
        num, den = node.num, node.den
        vulgar = self._vulgar_fraction(num, den)
        if vulgar is not None:
            return vulgar
        ns = self.speak(num)
        ds = self.speak(den)
        if self.explicit:
            if self._is_complex(num) or self._is_complex(den):
                return "the quantity " + ns + " over the quantity " + ds
            return "the fraction " + ns + " over " + ds
        return ns + " over " + ds

    def _vulgar_fraction(self, num, den):
        ni = _as_int(num)
        di = _as_int(den)
        if ni is None or di is None:
            return None
        if di not in _DENOM or ni < 1 or ni > 20:
            return None
        word = _DENOM[di]
        if ni != 1:
            word = _pluralize(word)
        return num_to_words(ni) + " " + word

    def _is_complex(self, node):
        return node is not None and node.kind == "seq" and len(node.items) > 1

    # -- roots ------------------------------------------------------------
    def _s_sqrt(self, node):
        arg = self.speak(node.arg)
        idx = node.index
        if idx is None:
            return "square root of " + arg
        k = _as_int(idx)
        if k == 2:
            return "square root of " + arg
        if k == 3:
            return "cube root of " + arg
        if k is not None:
            return ordinal(k) + " root of " + arg
        return self.speak(idx) + "-th root of " + arg

    # -- accents ----------------------------------------------------------
    def _s_accent(self, node):
        word, pos = S.ACCENTS[node.name]
        inner = self.speak(node.arg)
        if pos == "pre":
            return (word + " " + inner).strip()
        return (inner + " " + word).strip()

    # -- scripts ----------------------------------------------------------
    def _s_script(self, node):
        base = self.speak(node.base)
        return self._apply_scripts(base, node.sup, node.sub)

    def _apply_scripts(self, base_str, sup, sub):
        s = base_str
        if sub is not None:
            joiner = " subscript " if self.explicit else " sub "
            s = s + joiner + self.speak(sub)
        if sup is not None:
            s = self._apply_super(s, sup)
        return s.strip()

    def _apply_super(self, base_str, sup):
        if _is_degree(sup):
            return base_str + " degrees"
        if _is_named(sup, "prime"):
            return base_str + " prime"
        k = _as_int(sup)
        if not self.explicit and k == 2:
            return base_str + " squared"
        if not self.explicit and k == 3:
            return base_str + " cubed"
        joiner = " to the power of " if self.explicit else " to the "
        spoken = self.speak(sup)
        # A multi-term exponent ("e^{x+2}") is ambiguous when spoken flat:
        # the listener cannot tell where the exponent ends. Mark it.
        # (the natural joiner already ends in "the": "to the quantity ...")
        if _has_inner_pm(sup):
            spoken = ("the quantity " if self.explicit else "quantity ") + spoken
        return base_str + joiner + spoken

    # -- named functions --------------------------------------------------
    def _s_func(self, node):
        name = S.FUNCTIONS.get(node.name, node.name)
        s = name
        if node.sub is not None:
            s = s + " sub " + self.speak(node.sub)
        if node.power is not None:
            s = self._apply_super(s, node.power)
        if node.arg is not None:
            argtxt = self.speak(node.arg)
            if argtxt:
                s = s + " of " + argtxt
        return s

    # -- application f(x) -------------------------------------------------
    def _s_app(self, node):
        f = self.speak(node.func)
        inner = self.speak(node.arg.body) if node.arg is not None else ""
        return (f + " of " + inner).strip()

    # -- delimiters -------------------------------------------------------
    def _s_delim(self, node):
        inner = self.speak(node.body)
        left = node.left
        if left == "|":
            return "absolute value of " + inner
        if left == "||":
            return "norm of " + inner
        if left == "{":
            return ("the set " + inner).strip()
        if left == "<":
            return inner
        if self.explicit and left in ("(", "["):
            return ("the quantity " + inner).strip() if inner else ""
        return inner

    # -- big operators ----------------------------------------------------
    def _s_bigop(self, node):
        name = S.BIGOPS.get(node.name, node.name)
        body = self.speak(node.body) if getattr(node, "body", None) else ""

        if node.name in ("lim", "limsup", "liminf"):
            parts = [name]
            if node.lower is not None:
                prev = self.in_limit
                self.in_limit = True
                low = self.speak(node.lower)
                self.in_limit = prev
                if low:
                    parts.append("as " + low)
            if body:
                parts.append("of " + body)
            return " ".join(parts)

        parts = [name]
        if node.lower is not None and node.upper is None:
            # Subscript-only: a region/index, not a range ("\iint_S" -> "over
            # S", "\oint_C" -> "around C", "\sum_j" -> "over j").
            low = self.speak(node.lower)
            if low:
                prep = "around" if "oint" in node.name else "over"
                parts.append(prep + " " + low)
        elif node.lower is not None:
            low = self.speak(node.lower)
            if low:
                parts.append("from " + low)
        if node.upper is not None:
            up = self.speak(node.upper)
            if up:
                parts.append("to " + up)
        if body:
            parts.append("of " + body)
        return " ".join(parts)

    # -- environments -----------------------------------------------------
    def _s_env(self, node):
        return speak_environment(node, self)


# --------------------------------------------------------------------------
# Node inspection helpers
# --------------------------------------------------------------------------
def _unwrap(node):
    """Peel single-element groups/seqs to their inner node."""
    while node is not None and node.kind in ("group", "seq"):
        items = node.body.items if node.kind == "group" else node.items
        if len(items) != 1:
            return node
        node = items[0]
    return node


def _as_int(node):
    node = _unwrap(node)
    if node is None:
        return None
    if node.kind == "num" and "." not in node.value:
        try:
            return int(node.value)
        except ValueError:
            return None
    return None


def _is_named(node, name):
    node = _unwrap(node)
    return node is not None and node.kind == "sym" and node.name == name


def _is_degree(node):
    node = _unwrap(node)
    return node is not None and node.kind == "sym" and node.name in ("circ", "degree")


def _has_inner_pm(node):
    """True if the node is a sequence with a top-level +/- after the first
    item — a multi-term expression whose spoken end would be ambiguous."""
    while node is not None and node.kind == "group":
        node = node.body
    if node is None or node.kind != "seq":
        return False
    return any(
        i > 0 and it.kind == "punct" and it.value in "+-"
        for i, it in enumerate(node.items)
    )


def speak_tree(tree, verbosity="natural"):
    return Speaker(verbosity).speak(tree)
