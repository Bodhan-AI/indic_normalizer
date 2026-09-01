# indic_normalizer

A **lightweight, pure-Python** text normalizer designed as a **pre-step before TTS**
for the **22 scheduled languages of India** (+ English). It turns raw, messy text
into clean spoken-form words: numbers, dates, currency, measures, LaTeX math, and
more — while stripping artifacts that hurt synthesis.

- **Zero runtime dependencies** (standard library only). No `pynini`, no models.
- **All 22 scheduled languages + English** for number reading.
- **Context-aware**: `1947` → *nineteen forty seven* (year) vs `1,947` / `1947 kg`
  → *one thousand nine hundred and forty seven* (cardinal).
- **Script-aware language resolution** (see below).
- **From-scratch LaTeX-to-speech** for math / physics / chemistry (English).
- **Artifact stripping** with tag preservation for TTS markup.

## Install

```bash
pip install -e .        # from the repo root
```

## Quick start

```python
from indic_normalizer import Normalizer, normalize

normalize("India became independent in 1947.", lang="en")
# 'India became independent in nineteen forty seven.'

normalize("भारत 1947 में स्वतंत्र हुआ।", lang="hi")
# 'भारत nineteen forty seven में स्वतंत्र हुआ।'   (ASCII digits -> English)

normalize("यह १९४७ की बात है।", lang="hi")
# 'यह एक हज़ार नौ सौ सैंतालीस की बात है।'          (native digits -> Hindi)

normalize("1947", lang="hi", number_lang="hi")
# 'एक हज़ार नौ सौ सैंतालीस'                          (forced language)
```

## How numbers pick their language

Unless a language is forced, numbers are spoken in **English by default**, because
Indian TTS commonly reads Arabic numerals in English even inside regional text.

1. **Forced** — `number_lang="ta"` (or `force=True`, i.e. use `lang`): every number
   is read in that language.
2. **Native-script digits** (`१९४७`, `১৯৪৭`, …) → read in the **sentence language** (`lang`).
3. **Native-script scale word** — an ASCII number followed by a native scale word
   is treated like native digits: `2 करोड़ लोग` → `दो करोड़ लोग`.
4. **Native ordinal suffix** — `5वाँ` speaks the sentence language (`पाँचवाँ`),
   since the suffix itself proves it.
5. **ASCII digits** (`0-9`) otherwise → read in **English** (`default_number_lang`).

## What it normalizes

