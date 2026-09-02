Normalization case catalog
==========================

This page describes every semiotic class recognized by the default pipeline.
Examples show exact output from the current implementation. Language-specific
wording follows the rules in :doc:`languages`.

Numbers
-------

Cardinals and years
~~~~~~~~~~~~~~~~~~~

Comma-grouped numbers are cardinals. A bare four-digit number in the default
``year_range`` of 1100–2099 uses the English paired-year style when English is
the resolved number language. A measurement or comma separator forces a
cardinal interpretation.

.. doctest::

   >>> from indic_normalizer import normalize
   >>> normalize("A crowd of 1,947 gathered.")
   'A crowd of one thousand nine hundred and forty seven gathered.'
   >>> normalize("India became independent in 1947.")
   'India became independent in nineteen forty seven.'
   >>> normalize("The rover travelled 1947 km.")
   'The rover travelled one thousand nine hundred and forty seven kilometers.'

Leading zeros and signs
~~~~~~~~~~~~~~~~~~~~~~~

Multi-digit values beginning with zero are treated as codes and read one digit
at a time. ASCII ``+``, ASCII ``-``, and Unicode minus are spoken.

.. doctest::

   >>> normalize("agent 007 reporting")
   'agent zero zero seven reporting'
   >>> normalize("dial 0091 first")
   'dial zero zero nine one first'
   >>> normalize("+42 and −42")
   'plus forty two and minus forty two'

Decimals and percentages
~~~~~~~~~~~~~~~~~~~~~~~~

The integer part is cardinal and the fractional part is digit-wise.

.. doctest::

   >>> normalize("pi is 3.14")
   'pi is three point one four'
   >>> normalize("Growth was 12.5% this year")
   'Growth was twelve point five percent this year'
   >>> normalize("-12% dip")
   'minus twelve percent dip'

Ranges
~~~~~~

Hyphen, en dash, and em dash ranges are accepted when both sides contain at
most four digits. A percent sign or supported unit may follow the range.
Longer hyphenated groups fall through to phone/ID handling.

.. doctest::

   >>> normalize("1939-1945 war")
   'nineteen thirty nine to nineteen forty five war'
   >>> normalize("pages 10-15")
   'pages ten to fifteen'
   >>> normalize("10-15% growth")
   'ten to fifteen percent growth'
   >>> normalize("carry 5-10 kg only")
   'carry five to ten kilograms only'
   >>> normalize("१०-१५ लोग", lang="hi")
   'दस से पंद्रह लोग'

Ratios and scores
~~~~~~~~~~~~~~~~~

Colon pairs that were not recognized as times are read with the language's
range connector.

.. doctest::

   >>> normalize("won 3:2 against them")
   'won three to two against them'
   >>> normalize("a 16:9 screen")
   'a sixteen to nine screen'

Fractions
~~~~~~~~~

English has named forms for ``1/2``, ``1/3``, ``2/3``, ``1/4``, and ``3/4``.
Other English fractions use “over”. Non-English output joins the two
cardinals with that lexicon's connector.

.. doctest::

   >>> normalize("3/4 of the cake")
   'three quarters of the cake'
   >>> normalize("24/7 support")
   'twenty four over seven support'

Ordinals and decades
~~~~~~~~~~~~~~~~~~~~

English ordinal suffixes and supported native suffixes are recognized.
English decade idioms accept four-digit, two-digit, and apostrophe forms.

.. doctest::

   >>> normalize("He came 21st in the 3rd race")
   'He came twenty first in the third race'
   >>> normalize("5वाँ स्थान", lang="hi")
   'पाँचवाँ स्थान'
   >>> normalize("the 1990s and the 80's")
   'the nineteen nineties and the eighties'

Scientific notation
~~~~~~~~~~~~~~~~~~~

Scientific notation uses English wording. Lowercase ``e`` works with integer
or decimal mantissas; uppercase ``E`` requires a decimal mantissa so flight
codes such as ``6E204`` are not mistaken for exponents.

.. doctest::

   >>> normalize("energy 1.5e10 joules")
   'energy one point five times ten to the power ten joules'
   >>> normalize("about 2e-3 seconds")
   'about two times ten to the power minus three seconds'
   >>> normalize("about 1.5E10 joules")
   'about one point five times ten to the power ten joules'

Dates and times
---------------

Numeric dates
~~~~~~~~~~~~~

Supported forms are ``d/m/yyyy``, ``d-m-yyyy``, ``yyyy-mm-dd``, and
``d.m.yyyy``. If day/month order is invalid but month/day is valid, US order is
used. A hopeless slash date is read as separate numbers, not as a fraction.
Dotted dates require a four-digit year.

.. doctest::

   >>> normalize("15/08/1947 was independence")
   'fifteenth August nineteen forty seven was independence'
   >>> normalize("Meeting on 2024-03-05")
   'Meeting on fifth March twenty twenty four'
   >>> normalize("08/15/1947 anniversary")
   'fifteenth August nineteen forty seven anniversary'
   >>> normalize("on 15.8.1947 India")
   'on fifteenth August nineteen forty seven India'
   >>> normalize("code 25/17/2020 file")
   'code twenty five seventeen twenty twenty file'

Textual dates
~~~~~~~~~~~~~

English month names and common abbreviations accept day-month or month-day
order, with an optional four-digit year. Lowercase ambiguous words such as
``may`` and ``march`` require a year.

.. doctest::

   >>> normalize("15 August 1947 dawn")
   'fifteenth August nineteen forty seven dawn'
   >>> normalize("Aug 15, 1947 issue")
   'August fifteenth nineteen forty seven issue'
   >>> normalize("meeting on 5 June")
   'meeting on fifth June'
   >>> normalize("March 2020 lockdown")
   'March twenty twenty lockdown'

Times
~~~~~

Times accept ``HH:MM``, optional seconds, and optional ``am``/``pm`` forms
(including dotted forms). English minutes 01–09 use “oh”; ``:00`` uses
“o'clock” when seconds are absent.

.. doctest::

   >>> normalize("Train at 18:45")
   'Train at eighteen forty five'
   >>> normalize("at 09:05")
   'at nine oh five'
   >>> normalize("at 10:00 am")
   "at ten o'clock am"
   >>> normalize("at 10:30:45 sharp")
   'at ten thirty forty five sharp'

Money and measurements
----------------------

Currency
~~~~~~~~

Prefix tokens are ``₹``, ``$``, ``€``, ``£``, ``Rs``, ``INR``, ``USD``,
``EUR``, and ``GBP`` (case-insensitive for letter forms). Symbols and ``rs``
can also follow the amount. Major and minor units use singular forms where
known; a zero major amount is omitted. Decimal minor units are padded or
truncated to two digits.

.. doctest::

   >>> normalize("It costs ₹1,234.50 only.")
   'It costs one thousand two hundred and thirty four rupees and fifty paise only.'
   >>> normalize("a ₹1 coin")
   'a one rupee coin'
   >>> normalize("₹0.50 candy")
   'fifty paise candy'
   >>> normalize("₹1.01 exactly")
   'one rupee and one paisa exactly'
   >>> normalize("Loss of ₹-500")
   'Loss of minus five hundred rupees'
   >>> normalize("fee 99.50₹ paid")
   'fee ninety nine rupees and fifty paise paid'
   >>> normalize("gave 100 rs. today")
   'gave one hundred rupees today'

Currency scale words
~~~~~~~~~~~~~~~~~~~~

English ``thousand``, ``lakh``, ``crore``, ``million``, ``billion``, and
``trillion`` forms are supported after an amount, along with common native
script forms. Scaled currency does not create a minor-unit reading.

.. doctest::

   >>> normalize("₹5 lakh was sanctioned")
   'five lakh rupees was sanctioned'
   >>> normalize("a USD 50 million deal")
   'a fifty million dollars deal'
   >>> normalize("₹५ लाख की लागत", lang="hi")
   'पाँच लाख रुपये की लागत'

Measurements
~~~~~~~~~~~~

Units are case-sensitive to avoid collisions such as ``5G`` versus five grams.
Recognized tokens are:

``km/h``, ``kmph``, ``kph``, ``°C``, ``°F``, ``°``, ``kg``, ``mg``, ``g``,
``km``, ``cm``, ``mm``, ``ml``, ``GB``, ``MB``, ``KB``, ``TB``, ``hr``,
``min``, ``sec``, ``ft``, ``mAh``, ``kWh``, ``Hz``, ``kHz``, ``MHz``,
``GHz``, ``rpm``, and ``mmHg``.

