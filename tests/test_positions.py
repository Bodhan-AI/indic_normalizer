# -*- coding: utf-8 -*-
"""Position numbers after room/page/flight/gate/bus read in pairing style."""

from indic_normalizer import normalize


def test_room():
    assert normalize("room 225 is ready", lang="en") == \
        "room two twenty five is ready"


def test_page():
    assert normalize("page 123 covers it", lang="en") == \
        "page one twenty three covers it"


def test_flight():
    assert normalize("flight 747 landed", lang="en") == \
        "flight seven forty seven landed"


def test_gate_oh_form():
    assert normalize("gate 205 closed", lang="en") == "gate two oh five closed"


def test_bus():
    assert normalize("bus 340 arrived", lang="en") == \
        "bus three forty arrived"


def test_four_digit_flight():
    assert normalize("flights 6204 and 6205", lang="en") == \
        "flights sixty two oh four and six thousand two hundred and five"


# ---- guards ----
def test_round_hundred_stays_cardinal():
    assert normalize("room 200 booked", lang="en") == \
        "room two hundred booked"


def test_no_trigger_word_stays_cardinal():
    assert normalize("225 people came", lang="en") == \
        "two hundred and twenty five people came"


def test_small_number_untouched():
    assert normalize("page 12 read", lang="en") == "page twelve read"


def test_knob_off():
    assert normalize("room 225 is ready", lang="en", detect_positions=False) == \
        "room two hundred and twenty five is ready"


def test_room_no_dot():
    assert normalize("room no. 225 ready", lang="en") == \
        "room number two twenty five ready"


def test_room_no_capitalized():
    # abbrev expands "No." -> "Number" first; position must still pair
    assert normalize("Room No. 225 ready", lang="en") == \
        "Room Number two twenty five ready"


def test_page_number_word():
    assert normalize("page number 123", lang="en") == \
        "page number one twenty three"


def test_page_range_still_range():
    assert normalize("pages 110-115", lang="en") == \
        "pages one hundred and ten to one hundred and fifteen"
