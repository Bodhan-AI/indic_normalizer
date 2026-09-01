# -*- coding: utf-8 -*-
"""Per-language lexicon data (glue words the number engine cannot supply).

Fields left unspecified for a language fall back to the English defaults in
:class:`~indic_normalizer.lexicon.base.Lexicon`. This is intentional: for a
lightweight TTS pre-step, unit/symbol tokens (kg, km, +, @) are very often
spoken in English even inside regional sentences.

Entries whose native wording could not be verified by a native speaker are
listed in ``review=(...)`` so they can be surfaced via
``lexicon.list_review_flags()``. Cardinals themselves come from the vendored
engine and are NOT part of this best-effort layer.
"""

# Common English units / currency reused as fallbacks.
_EN_UNITS = {
    "kg": "kilograms", "g": "grams", "mg": "milligrams",
    "km": "kilometers", "m": "meters", "cm": "centimeters", "mm": "millimeters",
    "ml": "milliliters", "l": "liters",
    "km/h": "kilometers per hour", "kmph": "kilometers per hour", "kph": "kilometers per hour",
    "%": "percent", "°": "degrees", "°c": "degrees celsius", "°f": "degrees fahrenheit",
    "ft": "feet", "in": "inches", "hr": "hours", "min": "minutes", "sec": "seconds",
    "kb": "kilobytes", "mb": "megabytes", "gb": "gigabytes", "tb": "terabytes",
    "mah": "milliamp hours", "kwh": "kilowatt hours",
    "hz": "hertz", "khz": "kilohertz", "mhz": "megahertz", "ghz": "gigahertz",
    "rpm": "revolutions per minute", "mmhg": "millimeters of mercury",
}

_EN_SYMBOLS = {
    "+": "plus", "-": "minus", "=": "equals", "@": "at", "&": "and",
    "/": "slash", "*": "star", "#": "hash", "%": "percent",
    "~": "tilde", "^": "caret", "_": "underscore", "\\": "backslash",
    "|": "pipe", "<": "less than", ">": "greater than",
}

_EN_CURRENCY = {
    "₹": ("rupees", "paise"), "rs": ("rupees", "paise"), "rs.": ("rupees", "paise"),
    "inr": ("rupees", "paise"), "$": ("dollars", "cents"), "usd": ("dollars", "cents"),
    "€": ("euros", "cents"), "eur": ("euros", "cents"),
    "£": ("pounds", "pence"), "gbp": ("pounds", "pence"),
}

_EN_MONTHS = {
    1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
    7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December",
}

# Rupee currency tuples in various languages (major, minor).
_RUPEE = {
    "hi": ("रुपये", "पैसे"), "mr": ("रुपये", "पैसे"), "ne": ("रुपैयाँ", "पैसा"),
    "bn": ("টাকা", "পয়সা"), "as": ("টকা", "পইছা"), "gu": ("રૂપિયા", "પૈસા"),
    "pa": ("ਰੁਪਏ", "ਪੈਸੇ"), "or": ("ଟଙ୍କା", "ପଇସା"), "ta": ("ரூபாய்", "பைசா"),
    "te": ("రూపాయలు", "పైసలు"), "kn": ("ರೂಪಾಯಿ", "ಪೈಸೆ"), "ml": ("രൂപ", "പൈസ"),
    "ur": ("روپے", "پیسے"), "sa": ("रूप्यकाणि", "पैसा"),
    "doi": ("रुपये", "पैसे"), "kok": ("रुपये", "पैसे"), "mai": ("रुपये", "पैसे"),
    "ks": ("روپے", "پیسے"),
}

# decimal-point word per language. doi/kok/mai use the standard Hindi loan;
# ks (Perso-Arabic) and sd (the vendored engine speaks Devanagari Sindhi) are
# best-effort fills kept in the review list.
_POINT = {
    "hi": "दशमलव", "mr": "दशांश", "ne": "दशमलव", "sa": "दशांशः",
    "bn": "দশমিক", "as": "দশমিক", "gu": "દશાંશ", "pa": "ਦਸ਼ਮਲਵ",
    "or": "ଦଶମିକ", "ta": "புள்ளி", "te": "దశాంశ", "kn": "ದಶಮಾಂಶ",
    "ml": "ദശാംശം", "ur": "اعشاریہ",
    "doi": "दशमलव", "kok": "दशमलव", "mai": "दशमलव",
    "ks": "اعشاریہ", "sd": "दशमलव",
}

