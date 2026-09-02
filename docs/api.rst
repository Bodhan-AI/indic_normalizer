API reference
=============

Top-level API
-------------

.. automodule:: indic_normalizer

.. autofunction:: indic_normalizer.normalize

.. autoclass:: indic_normalizer.Normalizer
   :members: normalize

.. autoclass:: indic_normalizer.NormalizerConfig
   :members: resolve_number_lang

.. autodata:: indic_normalizer.SUPPORTED_LANGS
   :no-value:

.. autodata:: indic_normalizer.__version__
   :no-value:

LaTeX API
---------

.. autofunction:: indic_normalizer.latex_to_speech

.. autofunction:: indic_normalizer.latex.convert_spans

.. autodata:: indic_normalizer.latex.LATEX_SPAN_PATTERN
   :no-value:

Chemistry helpers
~~~~~~~~~~~~~~~~~

These helpers are useful when an application identifies bare formula tokens
itself. The main normalizer only auto-detects chemistry in ``\ce{...}`` spans.

.. autofunction:: indic_normalizer.latex.chemistry.looks_like_formula

.. autofunction:: indic_normalizer.latex.chemistry.read_formula

.. autofunction:: indic_normalizer.latex.chemistry.read_ce

Number helpers
--------------

These functions bypass contextual classification and directly verbalize a
known numeric value.

.. autofunction:: indic_normalizer.numbers.cardinal

.. autofunction:: indic_normalizer.numbers.cardinal_variations

.. autofunction:: indic_normalizer.numbers.split_digits

.. autofunction:: indic_normalizer.numbers.decimal

.. autofunction:: indic_normalizer.numbers.ordinal

.. autofunction:: indic_normalizer.numbers.year

.. autofunction:: indic_normalizer.numbers.english_ordinal

Numeral and script helpers
--------------------------

.. autofunction:: indic_normalizer.numerals.is_ascii_digit

.. autofunction:: indic_normalizer.numerals.is_native_digit

.. autofunction:: indic_normalizer.numerals.digit_value

.. autofunction:: indic_normalizer.numerals.to_ascii_digits

.. autofunction:: indic_normalizer.numerals.digits_are_native

.. autofunction:: indic_normalizer.numerals.script_of_digits

.. autofunction:: indic_normalizer.preprocess.char_script

.. autofunction:: indic_normalizer.preprocess.dominant_script

Lexicon API
-----------

.. autoclass:: indic_normalizer.lexicon.Lexicon
   :members: ordinal

.. autofunction:: indic_normalizer.lexicon.get_lexicon

.. autofunction:: indic_normalizer.lexicon.list_review_flags

Preprocessing helpers
---------------------

These are the same building blocks used by :class:`indic_normalizer.Normalizer`.
Calling tag protection manually requires retaining the returned store and
passing it back to ``restore_tags``.

.. autofunction:: indic_normalizer.preprocess.clean_controls

.. autofunction:: indic_normalizer.preprocess.strip_escapes

.. autofunction:: indic_normalizer.preprocess.protect_tags

.. autofunction:: indic_normalizer.preprocess.restore_tags

.. autofunction:: indic_normalizer.preprocess.strip_parentheses

Advanced pipeline API
---------------------

The following interface exposes the ordered handler pipeline. It is useful for
experimentation and extensions but is lower-level than the stable top-level
API; applications normally use :class:`indic_normalizer.Normalizer`.

.. automodule:: indic_normalizer.normalizer
   :no-members:

.. automodule:: indic_normalizer.config
   :no-members:

.. autoclass:: indic_normalizer.classes.Context
   :members: sentence_lex, resolve

.. autofunction:: indic_normalizer.classes.apply_all

Handler functions
~~~~~~~~~~~~~~~~~

Every handler has the signature ``handler(text, context) -> text``. The public
registry, rather than alphabetical order below, determines precedence; see
:doc:`configuration`.

.. automodule:: indic_normalizer.classes.handlers
   :members:
