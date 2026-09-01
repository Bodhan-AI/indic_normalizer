# -*- coding: utf-8 -*-
"""Deterministic fuzz nets: the pipeline must never raise, and the LaTeX
engine must never leak markup into spoken output (backlog batch)."""

import random

from indic_normalizer import normalize, latex_to_speech


def test_latex_fuzz_never_raises_or_leaks_markup():
    rng = random.Random(42)
    pool = [
        "\\frac", "{", "}", "$", "^", "_", "\\sqrt", "x", "1", "+", "-",
        "\\alpha", " ", "\\begin{matrix}", "\\end{matrix}", "2", "=",
        "\\int", "e", "\\", "&", "\\ce", "\\left(", "\\right)", "\\,",
        "\\text{ok}", "%", "~", "\\\\", "\\lim_", "^{", "_{",
    ]
    for _ in range(300):
        expr = "".join(rng.choice(pool) for _ in range(rng.randint(1, 40)))
        out = latex_to_speech(expr)
        assert isinstance(out, str)
        for ch in "\\{}$^_":
            assert ch not in out, f"markup {ch!r} leaked for {expr!r}: {out!r}"


def test_normalize_fuzz_never_raises():
    rng = random.Random(7)
    pool = list("abz ABZ019०९.,$₹%/-:()[]<>@&+=\\#!?'\"॥ ") + [
        "१९४७", "$x$", "12:30", "e.g.", "\\n", "kg", "rs", "lakh", "करोड़",
        "www.", ".com", "Dr.", "IV", "\ue100", "\u200d", "−", "🙂",
    ]
    for _ in range(300):
        s = "".join(rng.choice(pool) for _ in range(rng.randint(0, 60)))
        out = normalize(s)
        assert isinstance(out, str)


def test_normalize_fuzz_hindi_never_raises():
    rng = random.Random(13)
    pool = list("क़ख हिन्दी ०१९ ₹%.-/:] [<>") + ["१२३", "लाख", "वाँ", "12", "am"]
    for _ in range(200):
        s = "".join(rng.choice(pool) for _ in range(rng.randint(0, 40)))
        out = normalize(s, lang="hi")
        assert isinstance(out, str)
