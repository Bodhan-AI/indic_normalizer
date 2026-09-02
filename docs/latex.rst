LaTeX, math, and chemistry
==========================

The bundled LaTeX-to-speech engine is pure Python, has no runtime dependencies,
and produces English speech. Use :func:`indic_normalizer.latex_to_speech` for a
raw expression without delimiters, or :func:`indic_normalizer.normalize` to
detect supported spans inside prose.

.. doctest::

   >>> from indic_normalizer import latex_to_speech, normalize
   >>> latex_to_speech(r"\int_0^1 x^2\,dx")
   'integral from zero to one of x squared d x'
   >>> normalize(r"The root is $x^2+1$.")
   'The root is x squared plus one.'

Verbosity
---------

``natural`` is the default and uses familiar forms such as “squared” and a
plain “over”. ``explicit`` adds structural wording where it helps disambiguate
speech.

.. doctest::

   >>> latex_to_speech(r"x^2", verbosity="natural")
   'x squared'
   >>> latex_to_speech(r"x^2", verbosity="explicit")
   'x to the power of two'
   >>> latex_to_speech(r"\frac{a}{b}", verbosity="explicit")
   'the fraction a over b'

Configure embedded conversion with ``latex_verbosity``. Set ``latex=False``
to skip span conversion, but note that raw markup is then still exposed to
later number and symbol handlers; disabling LaTeX is not an escaping mechanism.

Detected spans
--------------

The mixed-text pipeline detects all of these forms:

* inline ``$...$``;
* display ``$$...$$``;
* ``\(...\)`` and ``\[...\]``;
* ``\begin{environment}...\end{environment}``;
* chemistry ``\ce{...}``.

.. doctest::

   >>> normalize(r"See $$\frac{1}{2}$$ now.")
   'See one half now.'
   >>> normalize(r"See \[E=mc^2\] now.")
   'See E equals m c squared now.'
   >>> normalize(r"Take \(\alpha\) please.")
   'Take alpha please.'
   >>> normalize(r"Water is \ce{H2O}.")
   'Water is H two O.'

Dollar spans are gated to avoid stealing currency. ``$5`` is a dollar amount;
a short variable or math-shaped span is LaTeX.

.. doctest::

   >>> normalize("I paid $5 and she paid $10.")
   'I paid five dollars and she paid ten dollars.'
   >>> normalize("let $n$ be even.")
   'let n be even.'

Scripts, fractions, and roots
-----------------------------

Superscripts support squared, cubed, negative, simple, and grouped expression
readings. Subscripts use “sub” in natural mode and “subscript” in explicit
mode. Fraction commands include ``frac``, ``dfrac``, ``tfrac``, and ``cfrac``;
common simple fractions receive named readings. Square, cube, and indexed roots
are supported.

.. doctest::

   >>> latex_to_speech(r"e^{x_i+2}")
   'e to the quantity x sub i plus two'
   >>> latex_to_speech(r"x_1")
   'x sub one'
   >>> latex_to_speech(r"\frac{3}{4}")
   'three quarters'
   >>> latex_to_speech(r"\sqrt[3]{8}")
   'cube root of eight'

Big operators
-------------

Supported big operators are integrals (``int``, ``iint``, ``iiint``,
``oint``), ``sum``, ``prod``, ``coprod``, ``bigcup``, ``bigcap``,
``bigoplus``, ``bigotimes``, ``bigvee``, ``bigwedge``, ``lim``, ``limsup``,
and ``liminf``. Upper and lower scripts form ranges; a lower script alone is
read as a region (“over” or “around”) where appropriate.

.. doctest::

   >>> latex_to_speech(r"\sum_{i=1}^{n} i")
   'sum from i equals one to n of i'
   >>> latex_to_speech(r"\lim_{x\to 0}")
   'limit as x approaches zero'
   >>> latex_to_speech(r"\sum_j x_j")
   'sum over j of x sub j'
   >>> latex_to_speech(r"\oint_C E \cdot dl")
   'contour integral around C of E times d l'

Symbols and relations
---------------------

The symbol vocabulary includes:

* lowercase and standard uppercase Greek commands, including common variant
  forms such as ``varepsilon``, ``vartheta``, ``varphi``, and ``varrho``;
* comparisons and set relations such as ``neq``, ``leq``, ``geq``, ``approx``,
  ``equiv``, ``propto``, ``in``, ``notin``, ``subset``, ``subseteq``,
  ``supset``, ``supseteq``, ``cup``, ``cap``, ``perp``, and ``parallel``;
* arithmetic and logical operators such as ``pm``, ``mp``, ``times``, ``cdot``,
  ``div``, ``oplus``, ``otimes``, ``wedge``, and ``vee``;