# percent word per language
_PERCENT = {
    "hi": "प्रतिशत", "mr": "टक्के", "ne": "प्रतिशत", "sa": "प्रतिशतम्",
    "bn": "শতাংশ", "as": "শতাংশ", "gu": "ટકા", "pa": "ਪ੍ਰਤੀਸ਼ਤ",
    "or": "ପ୍ରତିଶତ", "ta": "சதவீதம்", "te": "శాతం", "kn": "ಶೇಕಡಾ",
    "ml": "ശതമാനം", "ur": "فیصد",
    "doi": "प्रतिशत", "kok": "प्रतिशत", "mai": "प्रतिशत", "ks": "فیصد",
}

# ordinal suffix (appended to cardinal) — only languages where plain
# concatenation is correct. Dravidian ordinals (ta/te/kn/ml) need stem
# sandhi (ఐదు+వ -> ఐదవ), so they stay unfilled and review-flagged rather
# than filled wrongly.
_ORD_SUFFIX = {
    "hi": "वाँ", "mr": "वा", "ne": "औं", "bn": "তম", "as": "তম",
    "gu": "મો", "or": "ତମ", "sa": "तमः", "pa": "ਵਾਂ", "ur": "واں",
}

_ORD_IRREGULAR = {
    "hi": {1: "पहला", 2: "दूसरा", 3: "तीसरा", 4: "चौथा", 5: "पाँचवाँ", 6: "छठा"},
    "mr": {1: "पहिला", 2: "दुसरा", 3: "तिसरा", 4: "चौथा"},
    "bn": {1: "প্রথম", 2: "দ্বিতীয়", 3: "তৃতীয়", 4: "চতুর্থ"},
    "pa": {1: "ਪਹਿਲਾ", 2: "ਦੂਜਾ", 3: "ਤੀਜਾ", 4: "ਚੌਥਾ"},
    "ur": {1: "پہلا", 2: "دوسرا", 3: "تیسرا", 4: "چوتھا"},
}

# Year context trigger words (lowercased). Purely used as heuristic hints;
# ASCII years default to English anyway.
_YEAR_TRIGGERS = {
    "en": ("in", "year", "since", "by", "during", "circa", "around", "born", "established", "founded"),
    "hi": ("साल", "वर्ष", "सन", "ईस्वी", "में"),
    "mr": ("साल", "वर्ष", "सन", "मध्ये"),
    "bn": ("সাল", "বছর", "সালে", "খ্রিস্টাব্দ"),
    "ta": ("ஆண்டு", "வருடம்"),
    "te": ("సంవత్సరం", "ఏడాది"),
    "kn": ("ವರ್ಷ", "ಸಾಲಿನ"),
    "ml": ("വർഷം", "വര്ഷം"),
    "gu": ("વર્ષ", "સાલ"),
    "ur": ("سال", "برس", "عیسوی"),
}

# Full per-language override table. Only fields we are reasonably confident
# about are set; the rest fall back to English defaults in Lexicon.
LEX_DATA = {
    "en": dict(
        decimal_point="point", negative="minus", percent="percent",
        connector_and="and", year_pairing=True, year_hundred_word="hundred",
        year_oh_word="oh", symbols=_EN_SYMBOLS, currency=_EN_CURRENCY,
        units=_EN_UNITS, months=_EN_MONTHS, year_trigger_words=_YEAR_TRIGGERS["en"],
    ),
}


# range connector per language ("10-15" -> "दस से पंद्रह") — best-effort
_RANGE_TO = {
    "hi": "से", "mr": "ते", "ne": "देखि",
    "bn": "থেকে", "as": "পৰা", "gu": "થી", "pa": "ਤੋਂ",
    "or": "ରୁ", "ta": "முதல்", "te": "నుండి", "kn": "ರಿಂದ",
    "ml": "മുതൽ", "ur": "سے",
    "doi": "से", "kok": "से", "mai": "से",
}

# "and" connector per language (used e.g. between rupees and paise)
_AND = {
    "hi": "और", "mr": "आणि", "ne": "र", "sa": "च",
    "bn": "এবং", "as": "আৰু", "gu": "અને", "pa": "ਅਤੇ",
    "or": "ଏବଂ", "ta": "மற்றும்", "te": "మరియు", "kn": "ಮತ್ತು",
    "ml": "ഒപ്പം", "ur": "اور",
    "kok": "आनी", "doi": "और", "mai": "आ",
}


def _build_indic(lang, months=None, extra_review=()):
    """Assemble an Indic override dict from the compact field tables above."""
    d = {}
    if lang in _AND:
        d["connector_and"] = _AND[lang]
    review = []
    if lang in _POINT:
        d["decimal_point"] = _POINT[lang]
    else:
        review.append("decimal_point")
    if lang in _PERCENT:
        d["percent"] = _PERCENT[lang]
    else:
        review.append("percent")
    if lang in _RUPEE:
        # merge regional rupee over the English currency fallbacks
        cur = dict(_EN_CURRENCY)
        cur["₹"] = _RUPEE[lang]
        cur["rs"] = _RUPEE[lang]
        cur["inr"] = _RUPEE[lang]
        d["currency"] = cur
    else:
        review.append("currency")
    if lang in _ORD_SUFFIX:
        d["ordinal_suffix"] = _ORD_SUFFIX[lang]
    if lang in _ORD_IRREGULAR:
        d["ordinal_irregular"] = _ORD_IRREGULAR[lang]
    if "ordinal_suffix" not in d:
        review.append("ordinal")
    if lang in _RANGE_TO:
        d["range_to"] = _RANGE_TO[lang]
    else:
        review.append("range_to")
    if lang in _YEAR_TRIGGERS:
        d["year_trigger_words"] = _YEAR_TRIGGERS[lang]
    if months:
        d["months"] = months
    else:
        review.append("months")
    # units & symbols fall back to English (commonly spoken in English)
    d["review"] = tuple(review) + tuple(extra_review)
    return d


