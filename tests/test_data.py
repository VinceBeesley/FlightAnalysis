from flightanalysis.data import *


def test_jsons():
    assert "p23" in jsons


def test_get_schedule_definition():
    p23def = get_schedule_definition("P23")

    assert p23def[0].info.name == "Top Hat"