* arrows and logic such as ``to``, ``rightarrow``, ``Rightarrow``, ``implies``,
  ``leftarrow``, ``iff``, ``mapsto``, ``uparrow``, and ``downarrow``;
* common symbols such as ``infty``, ``partial``, ``nabla``, ``forall``,
  ``exists``, ``emptyset``, ``hbar``, ``Re``, ``Im``, and ``degree``.

.. doctest::

   >>> latex_to_speech(r"\alpha+\beta")
   'alpha plus beta'
   >>> latex_to_speech(r"a \leq b")
   'a less than or equal to b'
   >>> latex_to_speech(r"p \Rightarrow q")
   'p implies q'
   >>> latex_to_speech(r"\forall x \in A")
   'for all x in A'

Functions, accents, and delimiters
----------------------------------

Named functions include trigonometric and hyperbolic functions and their
inverses, logarithms, ``exp``, ``det``, ``dim``, ``ker``, ``gcd``, ``arg``,
``max``, ``min``, ``sup``, ``inf``, and ``Pr``. Function application is
spoken with “of”.

Accents include vectors/arrows, hats, bars, dots, tildes, checks, breves,
acute/grave marks, rings, and underlines. Absolute values, norms, parentheses,
and ``left``/``right`` delimiters are recognized.

.. doctest::

   >>> latex_to_speech(r"\sin^2 x")
   'sine squared of x'
   >>> latex_to_speech(r"\vec{F}=m\vec{a}")
   'vector F equals m vector a'
   >>> latex_to_speech(r"|x|")
   'absolute value of x'
   >>> latex_to_speech(r"\|x\|")
   'norm of x'
   >>> latex_to_speech(r"f(x)")
   'f of x'

Numbers and text wrappers
-------------------------

Integers, decimals, and degrees are verbalized. Text/style wrappers—including
``text``, ``textrm``, ``textbf``, ``textit``, ``mathrm``, ``mathbf``,
``mathcal``, ``mathbb``, ``operatorname``, and related common wrappers—speak
their content without the formatting command. Spacing macros are dropped.

.. doctest::

   >>> latex_to_speech(r"3.14")
   'three point one four'
   >>> latex_to_speech(r"90^\circ")
   'ninety degrees'
   >>> latex_to_speech(r"\text{if } x>0")
   'if x greater than zero'

Matrices and equation environments
----------------------------------

Matrix families (``matrix``, ``pmatrix``, ``bmatrix``, ``Bmatrix``,
``smallmatrix``, and ``array``) announce rows. ``vmatrix`` and ``Vmatrix`` are
read as determinants. ``cases``/``dcases`` separate cases. Alignment and
equation families—including ``align``, ``aligned``, ``equation``, ``split``,
``gather``, ``multline``, ``eqnarray``, ``flalign``, and ``displaymath``—speak
each row as a sentence.

.. doctest::

   >>> latex_to_speech(r"\begin{pmatrix}1&2\\3&4\end{pmatrix}")
   'matrix, row one one two, row two three four'
   >>> latex_to_speech(r"\begin{aligned}a &= b \\ c &= d\end{aligned}")
   'a equals b. c equals d'

Chemistry
---------

``\ce{...}`` supports coefficients, element letters, counts, reaction and
equilibrium arrows, charges, common physical-state suffixes, and grouped
formulae. It spells element symbols letter by letter; it does not attempt to
pronounce element names.

.. doctest::

   >>> latex_to_speech(r"\ce{2H2 + O2 -> 2H2O}")
   'two H two plus O two yields two H two O'
   >>> latex_to_speech(r"\ce{SO4^2-}")
   'S O four two minus'
   >>> latex_to_speech(r"\ce{NaCl(aq)}")
   'N a C l aqueous'

Lower-level helpers in :mod:`indic_normalizer.latex.chemistry` can classify
and read a bare formula, but the main mixed-text normalizer only auto-detects
chemistry inside ``\ce{...}``.

.. _latex-robustness:

Robustness and limitations
--------------------------

The engine is a speech-oriented subset, not a TeX renderer. Unknown commands
are dropped while readable operands survive. Malformed input degrades to a
markup-stripped string, and public conversion functions return a string rather
than raising.

.. doctest::

   >>> latex_to_speech(r"\unknown x + 1")
   'x plus one'
   >>> isinstance(latex_to_speech(r"\frac{1}{"), str)
   True
   >>> latex_to_speech(None)
   ''

The final scrub removes LaTeX markup characters from spoken output. Use the
normalizer's tag-preservation options—not raw LaTeX—to retain non-spoken
metadata.
