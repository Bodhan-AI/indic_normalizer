Languages and number-language resolution
========================================

Supported language codes
------------------------

The following codes are accepted by ``lang``, ``number_lang``, and
``default_number_lang``:

.. list-table::
   :header-rows: 1
   :widths: 12 25 12 25

   * - Code
     - Language
     - Code
     - Language
   * - ``as``
     - Assamese
     - ``bn``
     - Bengali
   * - ``brx``
     - Bodo
     - ``doi``
     - Dogri
   * - ``en``
     - English (Indian)
     - ``gu``
     - Gujarati
   * - ``hi``
     - Hindi
     - ``kn``
     - Kannada
   * - ``ks``
     - Kashmiri
     - ``kok``
     - Konkani
   * - ``mai``
     - Maithili
     - ``ml``
     - Malayalam
   * - ``mni``
     - Manipuri (Meitei)
     - ``mr``
     - Marathi
   * - ``ne``
     - Nepali
     - ``or``
     - Odia
   * - ``pa``
     - Punjabi
     - ``sa``
     - Sanskrit
   * - ``sat``
     - Santali
     - ``sd``
     - Sindhi
   * - ``ta``
     - Tamil
     - ``te``
     - Telugu
   * - ``ur``
     - Urdu
     -
     -

How a number picks its language
-------------------------------

``lang`` selects the sentence lexicon. Unless a number language is forced,
ASCII digits are spoken in English and native-script digits are spoken in the
sentence language. Resolution follows this order:

1. Explicit ``number_lang`` wins.
2. ``force=True`` sets ``number_lang`` to ``lang``.
3. A native ordinal suffix or native-script scale word proves the sentence
   language even when the digits are ASCII.
4. Other native-script digits use ``lang``.
5. Other ASCII digits use ``default_number_lang`` (``"en"`` by default).

ASCII and native digits
~~~~~~~~~~~~~~~~~~~~~~~

.. doctest::

   >>> from indic_normalizer import normalize
   >>> normalize("भारत 1947 में स्वतंत्र हुआ।", lang="hi")
   'भारत nineteen forty seven में स्वतंत्र हुआ।'
   >>> normalize("यह १९४७ की बात है।", lang="hi")
   'यह एक हज़ार नौ सौ सैंतालीस की बात है।'

Force all numbers into one language
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``force=True`` is a shorthand for using the sentence language.
``number_lang`` can instead select a different supported language.

.. doctest::

   >>> normalize("भारत 1947 में स्वतंत्र हुआ।", lang="hi", force=True)
   'भारत एक हज़ार नौ सौ सैंतालीस में स्वतंत्र हुआ।'
   >>> normalize("1947", lang="en", number_lang="hi")
   'एक हज़ार नौ सौ सैंतालीस'

Change the ASCII-digit default
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. doctest::

   >>> normalize("भारत 1947 में स्वतंत्र हुआ।", lang="hi",
   ...           default_number_lang="hi")
   'भारत एक हज़ार नौ सौ सैंतालीस में स्वतंत्र हुआ।'

Native evidence overrides the ASCII default
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Native scale words and ordinal suffixes are strong language evidence.

.. doctest::

   >>> normalize("2.5 लाख रुपये", lang="hi")
   'दो दशमलव पाँच लाख रुपये'
   >>> normalize("5वाँ और 21वाँ", lang="hi")
   'पाँचवाँ और इक्कीसवाँ'

Native digit coverage
---------------------

Unicode decimal digits are decoded generically. Explicit script recognition
is included for Devanagari, Bengali, Gurmukhi, Gujarati, Odia, Tamil, Telugu,
Kannada, Malayalam, Arabic and extended Arabic, Meetei Mayek, and Ol Chiki
digit blocks.

Feature depth by language
-------------------------

* Cardinal numbers are provided for every listed language through the vendored
  number engine.
* English has the broadest contextual grammar: paired years and positions,
  named fractions, textual dates, decades, scientific notation, cricket
  scores, blood-pressure readings, and LaTeX speech.
* Numeric dates, decimals, percentages, currency, measurements, ranges, and
  suffix ordinals use per-language lexicon entries where available.
* Gregorian month names ship for 19 languages. Native suffix ordinal rules ship
  for 10; Dravidian ordinals are intentionally not formed by naive suffixing.
* Some glue-word entries are best-effort and await native review. Inspect them
  with :func:`indic_normalizer.lexicon.list_review_flags` and see
  :doc:`review-status`.
* Sindhi cardinal conversion has upstream gaps for some values. The wrapper
  falls back to digit-by-digit output instead of raising.

.. doctest::

   >>> from indic_normalizer.lexicon import list_review_flags
   >>> flags = list_review_flags()
   >>> "brx: months" in flags
   True
   >>> len(flags)
   44
