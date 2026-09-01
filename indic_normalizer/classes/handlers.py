"""Semiotic-class handlers (regex tagger -> verbalizer), in priority order."""

from __future__ import annotations

import re

from .base import Context
from ..lexicon import get_lexicon
from ..numerals import to_ascii_digits
from .. import numbers as N


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _clean_int(s: str) -> str:
    return re.sub(r"[^0-9]", "", to_ascii_digits(s))


def _has_native(s: str) -> bool:
    from ..numerals import digits_are_native
    return digits_are_native(s)


def _signed(spoken: str, sign: str, lex) -> str:
    """Prefix a spoken number with its sign word ('-' -> negative, '+' -> plus)."""
    if sign == "-":
        return f"{lex.negative} {spoken}"
    if sign == "+":
        return f"{lex.symbols.get('+', 'plus')} {spoken}"
    return spoken


def _read_int_digits(digits: str, lang: str, lex, cfg, allow_year: bool = True) -> str:
    """Read an ASCII digit string: year-style when plausible, else cardinal.

    A leading zero ("007", "0091") signals a code, not a quantity: digit-wise.
    """
    if digits.startswith("0") and len(digits) > 1:
        return N.split_digits(digits, lang)
    value = int(digits)
    if (
        allow_year
        and cfg.detect_years
        and len(digits) == 4
        and cfg.year_range[0] <= value <= cfg.year_range[1]
    ):
        return N.year(value, lang, lex)
    return N.cardinal(digits, lang)


# ---------------------------------------------------------------------------
# 0. web: emails and URLs, spoken token-by-token ("at", "dot", "slash",
#    digits digit-wise). Runs first so no other handler can mangle them.
#    The protocol prefix (https://) is dropped: nobody reads it aloud.
# ---------------------------------------------------------------------------
_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")
_URL = re.compile(
    r"(?:https?://|www\.)\S+"
    r"|\b[\w-]+(?:\.[\w-]+)*\.(?:com|org|net|in|gov|edu|io|ai|co)\b(?:/\S*)?",
    re.I,
)
_WEB_CHARS = {
    ".": "dot", "/": "slash", "@": "at", "-": "dash", "_": "underscore",
    "?": "question mark", "=": "equals", "&": "and", "#": "hash",
    "+": "plus", ":": "colon", "%": "percent", "~": "tilde",
}
_WEB_TRAIL = ".,;:!?)]}\"'"


def _speak_web(tok: str, lang: str) -> str:
    tok = re.sub(r"^https?://", "", tok, flags=re.I)
    out = []
    for run in re.findall(r"\d+|[^\W\d_]+|.", tok):
        if run.isdigit():
            out.append(N.split_digits(run, lang))
        elif run.lower() == "www":
            out.append("w w w")
        else:
            out.append(_WEB_CHARS.get(run, run))
    return " ".join(out)


def _web_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        tok = m.group(0)
        trail = ""
        while tok and tok[-1] in _WEB_TRAIL:  # sentence punctuation, not URL
            trail = tok[-1] + trail
            tok = tok[:-1]
        lang, _lex = ctx.resolve(tok)
        return " " + _speak_web(tok, lang) + trail + " "
    return repl


def web_(text: str, ctx: Context) -> str:
    """Speak emails and URLs token-by-token ("at", "dot", "slash", digits
    digit-wise); the ``https://`` prefix is dropped."""
    repl = _web_repl(ctx)
    text = _EMAIL.sub(repl, text)
    text = _URL.sub(repl, text)
    return text


# ---------------------------------------------------------------------------
# 0b. abbreviations & titles (case-sensitive: "Dr." is a title, "dr." a path),
#     then dotted acronyms ("U.S.A." -> "U S A"). The abbreviation dot is
#     consumed; a sentence-final abbreviation loses its period (known ceiling).
# ---------------------------------------------------------------------------
_ABBREV = {
    "Dr.": "Doctor", "Mr.": "Mister", "Mrs.": "Missus", "Ms.": "Miz",
    "Prof.": "Professor",
    "Jr.": "Junior", "Sr.": "Senior",
    "Pvt.": "Private", "Ltd.": "Limited", "Govt.": "Government",
    "Dept.": "Department", "approx.": "approximately",
    "etc.": "et cetera", "e.g.": "for example", "i.e.": "that is",
    "vs.": "versus", "vs": "versus",
    "डॉ.": "डॉक्टर",
}
_ABBREV_RE = re.compile(
    r"(?<![\w.])(" + "|".join(re.escape(k) for k in sorted(_ABBREV, key=len, reverse=True)) + r")(?![\w.])"
)
# "No." means "Number" only right before a digit; "St." is Saint before a
# capitalized word, Street otherwise.
_NO_NUM = re.compile(r"(?<![\w.])No\.\s?(?=\d)")
_ST = re.compile(r"(?<![\w.])St\.(?![\w.])")
# dot-less "Main St": Street only when NOT followed by a capitalized word
# ("St Xavier" stays untouched — dotless Saint is left to the TTS)
_ST_BARE = re.compile(r"(?<![\w.])St(?![\w.])")
_ACRONYM = re.compile(r"(?<![\w.])((?:[A-Z]\.){2,})(?![\w])")


def abbrev_(text: str, ctx: Context) -> str:
    """Expand titles and abbreviations ("Dr.", "Pvt. Ltd.", "etc.", "vs.",
    "No. 5", "St." Saint/Street heuristic) and space out dotted acronyms
    ("U.S.A." -> "U S A")."""
    text = _ABBREV_RE.sub(lambda m: _ABBREV[m.group(1)], text)
    text = _NO_NUM.sub("Number ", text)

    def st(m: re.Match) -> str:
        rest = text[m.end():].lstrip()
        return "Saint" if rest[:1].isupper() else "Street"
    text = _ST.sub(st, text)

    def st_bare(m: re.Match) -> str:
        rest = text[m.end():].lstrip()
        return m.group(0) if rest[:1].isupper() else "Street"
    text = _ST_BARE.sub(st_bare, text)
    text = _ACRONYM.sub(lambda m: " ".join(m.group(1).replace(".", "")) , text)
    return text
#    boundaries so embedded numbers get verbalized while Latin stays verbatim.
#    e.g. "COVID19" -> "COVID 19", "5G" -> "5 G", "MP3" -> "MP 3".
# ---------------------------------------------------------------------------
_ALNUM_LD = re.compile(r"([A-Za-z])(\d)")
_ALNUM_DL = re.compile(r"(\d)([A-Za-z])")


def alphanumeric_split(text: str, ctx: Context) -> str:
    """Split Latin-letter/digit boundaries ("COVID19" -> "COVID 19") so the
    embedded number verbalizes while the Latin part stays verbatim."""
    text = _ALNUM_LD.sub(r"\1 \2", text)
    text = _ALNUM_DL.sub(r"\1 \2", text)
    return text


# ---------------------------------------------------------------------------
# 2. time  HH:MM(:SS)( am/pm )
# ---------------------------------------------------------------------------
# am/pm: "a.m." keeps its dots, but bare "am" must not swallow a sentence
# period ("10:30 am. Next") nor match inside a word ("ample").
_TIME = re.compile(r"(?<!\d)(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([ap]\.m\.?|[ap]m\b)?(?!\d)", re.I)


def _time_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        lang, lex = ctx.resolve(m.group(0))
        h, mnt, sec, ampm = m.group(1), m.group(2), m.group(3), m.group(4)
        parts = [N.cardinal(int(h), lang)]
        mi = int(mnt)
        if mi == 0 and lang == "en" and not sec:
            parts.append("o'clock")
        elif mi:
            if 1 <= mi <= 9 and lang == "en":
                parts += ["oh", N.cardinal(mi, lang)]
            else:
                parts.append(N.cardinal(mi, lang))
        if sec and int(sec):
            parts.append(N.cardinal(int(sec), lang))
        if ampm:
            parts.append(ampm.replace(".", "").lower())
        return " " + " ".join(parts) + " "
    return repl


def time_(text: str, ctx: Context) -> str:
    """HH:MM(:SS) with optional am/pm: "10:30 am" -> "ten thirty am"."""
    return _TIME.sub(_time_repl(ctx), text)


# ---------------------------------------------------------------------------
# 2b. ratio / score  "3:2", "16:9" — colon pairs the time handler rejected
#     (its minutes need exactly two digits).
# ---------------------------------------------------------------------------
_RATIO = re.compile(r"(?<![\d:])(\d{1,3}):(\d{1,3})(?![\d:])")


def _ratio_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        lang, lex = ctx.resolve(m.group(0))
        a = N.cardinal(_clean_int(m.group(1)), lang)
        b = N.cardinal(_clean_int(m.group(2)), lang)
        return f" {a} {lex.range_to} {b} "
    return repl


def ratio_(text: str, ctx: Context) -> str:
    """Colon pairs the time handler rejected: "3:2" -> "three to two"."""
    return _RATIO.sub(_ratio_repl(ctx), text)


# ---------------------------------------------------------------------------
# 3. date  d/m/yyyy | d-m-yyyy | yyyy-mm-dd
# ---------------------------------------------------------------------------
_DATE_DMY = re.compile(r"(?<!\d)(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})(?!\d)")
_DATE_YMD = re.compile(r"(?<!\d)(\d{4})-(\d{1,2})-(\d{1,2})(?!\d)")
# European "15.8.1947": 4-digit year only, and strict — an implausible triple
# stays untouched so the dotted (version) handler can read it.
_DATE_DOT = re.compile(r"(?<!\d)(\d{1,2})\.(\d{1,2})\.(\d{4})(?!\d)")


def _month_name(lex, mnum: int, lang: str) -> str:
    if mnum in lex.months:
        return lex.months[mnum]
    return N.cardinal(mnum, lang)


def _date_repl(ctx: Context, order, strict: bool = False):
    def repl(m: re.Match) -> str:
        lang, lex = ctx.resolve(m.group(0))
        g = m.groups()
        if order == "dmy":
            d, mo, y = int(g[0]), int(g[1]), int(g[2])
        else:  # ymd
            y, mo, d = int(g[0]), int(g[1]), int(g[2])
        if not (1 <= mo <= 12 and 1 <= d <= 31):
            if order == "dmy" and 1 <= d <= 12 and 1 <= mo <= 31:
                d, mo = mo, d  # US-style month/day ("08/15/1947")
            elif strict:
                return m.group(0)
            else:
                # hopeless as a date: read the components as plain numbers so
                # the span never leaks to the fraction handler ("25 over 17").
                cfg = ctx.cfg
                words = [_read_int_digits(_clean_int(x), lang, lex, cfg) for x in g]
                return " " + " ".join(words) + " "
        day = N.ordinal(d, lang, lex) if lang == "en" else N.cardinal(d, lang)
        month = _month_name(lex, mo, lang)
        yr = N.year(y, lang, lex) if y >= 100 else N.cardinal(y, lang)
        return f" {day} {month} {yr} "
    return repl


def date_(text: str, ctx: Context) -> str:
    """Numeric dates (d/m/yyyy, d-m-yyyy, yyyy-mm-dd, d.m.yyyy). An invalid
    day/month pair first tries US month/day order; a hopeless triple reads
    as plain numbers instead of leaking to the fraction handler."""
    text = _DATE_YMD.sub(_date_repl(ctx, "ymd"), text)
    text = _DATE_DMY.sub(_date_repl(ctx, "dmy"), text)
    text = _DATE_DOT.sub(_date_repl(ctx, "dmy", strict=True), text)
    return text


