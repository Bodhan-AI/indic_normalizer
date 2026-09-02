indic_normalizer documentation
==============================

``indic_normalizer`` is a dependency-free Python text normalizer for TTS. It
turns written forms—numbers, dates, money, measurements, identifiers, web
addresses, and LaTeX—into words suitable for speech synthesis. Cardinal
numbers are available in the 22 scheduled languages of India plus English.

.. doctest::

   >>> from indic_normalizer import normalize
   >>> normalize("India became independent in 1947.")
   'India became independent in nineteen forty seven.'
   >>> normalize("यह १९४७ की बात है।", lang="hi")
   'यह एक हज़ार नौ सौ सैंतालीस की बात है।'

The package is designed as a deterministic pre-processing step. It has no
runtime dependencies, does not require a model, and returns NFC-normalized
text. Calling it again on normalized output is safe.

Choose a guide
--------------

* :doc:`getting-started` — installation and one-shot, reusable, and
  configuration-object usage.
* :doc:`normalization-cases` — a feature-by-feature catalog with inputs,
  outputs, guards, and edge cases.
* :doc:`languages` — supported language codes and number-language resolution.
* :doc:`latex` — math, physics, chemistry, delimiters, environments, and
  verbosity.
* :doc:`configuration` — every option, pipeline order, artifact handling, and
  production integration advice.
* :doc:`api` — the public Python API and useful lower-level helpers.

Documentation contents
----------------------

.. toctree::
   :maxdepth: 2
   :caption: User guide

   getting-started
   normalization-cases
   languages
   latex
   configuration

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api
   review-status

Project status
--------------

The package is beta software. Cardinal number support is broad; language-
specific glue such as month names, currency words, ordinal suffixes, and
connectors has a smaller review surface. See :doc:`review-status` before using
unreviewed wording in a production voice.
