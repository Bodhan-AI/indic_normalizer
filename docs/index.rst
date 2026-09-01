indic_normalizer
================

A lightweight, pure-Python text normalizer designed as a pre-step before TTS
for the 22 scheduled languages of India (+ English). It turns raw, messy text
into clean spoken-form words: numbers, dates, currency, measures, LaTeX math,
and more — while stripping artifacts that hurt synthesis.

Quick start
-----------

.. code-block:: python

   from indic_normalizer import normalize

   normalize("India became independent in 1947.", lang="en")
   # 'India became independent in nineteen forty seven.'

   normalize("यह १९४७ की बात है।", lang="hi")
   # 'यह एक हज़ार नौ सौ सैंतालीस की बात है।'

See the project ``README.md`` for the full feature table, number-language
resolution rules, and configuration reference.

Handler pipeline
----------------

Semiotic-class handlers run in a fixed priority order (specific → general);
each rewrites its spans into words, so later handlers never re-match them::

   web → abbrev → time → ratio → date → textdate → money → range → percent →
   ids → bp → measure → native_scale → scientific → code → decade → ordinal →
   alphanumeric → phone → dotted → cricket → fraction → decimal → position →
   number → symbol → roman_ctx → roman (opt-in)

The registry lives in :mod:`indic_normalizer.classes`; each handler is
documented in :mod:`indic_normalizer.classes.handlers`.

API reference
-------------

.. toctree::
   :maxdepth: 2

   api