# ---------------------------------------------------------------------------
# 3b. textual dates (English): "15 August 1947", "Aug 15, 1947", "5 June".
#     Day becomes an ordinal, abbreviations expand, year reads year-style.
# ---------------------------------------------------------------------------
_MONTH_WORD = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?"
    r"|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
)
_TEXTDATE_DM = re.compile(
    r"(?<![\w/.-])(\d{1,2})(?:st|nd|rd|th)?\s+(" + _MONTH_WORD + r")\.?"
    r"(?:,?\s+(\d{4})(?!\d))?(?![\w])",
    re.I,
)
_TEXTDATE_MD = re.compile(
    r"(?<![\w/.-])(" + _MONTH_WORD + r")\.?\s+(\d{1,2})(?!\d)(?:st|nd|rd|th)?"
    r"(?:,?\s+(\d{4})(?!\d))?(?![\w])",
    re.I,
)
_MONTH_NUM = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
              "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
# lowercase forms that are ordinary English words: require a year to convert
_AMBIG_MONTHS = {"may", "march", "mar"}


def _textdate_repl(ctx: Context, order):
    def repl(m: re.Match) -> str:
        if order == "dm":
            day_s, mon_s, yr_s = m.group(1), m.group(2), m.group(3)
        else:
            mon_s, day_s, yr_s = m.group(1), m.group(2), m.group(3)
        day = int(day_s)
        if not (1 <= day <= 31):
            return m.group(0)
        if mon_s[0].islower() and mon_s.lower() in _AMBIG_MONTHS and not yr_s:
            return m.group(0)
        lang, lex = ctx.resolve(day_s)
        if lang != "en":
            return m.group(0)  # forced non-English numbers: leave to later handlers
        month = lex.months.get(_MONTH_NUM[mon_s[:3].lower()], mon_s)
        day_w = N.english_ordinal(day)
        parts = [day_w, month] if order == "dm" else [month, day_w]
        if yr_s:
            parts.append(N.year(int(yr_s), lang, lex))
        return " " + " ".join(parts) + " "
    return repl


def textdate_(text: str, ctx: Context) -> str:
    """English textual dates ("15 August 1947", "Aug 15, 1947", "5 June"):
    ordinal day, expanded month name, year-style year."""
    text = _TEXTDATE_DM.sub(_textdate_repl(ctx, "dm"), text)
    text = _TEXTDATE_MD.sub(_textdate_repl(ctx, "md"), text)
    return text


# ---------------------------------------------------------------------------
# 4. money  <symbol|code><amount>  e.g. ₹1,234.50  Rs 150  $5  INR 200
# ---------------------------------------------------------------------------
_CUR_TOKENS = ["₹", "$", "€", "£", "rs.", "rs", "inr", "usd", "eur", "gbp"]
_CUR_ALT = "|".join(re.escape(t) for t in sorted(_CUR_TOKENS, key=len, reverse=True))

# Scale words that may follow an amount ("₹5 lakh", "USD 50 million"). Spoken
# verbatim, placed between the number and the (plural) currency unit; a scaled
# amount never has a paise/cents part. Best-effort common forms per script;
# an unlisted form just falls back to the unscaled reading.
_SCALE_WORDS = [
    "lakhs", "lakh", "crores", "crore", "thousand", "million", "billion", "trillion",
    "हज़ार", "हजार", "लाख", "करोड़", "कोटी", "अरब",
    "লাখ", "লক্ষ", "কোটি", "হাজার",
    "லட்சம்", "கோடி", "ஆயிரம்",
    "లక్షల", "లక్ష", "కోట్ల", "కోటి",
    "ಲಕ್ಷ", "ಕೋಟಿ", "ಸಾವಿರ",
    "ലക്ഷം", "കോടി",
    "લાખ", "કરોડ", "હજાર",
    "ਲੱਖ", "ਕਰੋੜ", "ਹਜ਼ਾਰ",
    "لاکھ", "کروڑ", "ہزار", "ارب",
]

_MONEY = re.compile(
    r"(?<![A-Za-z])(?P<cur>" + _CUR_ALT + r")\s?(?P<sign>-?)(?P<amt>\d[\d,]*(?:\.\d+)?)"
    r"(?:\s+(?P<scale>" + "|".join(_SCALE_WORDS) + r")(?!\w))?",
    re.I,
)

# singular unit forms for value == 1 (unlisted words stay plural)
_SINGULAR = {
    "rupees": "rupee", "dollars": "dollar", "euros": "euro", "pounds": "pound",
    "cents": "cent", "paise": "paisa", "pence": "penny",
    "रुपये": "रुपया", "पैसे": "पैसा",
}


def _amount_words(amt: str, major: str, minor: str, lang: str, lex) -> str:
    """Unscaled amount reading with singular units and zero-major elision."""
    int_part, _, frac = amt.partition(".")
    int_part = _clean_int(int_part)
    int_val = int(int_part or "0")
    if major and int_val == 1:
        major = _SINGULAR.get(major, major)
    words = [N.cardinal(int_part or "0", lang)]
    if major:
        words.append(major)
    if frac and int(frac):
        # pad/truncate to 2 significant minor digits
        paise = int((frac + "00")[:2])
        if minor and paise == 1:
            minor = _SINGULAR.get(minor, minor)
        if int_val == 0:
            words = [N.cardinal(paise, lang)]  # "₹0.50" -> just "fifty paise"
        else:
            words += [lex.connector_and, N.cardinal(paise, lang)]
        if minor:
            words.append(minor)
    return " ".join(w for w in words if w)


def _money_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        amt = m.group("amt")
        lang, lex = ctx.resolve(amt)
        key = m.group("cur").lower()
        major, minor = lex.currency.get(key, ("", ""))
        neg = lex.negative + " " if m.group("sign") else ""
        scale = m.group("scale")
        if scale:
            num = to_ascii_digits(amt).replace(",", "")
            if "." in num:
                spoken = N.decimal(num, lang, lex)
            else:
                spoken = N.cardinal(num, lang)
            return " " + neg + " ".join(w for w in (spoken, scale, major) if w) + " "
        return " " + neg + _amount_words(amt, major, minor, lang, lex) + " "
    return repl


# suffix currency: "100₹", "250 rs" (symbols or a standalone rs token)
_MONEY_SUF = re.compile(
    r"(?<![\w.])(?P<amt>\d[\d,]*(?:\.\d+)?)\s?(?P<cur>₹|\$|€|£|(?i:rs)\.?)(?![A-Za-z0-9])"
)


def _money_suf_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        amt = m.group("amt")
        lang, lex = ctx.resolve(amt)
        key = m.group("cur").lower().rstrip(".") or m.group("cur").lower()
        major, minor = lex.currency.get(key, lex.currency.get(key + ".", ("", "")))
        if not major:
            return m.group(0)
        return " " + _amount_words(amt, major, minor, lang, lex) + " "
    return repl


def money_(text: str, ctx: Context) -> str:
    """Currency amounts: prefix symbol/code ("₹1,234.50", "Rs 150"), scale
    words ("₹5 lakh"), signs, singular units ("₹1" -> "one rupee"), and
    suffix forms ("100₹", "250 rs")."""
    text = _MONEY.sub(_money_repl(ctx), text)
    return _MONEY_SUF.sub(_money_suf_repl(ctx), text)


# ---------------------------------------------------------------------------
# 5. percent   12%   3.5 %
# ---------------------------------------------------------------------------
_PCT = re.compile(r"(?<![\w])([-+]?)(\d[\d,]*(?:\.\d+)?)\s*%")


def _pct_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        sign, num = m.group(1), m.group(2)
        lang, lex = ctx.resolve(num)
        if "." in num:
            spoken = N.decimal(num, lang, lex)
        else:
            spoken = N.cardinal(_clean_int(num), lang)
        spoken = _signed(spoken, sign, lex)
        return f" {spoken} {lex.percent} "
    return repl


def percent_(text: str, ctx: Context) -> str:
    """"12.5%" -> "twelve point five percent" (optional leading sign)."""
    return _PCT.sub(_pct_repl(ctx), text)


# ---------------------------------------------------------------------------
# 5b. Indian ID formats, spelled out: PAN (ABCDE1234F), IFSC (SBIN0001234),
#     vehicle plates (KA 01 AB 1234), PIN codes ("PIN 560001"). Must run
#     before measure/alphanumeric so unit-lookalikes inside them survive.
# ---------------------------------------------------------------------------
_PAN_ID = re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")
_IFSC_ID = re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b")
_PLATE_ID = re.compile(r"\b[A-Z]{2}[ -]?\d{1,2}[ -]?[A-Z]{1,2}[ -]?\d{3,4}\b")
_PIN_ID = re.compile(r"\b(PIN(?:\s?code)?|pincode)\s*:?\s*(\d{6})\b", re.I)


def _spell_id(tok: str, lang: str) -> str:
    """Letters one by one, digit runs digit-wise, separators dropped."""
    out = []
    for run in re.findall(r"\d+|[A-Za-z]", tok):
        out.append(N.split_digits(run, lang) if run.isdigit() else run)
    return " ".join(out)


def _id_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        lang, _lex = ctx.resolve(m.group(0))
        return " " + _spell_id(m.group(0), lang) + " "
    return repl


def ids_(text: str, ctx: Context) -> str:
    """Indian ID formats spelled letter-by-letter with digit-wise digits:
    PAN (ABCDE1234F), IFSC (SBIN0001234), vehicle plates (KA 01 AB 1234),
    and "PIN <6 digits>"."""
    repl = _id_repl(ctx)
    text = _PAN_ID.sub(repl, text)
    text = _IFSC_ID.sub(repl, text)
    text = _PLATE_ID.sub(repl, text)

    def pin(m: re.Match) -> str:
        lang, _lex = ctx.resolve(m.group(2))
        return f" {m.group(1)} {N.split_digits(m.group(2), lang)} "
    return _PIN_ID.sub(pin, text)


# ---------------------------------------------------------------------------
# 5c. blood pressure "120/80 mmHg" (unit or a BP trigger word). Must beat the
#     measure handler, which would otherwise eat "80 mmHg" and strand "120/".
# ---------------------------------------------------------------------------
_BP_UNIT = re.compile(r"(?<![\w./])(\d{2,3})/(\d{2,3})\s?(mm ?Hg)\b")
_BP_TRIG = re.compile(r"(?i:\b(BP|blood pressure)\s+)(\d{2,3})/(\d{2,3})(?![\w./])")


def _bp_repl(ctx: Context, trigger: bool):
    def repl(m: re.Match) -> str:
        g = m.groups()
        lang, lex = ctx.resolve(m.group(0))
        if lang != "en":
            return m.group(0)
        if trigger:
            word, a, b, unit = g[0], g[1], g[2], ""
        else:
            word, a, b, unit = "", g[0], g[1], " millimeters of mercury"
        head = f"{word} " if word else " "
        return f"{head}{N.cardinal(a, lang)} over {N.cardinal(b, lang)}{unit} "
    return repl