| Class | Example (en) | Output |
|---|---|---|
| Year (context) | `in 1947` | `nineteen forty seven` |
| Cardinal | `1,947` / `1947 kg` | `one thousand nine hundred and forty seven …` |
| Leading zeros | `agent 007`, `0091` | `zero zero seven`, `zero zero nine one` (digit-wise) |
| Decimal | `3.14` | `three point one four` |
| Signed values | `-5°C`, `+42`, `−42` | `minus five degrees celsius`, `plus forty two`, … |
| Currency | `₹1,234.50` / `₹1` / `₹0.50` | `… rupees and fifty paise` / `one rupee` / `fifty paise` |
| Currency scales | `₹5 lakh`, `$1.5 billion` | `five lakh rupees`, `one point five billion dollars` |
| Suffix currency | `100₹`, `250 rs` | `one hundred rupees`, `two hundred and fifty rupees` |
| Percent | `12.5%` | `twelve point five percent` |
| Measure | `37.5°C`, `5000 mAh`, `2.4 GHz`, `3000 rpm` | `… degrees celsius`, `… milliamp hours`, `… gigahertz`, `… revolutions per minute` |
| Range | `1939-1945`, `pages 10-15`, `10-15%`, `5-10 kg` | `nineteen thirty nine to nineteen forty five`, `ten to fifteen …` |
| Ratio / score | `won 3:2`, `16:9` | `three to two`, `sixteen to nine` |
| Date (numeric) | `15/08/1947`, `2024-03-05`, `15.8.1947`, `08/15/1947` | `fifteenth August nineteen forty seven` (US order auto-detected) |
| Date (textual) | `15 August 1947`, `Aug 15, 1947`, `5 June` | `fifteenth August nineteen forty seven`, `August fifteenth …`, `fifth June` |
| Decade | `the 1990s`, `the 90s` | `the nineteen nineties`, `the nineties` |
| Time | `10:30 am`, `18:45` | `ten thirty am`, `eighteen forty five` |
| Phone | `+91 98765 43210`, `011-2345-6789` | `plus nine one nine eight …` (digit-by-digit, shape-gated) |
| Indian IDs | `PAN ABCDE1234F`, `SBIN0001234`, `KA 01 AB 1234`, `PIN 560001` | spelled letter-by-letter, digits digit-wise |
| Email / URL | `test123@gmail.com`, `www.example.com/page2` | `test one two three at gmail dot com`, `w w w dot example dot com slash page two` |
| Version / IP | `Python 3.11.4`, `192.168.1.1` | `three point eleven point four`, `one nine two dot one six eight dot one dot one` |
| Scientific | `1.5e10` | `one point five times ten to the power ten` |
| Ordinal | `21st`, `5वाँ`, `2ਵਾਂ` | `twenty first`, `पाँचवाँ`, `ਦੂਜਾ` |
| Fraction | `3/4` | `three quarters` |
| Blood pressure | `BP 120/80`, `140/90 mmHg` | `one hundred and twenty over eighty (millimeters of mercury)` |
| Cricket score | `287/5 in 50 overs` | `two hundred and eighty seven for five …` (context-gated) |
| Abbreviations | `Dr. Rao`, `Pvt. Ltd.`, `etc.`, `vs.`, `No. 5`, `Main St.` | `Doctor Rao`, `Private Limited`, `et cetera`, `versus`, `Number five`, `Main Street` |
| Acronyms | `U.S.A.`, `A.P.J. Kalam` | `U S A`, `A P J Kalam` |
| Roman (context) | `Chapter IV`, `Class X`, `World War II` | `Chapter four`, `Class ten`, `World War two` (always on) |
| Alphanumeric | `COVID19`, `5G`, `seat 32A` | `COVID nineteen`, `five G`, `seat thirty two A` (Latin kept as-is) |
| Codes | `AB123CD`, `6E204` | `A B one two three C D`, `six E two zero four` (≥2 letter/digit transitions) |
| Position numbers | `room 225`, `flight 6204` | `room two twenty five`, `flight sixty two oh four` (after room/page/flight/gate/bus) |
| Symbols | `2 + 2 = 4`, `5 < 10`, `A & B`, `@` | `plus / equals / less than / and / at` (standalone only) |
| LaTeX | `$x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}$` | `x equals minus b plus or minus square root of b squared minus four a c over two a` |
| Chemistry | `\ce{2H2 + O2 -> 2H2O}` | `two H two plus O two yields two H two O` |

A bare `$…$` span is only treated as math when its content looks mathy —
`I paid $5 and she paid $10` reads as two dollar amounts, never as LaTeX.

### Handler pipeline

Handlers run in a fixed priority order (specific → general); each rewrites its
spans into words, so later handlers never re-match them:

`web → abbrev → time → ratio → date → textdate → money → range → percent →
ids → bp → measure → native_scale → scientific → code → decade → ordinal →
alphanumeric → phone → dotted → cricket → fraction → decimal → position →
number → symbol → roman_ctx → roman (opt-in)`

See `indic_normalizer/classes/__init__.py` for the registry and
`classes/handlers.py` for each handler.

### Artifacts & tags

- Escape sequences (`\n`, `\t`, `\uXXXX`) and control/zero-width chars are stripped;
  Unicode minus (`−`) is normalized to `-`, and output is always NFC-normalized
  (so `normalize` is idempotent).
- **`(...)` parentheticals are removed** (balanced pairs only — an unmatched `(`
  can never swallow the rest of the utterance).
