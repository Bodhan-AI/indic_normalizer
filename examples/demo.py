"""Demo showcase for indic_normalizer.

Run:  python examples/demo.py
"""

from indic_normalizer import normalize, latex_to_speech


CASES = [
    # (label, text, kwargs)
    ("year vs cardinal (en)", "India became independent in 1947.", dict(lang="en")),
    ("cardinal (comma)", "A crowd of 1,947 gathered.", dict(lang="en")),
    ("cardinal (unit)", "The rover travelled 1947 km.", dict(lang="en")),
    ("modern year", "Released in the year 2024.", dict(lang="en")),
    ("ASCII digits in Hindi -> English", "भारत 1947 में स्वतंत्र हुआ।", dict(lang="hi")),
    ("native digits -> regional", "यह १९४७ की बात है।", dict(lang="hi")),
    ("forced language", "Chapter 1947", dict(lang="hi", number_lang="hi")),
    ("currency", "It costs ₹1,234.50 only.", dict(lang="en")),
    ("percent + decimal", "Inflation rose 12.5% last month.", dict(lang="en")),
    ("time + date", "Meet at 10:30 am on 15/08/1947.", dict(lang="en")),
    ("phone -> digits", "Call +91 98765 43210 now.", dict(lang="en")),
    ("ordinals", "She finished 21st, he came 3rd.", dict(lang="en")),
    ("code-mixed alnum", "COVID19 spread; 5G rollout; buy MP3 files.", dict(lang="en")),
    ("artifacts + tags", "Keep [emphasis] and <break/> (drop this note).", dict(lang="en")),
    ("escape sequences", "First line\\nSecond line\\tindented.", dict(lang="en")),
    ("latex inline", "The root is $x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$.", dict(lang="en")),
    ("latex chemistry (in Hindi)", "अभिक्रिया: \\ce{2H2 + O2 -> 2H2O}", dict(lang="hi")),
]


def main():
    print("=" * 72)
    print("indic_normalizer — TTS pre-normalization demo")
    print("=" * 72)
    for label, text, kw in CASES:
        print(f"\n[{label}]  ({', '.join(f'{k}={v}' for k, v in kw.items())})")
        print(f"  in : {text}")
        print(f"  out: {normalize(text, **kw)}")

    print("\n" + "-" * 72)
    print("LaTeX standalone (natural vs explicit):")
    for expr in [r"\frac{1}{2}", r"\int_0^1 x^2\,dx", r"\sum_{i=1}^{n} i", r"\sqrt[3]{8}"]:
        print(f"  {expr}")
        print(f"    natural : {latex_to_speech(expr)}")
        print(f"    explicit: {latex_to_speech(expr, verbosity='explicit')}")


if __name__ == "__main__":
    main()