Ambiguous single-letter units such as ``m``, ``l``, and ``in`` are
intentionally omitted.

.. doctest::

   >>> normalize("5kg and 37.5°C")
   'five kilograms and thirty seven point five degrees celsius'
   >>> normalize("battery 5000 mAh lasts")
   'battery five thousand milliamp hours lasts'
   >>> normalize("wifi at 2.4 GHz")
   'wifi at two point four gigahertz'
   >>> normalize("3000 rpm motor used 1.5 kWh")
   'three thousand revolutions per minute motor used one point five kilowatt hours'

Domain-specific readings
------------------------

Blood pressure
~~~~~~~~~~~~~~

An ``mmHg`` unit or preceding ``BP``/``blood pressure`` trigger selects the
blood-pressure reading. This English-only handler runs before measurements and
fractions.

.. doctest::

   >>> normalize("BP 120/80 noted")
   'BP one hundred and twenty over eighty noted'
   >>> normalize("reading 120/80 mmHg high")
   'reading one hundred and twenty over eighty millimeters of mercury high'

Cricket scores
~~~~~~~~~~~~~~

A two- or three-digit run score followed by one or two wicket digits reads as
“runs for wickets” only when a cricket context word occurs within 60
characters. The wicket value must be at most ten. Without that context, normal
fraction behavior applies.

.. doctest::

   >>> normalize("India 287/5 in 50 overs")
   'India two hundred and eighty seven for five in fifty overs'
   >>> normalize("24/7 support")
   'twenty four over seven support'

Phones, identifiers, and codes
------------------------------

Phone-shaped numbers
~~~~~~~~~~~~~~~~~~~~

Phone numbers are digit-wise. A leading ``+`` qualifies; a contiguous run must
have at least seven digits. Separated numbers require at least ten total digits
and groups of at least three digits. Lists composed only of plausible years are
not phones.

.. doctest::

   >>> normalize("Call +91 98765 43210 now")
   'Call plus nine one nine eight seven six five four three two one zero now'
   >>> normalize("Call 011-2345-6789")
   'Call zero one one two three four five six seven eight nine'
   >>> normalize("Aadhaar 1234 5678 9012")
   'Aadhaar one two three four five six seven eight nine zero one two'
   >>> normalize("years 2020 2021 were tough")
   'years twenty twenty twenty twenty one were tough'

Indian identifiers
~~~~~~~~~~~~~~~~~~

PAN, IFSC, vehicle registration, and context-prefixed six-digit PIN formats
are spelled with individual letters and digits. A bare six-digit quantity is
still a cardinal.

.. doctest::

   >>> normalize("PAN ABCDE1234F given")
   'PAN A B C D E one two three four F given'
   >>> normalize("IFSC SBIN0001234 branch")
   'IFSC S B I N zero zero zero one two three four branch'
   >>> normalize("car KA 01 AB 1234 parked")
   'car K A zero one A B one two three four parked'
   >>> normalize("PIN 560001 area")
   'PIN five six zero zero zero one area'
   >>> normalize("population 560001 rose")
   'population five lakh sixty thousand and one rose'

Alphanumeric text and codes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tokens with one letter/digit transition keep the letter run and verbalize the
number naturally. Tokens with two or more transitions are treated as codes:
letters and digits are spelled individually.

.. doctest::

   >>> normalize("COVID19 and 5G and MP3")
   'COVID nineteen and five G and MP three'
   >>> normalize("seat 32A and vitamin B12")
   'seat thirty two A and vitamin B twelve'
   >>> normalize("code AB123CD here")
   'code A B one two three C D here'
   >>> normalize("flight 6E204 delayed")
   'flight six E two zero four delayed'

Position numbers
~~~~~~~~~~~~~~~~

Three- and four-digit numbers after ``room``, ``page``, ``flight``, ``gate``,
or ``bus`` use English pairing. Exact hundreds stay cardinal. Set
``detect_positions=False`` to disable this handler.

.. doctest::

   >>> normalize("room 225 is ready")
   'room two twenty five is ready'
   >>> normalize("gate 205 closed")
   'gate two oh five closed'
   >>> normalize("flight 6204 landed")
   'flight sixty two oh four landed'
   >>> normalize("room 200 booked")
   'room two hundred booked'
   >>> normalize("room 225 is ready", detect_positions=False)
   'room two hundred and twenty five is ready'