def bp_(text: str, ctx: Context) -> str:
    """Blood pressure ("120/80 mmHg", or "BP 120/80") -> "one hundred and
    twenty over eighty (millimeters of mercury)"."""
    text = _BP_UNIT.sub(_bp_repl(ctx, trigger=False), text)
    text = _BP_TRIG.sub(_bp_repl(ctx, trigger=True), text)
    return text


# ---------------------------------------------------------------------------
# 6. measure   number + unit   e.g. 5 kg, 10km, 37.5°C
# ---------------------------------------------------------------------------
# Case-sensitive on purpose: matching is NOT re.I so tech terms like "5G" are
# not read as "5 grams". Ambiguous bare single letters (m, l, in) are omitted;
# they collide with ordinary words and are better left to the number handler.
_UNIT_TOKENS = [
    "km/h", "kmph", "kph", "°C", "°F", "°", "kg", "mg", "km", "cm", "mm",
    "ml", "GB", "MB", "KB", "TB", "hr", "min", "sec", "ft", "g",
    "mAh", "kWh", "kHz", "MHz", "GHz", "Hz", "rpm", "mmHg",
]
_UNIT_ALT = "|".join(re.escape(t) for t in sorted(_UNIT_TOKENS, key=len, reverse=True))
_MEASURE = re.compile(
    r"(?<![\w])([-+]?)(\d[\d,]*(?:\.\d+)?)\s?(" + _UNIT_ALT + r")(?![\w])",
)


def _measure_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        sign, num, unit = m.group(1), m.group(2), m.group(3).lower()
        lang, lex = ctx.resolve(num)
        if "." in num:
            spoken = N.decimal(num, lang, lex)
        else:
            spoken = N.cardinal(_clean_int(num), lang)
        spoken = _signed(spoken, sign, lex)
        unit_word = lex.units.get(unit, unit)
        return f" {spoken} {unit_word} "
    return repl


def measure_(text: str, ctx: Context) -> str:
    """Number + unit ("5kg", "37.5°C", "2.4 GHz") -> spoken unit words.
    Unit matching is case-sensitive so "5G" is never five grams."""
    return _MEASURE.sub(_measure_repl(ctx), text)


# ---------------------------------------------------------------------------
# 6a. bare number + native-script scale word ("2 करोड़ लोग"): the scale word
#     proves the language, so the ASCII digits are read in it — the same
#     override native digits get — instead of defaulting to English.
# ---------------------------------------------------------------------------
_NATIVE_SCALES = [w for w in _SCALE_WORDS if not w.isascii()]
_NATIVE_SCALE_RE = re.compile(
    r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)\s+(" + "|".join(_NATIVE_SCALES) + r")(?!\w)"
)


def _native_scale_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        num, scale = m.group(1), m.group(2)
        lang = ctx.cfg.resolve_number_lang(native=True)
        lex = get_lexicon(lang)
        num_a = to_ascii_digits(num).replace(",", "")
        if "." in num_a:
            spoken = N.decimal(num_a, lang, lex)
        else:
            spoken = N.cardinal(num_a, lang)
        return f" {spoken} {scale} "
    return repl


def native_scale_(text: str, ctx: Context) -> str:
    """ASCII number + native-script scale word ("2 करोड़") reads the number
    in the scale word's language: "दो करोड़"."""
    return _NATIVE_SCALE_RE.sub(_native_scale_repl(ctx), text)


# ---------------------------------------------------------------------------
# 6b. numeric range  N-M (both sides <= 4 digits), optional %/unit suffix.
#     Runs after date (so 15-08-1947 stays a date) and before phone (so
#     1939-1945 is not read digit-by-digit). Longer sides are left for the
#     phone handler (98765-43210).
# ---------------------------------------------------------------------------
_RANGE = re.compile(
    r"(?<![\w.,-])(\d[\d,]*)\s*[-–—]\s*(\d[\d,]*)"
    r"(?:\s*(%|" + _UNIT_ALT + r"))?"
    r"(?!\.?\d)(?![A-Za-z_-])"
)


def _range_repl(ctx: Context):
    cfg = ctx.cfg

    def repl(m: re.Match) -> str:
        a_raw, b_raw, suf = m.group(1), m.group(2), m.group(3)
        a, b = _clean_int(a_raw), _clean_int(b_raw)
        if not a or not b or len(a) > 4 or len(b) > 4:
            return m.group(0)  # long sides: likely phone/ID, leave alone
        lang, lex = ctx.resolve(m.group(0))
        wa = _read_int_digits(a, lang, lex, cfg, allow_year="," not in a_raw)
        wb = _read_int_digits(b, lang, lex, cfg, allow_year="," not in b_raw)
        out = f"{wa} {lex.range_to} {wb}"
        if suf == "%":
            out += f" {lex.percent}"
        elif suf:
            out += f" {lex.units.get(suf.lower(), suf)}"
        return " " + out + " "
    return repl


def range_(text: str, ctx: Context) -> str:
    """"N-M" ranges up to 4 digits per side ("1939-1945", "10-15%", "5-10 kg")
    -> "N to M" (year-style sides where plausible); longer sides fall through
    to the phone handler."""
    return _RANGE.sub(_range_repl(ctx), text)


# ---------------------------------------------------------------------------
# 7. phone / long digit strings -> digit by digit
#    triggers on +CC numbers or runs of >= 7 digits (ignoring separators).
#    "." is NOT a phone separator: decimals ("3.14159265") and IPs must fall
#    through to the decimal/number handlers.
# ---------------------------------------------------------------------------
_PHONE = re.compile(r"(?<![\w.])(\+?\d[\d\s()-]{6,}\d)(?![\w])")


def _looks_like_phone(raw: str, digits: str, cfg) -> bool:
    """Shape gate for matches without a leading '+'.

    A single contiguous run of >= 7 digits qualifies. Separated groups qualify
    only when total >= 10 with every group >= 3 digits ("98765 43210",
    "011-2345-6789", Aadhaar "1234 5678 9012") — short-group lists such as
    "100 200 300" or "2020 2021" are ordinary numbers. A sequence made purely
    of plausible years ("2019 2020 2021") is a list of years, not a phone.
    """
    groups = re.findall(r"\d+", to_ascii_digits(raw))
    if len(groups) == 1:
        return True
    if len(digits) < 10 or min(len(g) for g in groups) < 3:
        return False
    lo, hi = cfg.year_range
    if all(len(g) == 4 and lo <= int(g) <= hi for g in groups):
        return False
    return True


def _phone_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        raw = m.group(1)
        digits = _clean_int(raw)
        if len(digits) < 7:
            return m.group(0)
        if not raw.strip().startswith("+") and not _looks_like_phone(raw, digits, ctx.cfg):
            return m.group(0)  # leave for the later numeric handlers
        lang, lex = ctx.resolve(raw)
        plus = "plus " if raw.strip().startswith("+") else ""
        return " " + plus + N.split_digits(digits, lang) + " "
    return repl


def phone_(text: str, ctx: Context) -> str:
    """Phone-shaped digit runs -> digit-by-digit ("+91 98765 43210");
    shape-gated (see :func:`_looks_like_phone`) so year lists and large
    cardinals pass through to the number handler."""
    return _PHONE.sub(_phone_repl(ctx), text)


# ---------------------------------------------------------------------------
# 7b. dotted numerics with >= 2 dots: versions ("3.11.4" -> cardinals joined
#     by the decimal-point word) and IPv4 ("192.168.1.1" -> digit-wise with
#     "dot"). Plain decimals (one dot) stay with the decimal handler.
# ---------------------------------------------------------------------------
_DOTTED = re.compile(r"(?<![\w.])(\d+(?:\.\d+){2,})(?![\w.])")


def _dotted_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        raw = m.group(1)
        lang, lex = ctx.resolve(raw)
        parts = to_ascii_digits(raw).split(".")
        if len(parts) == 4 and all(len(p) <= 3 and int(p) <= 255 for p in parts):
            words = " dot ".join(N.split_digits(p, lang) for p in parts)
        else:
            sep = f" {lex.decimal_point} "
            words = sep.join(N.cardinal(p, lang) for p in parts)
        return " " + words + " "
    return repl


def dotted_(text: str, ctx: Context) -> str:
    """Digit runs with >= 2 dots: IPv4 reads digit-wise with "dot"; versions
    ("3.11.4") read as cardinals joined by the decimal-point word."""
    return _DOTTED.sub(_dotted_repl(ctx), text)


# ---------------------------------------------------------------------------
# 7c. cricket score "287/5": runs "for" wickets, gated on a cricket word
#     within a +/-60 char window so ordinary fractions stay fractions.
# ---------------------------------------------------------------------------
_CRICKET = re.compile(r"(?<![\w./])(\d{2,3})/(\d{1,2})(?!\.?\d)(?![\w/])")
_CRICKET_CTX = re.compile(
    r"(?i)\b(overs?|wickets?|innings|declared|run ?rate|runs|batting|chasing|scored?)\b"
)


def _cricket_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        if int(m.group(2)) > 10:  # a side has at most 10 wickets
            return m.group(0)
        window = m.string[max(0, m.start() - 60):m.end() + 60]
        if not _CRICKET_CTX.search(window):
            return m.group(0)
        lang, lex = ctx.resolve(m.group(0))
        if lang != "en":
            return m.group(0)
        return f" {N.cardinal(m.group(1), lang)} for {N.cardinal(m.group(2), lang)} "
    return repl


def cricket_(text: str, ctx: Context) -> str:
    """"287/5" near a cricket word -> "two hundred and eighty seven for
    five"; without the context word the fraction handler keeps it."""
    return _CRICKET.sub(_cricket_repl(ctx), text)


# ---------------------------------------------------------------------------
# 8. fraction  a/b   (simple)
# ---------------------------------------------------------------------------
# Trailing guard: block only a real decimal continuation ("1/3.5"), never a
# sentence period ("equals 1/3.").
_FRACTION = re.compile(r"(?<![\w.])(\d+)\s*/\s*(\d+)(?!\.?\d)(?![\w])")
_EN_FRAC = {(1, 2): "one half", (1, 3): "one third", (2, 3): "two thirds",
            (1, 4): "one quarter", (3, 4): "three quarters"}


def _fraction_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        a, b = int(m.group(1)), int(m.group(2))
        lang, lex = ctx.resolve(m.group(0))
        if lang == "en":
            if (a, b) in _EN_FRAC:
                return " " + _EN_FRAC[(a, b)] + " "
            return f" {N.cardinal(a, lang)} over {N.cardinal(b, lang)} "
        return f" {N.cardinal(a, lang)} {lex.connector_and} {N.cardinal(b, lang)} "
    return repl


def fraction_(text: str, ctx: Context) -> str:
    """"a/b" -> a named fraction ("3/4" -> "three quarters") or "a over b"
    (English); other languages join with the "and" connector."""
    return _FRACTION.sub(_fraction_repl(ctx), text)


# ---------------------------------------------------------------------------
# 9. decimal  d.d
# ---------------------------------------------------------------------------
_DECIMAL = re.compile(r"(?<![\w])(-?\d[\d,]*\.\d+)(?![\w])")


def _decimal_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        num = m.group(1)
        lang, lex = ctx.resolve(num)
        return " " + N.decimal(num, lang, lex) + " "
    return repl


