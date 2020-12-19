from flightanalysis.schedule import Schedule, Manoeuvre, Element, Elements, Categories
import unittest
from json import load


with open("schedules/P21.json", 'r') as seqfile:
    schedule = load(seqfile)


class TestElement(unittest.TestCase):
    def test_from_dict(self):
        half_roll = Element.from_dict(
            schedule["manoeuvres"][0]["elements"][0]
        )
        self.assertEqual(
            half_roll.classification,
            2
        )

        self.assertEqual(
            half_roll.proportion,
            0.5
        )


class TestManoeuvre(unittest.TestCase):
    def test_from_dict(self):
        vertical8 = Manoeuvre.from_dict(
            schedule["manoeuvres"][0]
        )
        self.assertEqual(vertical8.name, "vertical 8")
        self.assertEqual(vertical8.k, 3)
        self.assertEqual(vertical8.elements[0].classification, Elements.ROLL)