Web addresses and dotted numbers
--------------------------------

Email and URLs
~~~~~~~~~~~~~~

Email addresses and URLs run first so later handlers cannot corrupt them. HTTP
and HTTPS protocols are dropped. Digits are digit-wise in web tokens. Common
punctuation is spoken, including ``dot``, ``slash``, ``at``, ``dash``,
``underscore``, ``question mark``, ``equals``, ``and``, ``hash``, ``plus``,
``colon``, ``percent``, and ``tilde``. Bare domains are recognized for common
TLDs such as ``com``, ``org``, ``net``, ``in``, ``gov``, ``edu``, ``io``,
``ai``, and ``co``.

.. doctest::

   >>> normalize("mail test123@gmail.com now")
   'mail test one two three at gmail dot com now'
   >>> normalize("visit www.example.com/page2 today")
   'visit w w w dot example dot com slash page two today'
   >>> normalize("see https://docs.python.org/3 guide")
   'see docs dot python dot org slash three guide'

Versions and IPv4 addresses
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Numerics with at least two dots are versions unless they form four IPv4
octets in the 0–255 range. Version components are cardinals; IPv4 components
are digit-wise.

.. doctest::

   >>> normalize("Python 3.11.4 released")
   'Python three point eleven point four released'
   >>> normalize("server 192.168.1.1 up")
   'server one nine two dot one six eight dot one dot one up'

Words, symbols, and Roman numerals
----------------------------------

Abbreviations and dotted acronyms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Built-in English abbreviations include titles (``Dr.``, ``Mr.``, ``Mrs.``,
``Ms.``, ``Prof.``), suffixes (``Jr.``, ``Sr.``), organization forms
(``Pvt.``, ``Ltd.``, ``Govt.``, ``Dept.``), and common prose forms
(``approx.``, ``etc.``, ``e.g.``, ``i.e.``, ``vs.``). ``No.`` expands only
before a digit. ``St.`` selects Saint before a capitalized word and Street
otherwise. Hindi ``डॉ.`` is also supported. Matching is intentionally
case-sensitive for forms such as ``Dr.``.

.. doctest::

   >>> normalize("Dr. Sharma met Mr. Rao")
   'Doctor Sharma met Mister Rao'
   >>> normalize("Tata Pvt. Ltd. filed")
   'Tata Private Limited filed'
   >>> normalize("House No. 5 opened")
   'House Number five opened'
   >>> normalize("St. Xavier lives on Main St. nearby")
   'Saint Xavier lives on Main Street nearby'
   >>> normalize("U.S.A. and A.P.J. Kalam")
   'U S A and A P J Kalam'

Standalone symbols
~~~~~~~~~~~~~~~~~~

``&``, ``@``, ``+``, ``=``, ``<``, and ``>`` are spoken when surrounded by
spaces. This boundary keeps punctuation and markup-like text from being
overmatched.

.. doctest::

   >>> normalize("2 + 2 = 4")
   'two plus two equals four'
   >>> normalize("5 < 10 and 20 > 15")
   'five less than ten and twenty greater than fifteen'
   >>> normalize("A & B; meet @ 5")
   'A and B; meet at five'

Roman numerals
~~~~~~~~~~~~~~

Roman numerals are always converted after a safe trigger such as ``Chapter``,
``Part``, ``Class``, ``Section``, ``Volume``, ``Act``, ``Phase``, ``Grade``,
``Book``, ``Unit``, ``Stage``, ``Level``, ``War``, or ``Standard``. Bare Roman
conversion is off by default because ordinary uppercase words can look Roman;
enable it with ``detect_roman=True``.

.. doctest::

   >>> normalize("Chapter IV and Class X")
   'Chapter four and Class ten'
   >>> normalize("item XII")
   'item XII'
   >>> normalize("item XII", detect_roman=True)
   'item twelve'

LaTeX and input artifacts
-------------------------

Math and chemistry have their own complete guide: :doc:`latex`. Parentheses,
tags, escape sequences, control characters, Unicode normalization, and related
options are covered in :ref:`artifact-handling`.
