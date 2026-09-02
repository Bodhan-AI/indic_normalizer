Getting started
===============

Requirements and installation
-----------------------------

``indic_normalizer`` requires Python 3.10 or newer and has no runtime
dependencies.

Install from a local checkout:

.. code-block:: console

   $ python -m pip install .

For an editable development install with the test dependency:

.. code-block:: console

   $ python -m pip install -e ".[test]"
   $ python -m pytest -q

One-shot normalization
----------------------

Use :func:`indic_normalizer.normalize` for occasional calls. ``lang`` is the
sentence language; it is not necessarily the language used for ASCII digits.

.. doctest::

   >>> from indic_normalizer import normalize
   >>> normalize("There are 1,947 entries.")
   'There are one thousand nine hundred and forty seven entries.'
   >>> normalize("भारत 1947 में स्वतंत्र हुआ।", lang="hi")
   'भारत nineteen forty seven में स्वतंत्र हुआ।'
   >>> normalize("भारत 1947 में स्वतंत्र हुआ।", lang="hi", force=True)
   'भारत एक हज़ार नौ सौ सैंतालीस में स्वतंत्र हुआ।'

See :doc:`languages` for the complete resolution rules.

Reuse a normalizer
------------------

Construct :class:`indic_normalizer.Normalizer` once when processing many
utterances with the same settings.

.. doctest::

   >>> from indic_normalizer import Normalizer
   >>> normalizer = Normalizer(lang="en", detect_years=False)
   >>> [normalizer.normalize(text) for text in ["In 1947.", "Room 225."]]
   ['In one thousand nine hundred and forty seven.', 'Room two twenty five.']

Use a configuration object
--------------------------

:class:`indic_normalizer.NormalizerConfig` is convenient when configuration is
created separately from the processing code.

.. doctest::

   >>> from indic_normalizer import Normalizer, NormalizerConfig
   >>> config = NormalizerConfig(lang="en", strip_parentheses=False)
   >>> Normalizer(config=config).normalize("Keep (this note) and 42.")
   'Keep (this note) and forty two.'

When ``config=`` is supplied, that object is authoritative. Do not also pass
``lang`` or keyword options to ``Normalizer``; they are ignored by the current
constructor.

Batch and streaming integration
-------------------------------

The API accepts and returns one string. Keep record boundaries outside the
normalizer:

.. code-block:: python

   from indic_normalizer import Normalizer

   normalizer = Normalizer(lang="en")

   def normalize_records(records):
       for record in records:
           yield {**record, "spoken_text": normalizer.normalize(record["text"])}

For a dataframe or dataset, apply the same ``normalizer.normalize`` method to
the text column. Avoid joining unrelated records before normalization because
some handlers intentionally use nearby context—for example cricket scores and
year-like numbers.

Errors and empty input
----------------------

An empty string returns an empty string. Unsupported ``lang`` and
``number_lang`` values raise :class:`ValueError` during configuration.

.. doctest::

   >>> normalize("")
   ''
   >>> Normalizer(lang="xx")
   Traceback (most recent call last):
   ...
   ValueError: Unsupported lang 'xx'. Supported: ...

The LaTeX reader is deliberately best-effort and never raises for malformed
math; see :ref:`latex-robustness`.

Next steps
----------

Browse :doc:`normalization-cases` for every recognized input class, then tune
the behavior with :doc:`configuration`.