def decimal_(text: str, ctx: Context) -> str:
    """"3.14" -> "three point one four" (fraction digits read one by one)."""
    return _DECIMAL.sub(_decimal_repl(ctx), text)


# ---------------------------------------------------------------------------
# 9a. scientific notation "1.5e10" (English wording; before the alphanumeric
#     split turns it into "1.5 e 10").
# ---------------------------------------------------------------------------
_SCI = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)[eE]([+-]?\d{1,3})(?![\w.])")


def _sci_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        lang, lex = ctx.resolve(m.group(0))
        if lang != "en":
            return m.group(0)
        mant, exp = m.group(1), m.group(2)
        # Uppercase E with an integer mantissa is an ID, not math: flight
        # codes like "6E204" must fall through to the code handler.
        if "E" in m.group(0) and "." not in mant:
            return m.group(0)
        if "." in mant:
            mant_w = N.decimal(mant, lang, lex)
        else:
            mant_w = N.cardinal(mant, lang)
        neg = "minus " if exp.startswith("-") else ""
        exp_w = N.cardinal(exp.lstrip("+-"), lang)
        return f" {mant_w} times ten to the power {neg}{exp_w} "
    return repl


def scientific_(text: str, ctx: Context) -> str:
    """"1.5e10" -> "one point five times ten to the power ten" (English-only
    wording; other resolved languages pass through)."""
    return _SCI.sub(_sci_repl(ctx), text)


# ---------------------------------------------------------------------------
# 9a2. alphanumeric codes: a pure-alnum token with >= 2 letter<->digit
#      transitions ("AB123CD", "X9K42B", "6E204") is a code — spell letters,
#      digits digit-wise. Single-transition tokens ("32A", "B12", "COVID19")
#      keep the natural alphanumeric-split reading.
# ---------------------------------------------------------------------------
_CODE = re.compile(r"(?<![\w.])(?=[A-Za-z0-9]*\d)(?=[A-Za-z0-9]*[A-Za-z])[A-Za-z0-9]+(?![\w.])")


def _code_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        tok = m.group(0)
        if len(re.findall(r"\d+|[A-Za-z]+", tok)) < 3:  # runs = transitions+1
            return m.group(0)
        lang, _lex = ctx.resolve(tok)
        return " " + _spell_id(tok, lang) + " "
    return repl


def code_(text: str, ctx: Context) -> str:
    """Alphanumeric codes with >= 2 letter/digit transitions ("AB123CD",
    "6E204") spell out: letters one by one, digits digit-wise. Tokens with a
    single transition ("32A", "B12") keep the natural reading."""
    return _CODE.sub(_code_repl(ctx), text)


# ---------------------------------------------------------------------------
# 9b. decades (English idiom): "1990s" / "1980's" / "90s". Must run before the
#     alphanumeric split turns "1990s" into "1990 s".
# ---------------------------------------------------------------------------
_DECADE = re.compile(r"(?<![\w])(\d{4}|\d0)'?s\b")
_DECADE_WORDS = {"10": "tens", "20": "twenties", "30": "thirties", "40": "forties",
                 "50": "fifties", "60": "sixties", "70": "seventies",
                 "80": "eighties", "90": "nineties", "00": "hundreds"}


def _decade_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        tok = m.group(1)
        lang, lex = ctx.resolve(tok)
        if lang != "en":
            return m.group(0)  # decade wording is an English idiom
        if len(tok) == 2:
            word = _DECADE_WORDS.get(tok)
            return f" {word} " if word else m.group(0)
        if tok == "2000":
            return " two thousands "
        word = _DECADE_WORDS.get(tok[2:])
        if not word:
            return m.group(0)  # "1994s" etc.: not a decade
        return " " + N.cardinal(int(tok[:2]), "en") + " " + word + " "
    return repl


def decade_(text: str, ctx: Context) -> str:
    """"1990s" / "1980's" / "90s" -> "nineteen nineties" / "nineties"
    (English idiom; non-decades like "1994s" are left alone)."""
    return _DECADE.sub(_decade_repl(ctx), text)


# ---------------------------------------------------------------------------
# 10. ordinal   English 1st/2nd/3rd/4th ; generic <digits><suffix>
# ---------------------------------------------------------------------------
_EN_ORD = re.compile(r"(?<![\w])(\d+)(st|nd|rd|th)(?![\w])", re.I)


def _en_ord_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        lang, lex = ctx.resolve(m.group(1))
        # only when resolving to English; else leave to number handler
        if lang != "en":
            return m.group(0)
        return " " + N.english_ordinal(int(m.group(1))) + " "
    return repl


def ordinal_(text: str, ctx: Context) -> str:
    """English "21st" -> "twenty first"; native suffix ordinals ("5वाँ")
    speak the sentence language regardless of digit script."""
    text = _EN_ORD.sub(_en_ord_repl(ctx), text)
    # generic suffix ordinals in the sentence language (e.g. 5वाँ)
    lex = ctx.sentence_lex
    if lex.ordinal_suffix:
        suf = re.escape(lex.ordinal_suffix)
        pat = re.compile(r"(\d+)" + suf)

        def gen(m: re.Match) -> str:
            # The native suffix itself proves the language: speak the sentence
            # language even for ASCII digits ("5वाँ" -> "पाँचवाँ", not "fifth").
            return " " + N.ordinal(int(_clean_int(m.group(1))), ctx.cfg.lang, lex) + " "

        text = pat.sub(gen, text)
    return text


# ---------------------------------------------------------------------------
# 10b. position numbers: 3-4 digit numbers after room/page/flight/gate/bus
#      read in pairing style ("room 225" -> "room two twenty five"), the way
#      identifiers and positions are spoken. English idiom; off via
#      cfg.detect_positions.
# ---------------------------------------------------------------------------
_POSITION = re.compile(
    r"\b((?i:rooms?|pages?|flights?|gates?|bus(?:es)?))\s+"
    r"(?:((?i:no\.?|number))\s+)?(\d{3,4})(?!\.?\d)(?![\w,-])"
)