# Gregorian month names — standard newspaper transliterations per script.
_HI_MONTHS = {
    1: "जनवरी", 2: "फ़रवरी", 3: "मार्च", 4: "अप्रैल", 5: "मई", 6: "जून",
    7: "जुलाई", 8: "अगस्त", 9: "सितंबर", 10: "अक्टूबर", 11: "नवंबर", 12: "दिसंबर",
}
_MONTHS = {
    "hi": _HI_MONTHS,
    "mr": {1: "जानेवारी", 2: "फेब्रुवारी", 3: "मार्च", 4: "एप्रिल", 5: "मे", 6: "जून",
           7: "जुलै", 8: "ऑगस्ट", 9: "सप्टेंबर", 10: "ऑक्टोबर", 11: "नोव्हेंबर", 12: "डिसेंबर"},
    "ne": {1: "जनवरी", 2: "फेब्रुअरी", 3: "मार्च", 4: "अप्रिल", 5: "मे", 6: "जुन",
           7: "जुलाई", 8: "अगस्ट", 9: "सेप्टेम्बर", 10: "अक्टोबर", 11: "नोभेम्बर", 12: "डिसेम्बर"},
    "bn": {1: "জানুয়ারি", 2: "ফেব্রুয়ারি", 3: "মার্চ", 4: "এপ্রিল", 5: "মে", 6: "জুন",
           7: "জুলাই", 8: "আগস্ট", 9: "সেপ্টেম্বর", 10: "অক্টোবর", 11: "নভেম্বর", 12: "ডিসেম্বর"},
    "as": {1: "জানুৱাৰী", 2: "ফেব্ৰুৱাৰী", 3: "মাৰ্চ", 4: "এপ্ৰিল", 5: "মে", 6: "জুন",
           7: "জুলাই", 8: "আগষ্ট", 9: "ছেপ্টেম্বৰ", 10: "অক্টোবৰ", 11: "নৱেম্বৰ", 12: "ডিচেম্বৰ"},
    "gu": {1: "જાન્યુઆરી", 2: "ફેબ્રુઆરી", 3: "માર્ચ", 4: "એપ્રિલ", 5: "મે", 6: "જૂન",
           7: "જુલાઈ", 8: "ઑગસ્ટ", 9: "સપ્ટેમ્બર", 10: "ઑક્ટોબર", 11: "નવેમ્બર", 12: "ડિસેમ્બર"},
    "pa": {1: "ਜਨਵਰੀ", 2: "ਫਰਵਰੀ", 3: "ਮਾਰਚ", 4: "ਅਪ੍ਰੈਲ", 5: "ਮਈ", 6: "ਜੂਨ",
           7: "ਜੁਲਾਈ", 8: "ਅਗਸਤ", 9: "ਸਤੰਬਰ", 10: "ਅਕਤੂਬਰ", 11: "ਨਵੰਬਰ", 12: "ਦਸੰਬਰ"},
    "or": {1: "ଜାନୁଆରୀ", 2: "ଫେବୃଆରୀ", 3: "ମାର୍ଚ୍ଚ", 4: "ଅପ୍ରେଲ", 5: "ମଇ", 6: "ଜୁନ",
           7: "ଜୁଲାଇ", 8: "ଅଗଷ୍ଟ", 9: "ସେପ୍ଟେମ୍ବର", 10: "ଅକ୍ଟୋବର", 11: "ନଭେମ୍ବର", 12: "ଡିସେମ୍ବର"},
    "ta": {1: "ஜனவரி", 2: "பிப்ரவரி", 3: "மார்ச்", 4: "ஏப்ரல்", 5: "மே", 6: "ஜூன்",
           7: "ஜூலை", 8: "ஆகஸ்ட்", 9: "செப்டம்பர்", 10: "அக்டோபர்", 11: "நவம்பர்", 12: "டிசம்பர்"},
    "te": {1: "జనవరి", 2: "ఫిబ్రవరి", 3: "మార్చి", 4: "ఏప్రిల్", 5: "మే", 6: "జూన్",
           7: "జూలై", 8: "ఆగస్టు", 9: "సెప్టెంబర్", 10: "అక్టోబర్", 11: "నవంబర్", 12: "డిసెంబర్"},
    "kn": {1: "ಜನವರಿ", 2: "ಫೆಬ್ರವರಿ", 3: "ಮಾರ್ಚ್", 4: "ಏಪ್ರಿಲ್", 5: "ಮೇ", 6: "ಜೂನ್",
           7: "ಜುಲೈ", 8: "ಆಗಸ್ಟ್", 9: "ಸೆಪ್ಟೆಂಬರ್", 10: "ಅಕ್ಟೋಬರ್", 11: "ನವೆಂಬರ್", 12: "ಡಿಸೆಂಬರ್"},
    "ml": {1: "ജനുവരി", 2: "ഫെബ്രുവരി", 3: "മാർച്ച്", 4: "ഏപ്രിൽ", 5: "മേയ്", 6: "ജൂൺ",
           7: "ജൂലൈ", 8: "ഓഗസ്റ്റ്", 9: "സെപ്റ്റംബർ", 10: "ഒക്ടോബർ", 11: "നവംബർ", 12: "ഡിസംബർ"},
    "ur": {1: "جنوری", 2: "فروری", 3: "مارچ", 4: "اپریل", 5: "مئی", 6: "جون",
           7: "جولائی", 8: "اگست", 9: "ستمبر", 10: "اکتوبر", 11: "نومبر", 12: "دسمبر"},
}
# Devanagari-script languages share the Hindi forms; ks follows Urdu; sd's
# vendored engine speaks Devanagari Sindhi, so Devanagari forms fit. The
# borrowed sets (and sa) stay review-flagged below.
for _l in ("doi", "kok", "mai", "sa", "sd"):
    _MONTHS[_l] = _HI_MONTHS
_MONTHS["ks"] = _MONTHS["ur"]

# Best-effort fills that a native speaker should still confirm.
_EXTRA_REVIEW = {
    "ks": ("decimal_point", "percent", "currency", "months"),
    "sd": ("decimal_point", "months"),
    "sa": ("months",),
    "doi": ("months", "connector_and"), "kok": ("months",),
    "mai": ("months", "connector_and"),
}

for _lang in (
    "as", "bn", "brx", "doi", "gu", "hi", "kn", "ks", "kok", "mai", "ml",
    "mni", "mr", "ne", "or", "pa", "sa", "sat", "sd", "ta", "te", "ur",
):
    LEX_DATA[_lang] = _build_indic(
        _lang, months=_MONTHS.get(_lang), extra_review=_EXTRA_REVIEW.get(_lang, ()),
    )