- **`[...]` and tag-shaped `<...>` are preserved verbatim** — they are SSML /
  prosody markers (`[emphasis]`, `<break/>`). Bare comparisons (`5 < 10`) are
  NOT treated as tags and read as `five less than ten`.

## LaTeX-to-speech (standalone)

```python
from indic_normalizer import latex_to_speech
latex_to_speech(r"\int_0^1 x^2\,dx")            # 'integral from zero to one of x squared d x'
latex_to_speech(r"\frac{a}{b}", verbosity="explicit")  # 'the fraction a over b'
```

Auto-detected inside mixed text for the delimiters `$…$`, `$$…$$`, `\(…\)`,
`\[…\]`, `\begin{env}…\end{env}`, and `\ce{…}`.

## Configuration

`Normalizer(lang=..., **opts)` / `normalize(text, lang=..., **opts)` accept:

| Option | Default | Meaning |
|---|---|---|
| `lang` | `"en"` | sentence/regional language (drives lexicon + native-digit reading) |
| `number_lang` | `None` | force numbers into this language |
| `force` | `False` | shorthand: force numbers into `lang` |
| `default_number_lang` | `"en"` | language for ASCII digits when not forced |
| `strip_parentheses` | `True` | remove `(...)` |
| `keep_square_brackets` / `keep_angle_brackets` | `True` | preserve `[...]` / `<...>` |
| `strip_escapes` | `True` | strip escape-sequence artifacts |
| `latex` | `True` | convert LaTeX spans |
| `latex_verbosity` | `"natural"` | `"natural"` or `"explicit"` |
| `detect_years` | `True` | enable year-style reading |
| `detect_positions` | `True` | pairing style after room/page/flight/gate/bus (`room 225` → `two twenty five`) |
| `year_range` | `(1100, 2099)` | candidate year range |
| `detect_roman` | `False` | convert *bare* roman numerals everywhere (opt-in; risky). Context-gated romans (`Chapter IV`, `Class X`) are always on. |

## Languages

`as bn brx doi en gu hi kn ks kok mai ml mni mr ne or pa sa sat sd ta te ur`

Cardinals work for all of them via the vendored engine. The extra **glue-word
lexicon** (decimal point, percent, currency, months, ordinals, range/"and"
connectors) is populated for English, Hindi, and the other major scripts —
Gregorian month names ship for 19 languages, suffix ordinals for 10 (Dravidian
ordinals are deliberately left out: they need stem sandhi, not concatenation).
Best-effort or missing entries are flagged for native review:

```python
from indic_normalizer.lexicon import list_review_flags
list_review_flags()   # ['as: months', 'brx: currency', ...]
```

See [`data/review/REVIEW.md`](data/review/REVIEW.md). Contributions of verified
native wording are welcome.

> Note: Sindhi (`sd`) has upstream gaps in the number engine for some values;
> those fall back to a digit-by-digit reading rather than failing.

## API documentation

Sphinx autodocs (autodoc + napoleon + viewcode, RTD theme):

```bash
pip install sphinx sphinx_rtd_theme      # docs-only dependencies
sphinx-build -b html docs docs/_build/html
# open docs/_build/html/index.html
```

`docs/index.rst` carries the overview and handler pipeline; `docs/api.rst`
pulls the API reference straight from the module docstrings.

## Tests

```bash
python -m pytest -q      # 535 tests: per-handler suites, a 126-pin golden
                         # corpus (each pin also idempotency-checked), and
                         # deterministic fuzz nets (pipeline + LaTeX)
python examples/demo.py  # showcase
```

## Credits & license

MIT-licensed. Built from scratch, but **borrowing** (not depending on):

- Number-word tables & cardinal logic vendored from
  [AI4Bharat/indic-numtowords](https://github.com/AI4Bharat/indic-numtowords) (MIT).
- Semiotic-class taxonomy inspired by
  [Kenpath/indic-text-normalization](https://github.com/Kenpath/indic-text-normalization) (Apache-2.0).

See [`NOTICE`](NOTICE) for details.