def _position_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        word, mid, digits = m.group(1), m.group(2), m.group(3)
        if mid:  # "room no. 225" -> speak "number"; keep "Number" verbatim
            word += " number" if mid.lower().rstrip(".") == "no" else f" {mid}"
        if not ctx.cfg.detect_positions or digits.startswith("0"):
            return m.group(0)  # leading zero: leave for digit-wise reading
        lang, lex = ctx.resolve(digits)
        if lang != "en":
            return m.group(0)
        v = int(digits)
        if len(digits) == 3:
            hi, lo = divmod(v, 100)
            if lo == 0:
                spoken = N.cardinal(v, lang)             # 200 -> two hundred
            elif lo < 10:
                spoken = f"{N.cardinal(hi, lang)} {lex.year_oh_word} {N.cardinal(lo, lang)}"
            else:
                spoken = f"{N.cardinal(hi, lang)} {N.cardinal(lo, lang)}"
        else:
            spoken = N.year(v, lang, lex)                # 6204 -> sixty two oh four
        return f"{word} {spoken} "
    return repl


def position_(text: str, ctx: Context) -> str:
    """3-4 digit numbers after a position word (room/page/flight/gate/bus)
    read in pairing style: "room 225" -> "room two twenty five", "flight
    6204" -> "flight sixty two oh four". Gated by ``detect_positions``."""
    return _POSITION.sub(_position_repl(ctx), text)


# ---------------------------------------------------------------------------
# 11. number: bare integers (optionally comma-grouped) + year heuristic
# ---------------------------------------------------------------------------
# Reject only a genuine decimal continuation (".5"); a trailing sentence period
# ("1947.") must NOT block the match.
_NUMBER = re.compile(r"(?<![\w.])([-+]?)(\d[\d,]*)(?!\.?\d)")


def _number_repl(ctx: Context):
    cfg = ctx.cfg

    def repl(m: re.Match) -> str:
        sign, body = m.group(1), m.group(2)
        lang, lex = ctx.resolve(body)
        digits = _clean_int(body)
        if not digits:
            return m.group(0)
        # Year heuristic: bare 4-digit, in range, no thousands separator.
        spoken = _read_int_digits(digits, lang, lex, cfg, allow_year="," not in body)
        return " " + _signed(spoken, sign, lex) + " "
    return repl


def number_(text: str, ctx: Context) -> str:
    """Bare integers: year-style for plausible bare 4-digit years, digit-wise
    for leading zeros ("007"), else cardinal; leading +/- spoken."""
    return _NUMBER.sub(_number_repl(ctx), text)


# ---------------------------------------------------------------------------
# 12. standalone symbols  ( & @ + = )
# ---------------------------------------------------------------------------
_SYM = re.compile(r"(?<=\s)([&@+=<>])(?=\s)")


def _sym_repl(ctx: Context):
    lex = ctx.sentence_lex

    def repl(m: re.Match) -> str:
        return lex.symbols.get(m.group(1), m.group(1))
    return repl


def symbol_(text: str, ctx: Context) -> str:
    """Standalone symbols between spaces (& @ + = < >) -> words."""
    return _SYM.sub(_sym_repl(ctx), text)


# ---------------------------------------------------------------------------
# 12b. context-gated roman numerals — always on: a preceding title word
#      ("Chapter IV", "Class X", "World War II") makes the numeral safe even
#      for single letters the opt-in handler must refuse.
# ---------------------------------------------------------------------------
_ROMAN_CTX = re.compile(
    r"\b((?i:chapter|part|class|section|volume|vol\.?|act|phase|grade|book"
    r"|unit|stage|level|war|standard|std\.?))\s+"
    r"(M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3}))(?![\w])"
)


def _roman_ctx_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        tok = m.group(2)
        if not tok:
            return m.group(0)
        return f"{m.group(1)} {N.cardinal(_roman_value(tok), 'en')}"
    return repl


def roman_ctx_(text: str, ctx: Context) -> str:
    """Roman numerals after a title word ("Chapter IV", "Class X",
    "World War II") -> cardinals. Always on: the trigger word makes even
    single-letter numerals safe."""
    return _ROMAN_CTX.sub(_roman_ctx_repl(ctx), text)


# ---------------------------------------------------------------------------
# 13. roman numerals (opt-in; conservative)
# ---------------------------------------------------------------------------
_ROMAN = re.compile(r"(?<![\w])(M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))(?![\w])")
_ROMAN_STOP = {"MIX", "DID", "DIM", "MILD", "CIVIC", "MIMIC", "LID", "DILL", "MID", "I", "V", "X"}
_ROMAN_MAP = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def _roman_value(s: str) -> int:
    total, prev = 0, 0
    for ch in reversed(s.upper()):
        v = _ROMAN_MAP[ch]
        total += -v if v < prev else v
        prev = max(prev, v)
    return total


def _roman_repl(ctx: Context):
    def repl(m: re.Match) -> str:
        tok = m.group(1)
        if not tok or tok.upper() in _ROMAN_STOP or len(tok) < 2:
            return m.group(0)
        lang, lex = "en", ctx.sentence_lex
        return " " + N.cardinal(_roman_value(tok), "en") + " "
    return repl


def roman_(text: str, ctx: Context) -> str:
    """Bare roman numerals anywhere -> cardinals. Opt-in via
    ``detect_roman`` — risky on ordinary uppercase words."""
    return _ROMAN.sub(_roman_repl(ctx), text)
