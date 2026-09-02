Configuration and pipeline behavior
===================================

Every option can be passed to :func:`indic_normalizer.normalize`, passed when
constructing :class:`indic_normalizer.Normalizer`, or set on a
:class:`indic_normalizer.NormalizerConfig` object.

Option reference
----------------

.. list-table::
   :header-rows: 1
   :widths: 24 18 58

   * - Option
     - Default
     - Behavior
   * - ``lang``
     - ``"en"``
     - Sentence/regional language. Selects the lexicon and native-digit
       language.
   * - ``number_lang``
     - ``None``
     - Forces every recognized number into this language.
   * - ``force``
     - ``False``
     - If true and ``number_lang`` is unset, forces numbers into ``lang``.
   * - ``default_number_lang``
     - ``"en"``
     - Language for ASCII digits when no force or native evidence applies.
   * - ``strip_parentheses``
     - ``True``
     - Removes balanced ``(...)`` spans, including nested content.
   * - ``keep_square_brackets``
     - ``True``
     - Protects ``[...]`` spans verbatim from normalization.
   * - ``keep_angle_brackets``
     - ``True``
     - Protects tag-shaped ``<...>`` spans verbatim from normalization.
   * - ``strip_escapes``
     - ``True``
     - Decodes ``\uXXXX``/``\xHH`` and removes literal control escapes and
       stray backslashes after LaTeX extraction.
   * - ``latex``
     - ``True``
     - Converts recognized LaTeX and ``\ce`` spans to spoken English.
   * - ``latex_verbosity``
     - ``"natural"``
     - Selects ``"natural"`` or ``"explicit"`` LaTeX speech.
   * - ``detect_years``
     - ``True``
     - Enables paired-year reading for eligible bare four-digit numbers.
   * - ``year_range``
     - ``(1100, 2099)``
     - Inclusive range of candidate years.
   * - ``detect_positions``
     - ``True``
     - Enables English pairing after room/page/flight/gate/bus triggers.
   * - ``detect_roman``
     - ``False``
     - Enables conservative bare Roman conversion. Triggered Roman numerals
       remain enabled regardless.
   * - ``emit_variations``
     - ``False``
     - Reserved configuration field. The current normalizer output is
       unchanged when it is true; use ``cardinal_variations`` directly.

``lang`` and ``number_lang`` are validated during configuration.
``default_number_lang`` should also be one of the supported codes listed in
:doc:`languages`.

Year detection
--------------

.. doctest::

   >>> from indic_normalizer import normalize
   >>> normalize("India became independent in 1947.", detect_years=False)
   'India became independent in one thousand nine hundred and forty seven.'
   >>> normalize("The manuscript dates to 1050.")
   'The manuscript dates to one thousand and fifty.'
   >>> normalize("The manuscript dates to 1050.", year_range=(1000, 2099))
   'The manuscript dates to ten fifty.'

Year detection applies only to bare, ungrouped four-digit numbers. Currency,
measurements, comma-grouped quantities, IDs, and other specific classes run
first and keep their own readings.

.. _artifact-handling:

Artifact handling and tags
--------------------------

Control and Unicode cleanup always runs. It NFC-normalizes text, converts the
Unicode minus sign to ASCII minus, removes control and zero-width characters,
collapses whitespace/newlines, and produces NFC output again at the end.

Escape cleanup
~~~~~~~~~~~~~~

Literal ``\n``, ``\t``, and similar escape artifacts become spaces;
``\uXXXX`` and ``\xHH`` are decoded. Disable this only if downstream code needs
literal backslashes.

.. doctest::

   >>> normalize(r"First\nSecond\t\u0041")
   'First Second A'
   >>> normalize(r"First\nSecond", strip_escapes=False)
   'First\\nSecond'

Parentheses
~~~~~~~~~~~

Balanced parentheses, including nested pairs, are removed by default.
Unmatched parentheses remain so a stray opening mark cannot delete the rest of
an utterance.

.. doctest::

   >>> normalize("text (remove (this) too) kept")
   'text kept'
   >>> normalize("a ( b 42")
   'a ( b forty two'
   >>> normalize("Keep (this note) and 42.", strip_parentheses=False)
   'Keep (this note) and forty two.'

Square and angle tags
~~~~~~~~~~~~~~~~~~~~~

Square spans and tag-shaped angle spans are masked before handlers run, then
restored byte-for-byte. Bare comparisons such as ``5 < 10`` are not tags.
Turning a ``keep_*`` option off does not delete the markup; it exposes its
contents to normalization.

.. doctest::

   >>> normalize("Say [pause 2] <break time='1s'/> now.")
   "Say [pause 2] <break time='1s'/> now."
   >>> normalize("Say [pause 2] <break time='1s'/> now.",
   ...           keep_square_brackets=False)
   "Say [pause two ] <break time='1s'/> now."
   >>> normalize("Say [pause 2] <break time='1s'/> now.",
   ...           keep_angle_brackets=False)
   "Say [pause 2] <break time=' one s'/> now."

Pipeline order
--------------

Processing occurs in these stages:

1. Unicode/control cleanup.
2. LaTeX span conversion.
3. Literal escape cleanup.
4. Square/angle tag protection.
5. Balanced-parenthetical removal.
6. Semiotic-class handlers.
7. Tag restoration.
8. Whitespace and punctuation cleanup, followed by NFC normalization.

The handlers use a fixed specific-to-general order::

   web → abbrev → time → ratio → date → textdate → money → range → percent →
   ids → bp → measure → native_scale → scientific → code → decade → ordinal →
   alphanumeric → phone → dotted → cricket → fraction → decimal → position →
   number → symbol → roman_ctx → roman (opt-in)

Each successful handler replaces its numeric span with words. Later handlers
therefore cannot reinterpret it. This priority explains several deliberate
decisions:

* ``15-08-1947`` is a date before it could become a range.
* ``10-15%`` is a range before it could become a single percentage.
* ``120/80 mmHg`` is blood pressure before ``mmHg`` becomes a measurement.
* ``287/5`` near “overs” is a cricket score before it becomes a fraction.
* ``6E204`` is a code because uppercase integer scientific notation is gated.
* URLs run first so their punctuation and embedded digits remain one unit.

There is no public per-handler enable/disable switch. The behavior knobs are
the configuration fields above. For specialized policies, normalize only the
inputs that belong in scope or use the documented lower-level helpers in
:doc:`api`.

Idempotency and production use
------------------------------

Normalized output is designed to be stable under another pass. Preserve raw
input alongside normalized text for auditing, and pin the package version when
spoken wording is part of a production contract. Context-sensitive handlers
use local text windows, so normalize complete utterances rather than arbitrary
substrings or batches concatenated into one string.
