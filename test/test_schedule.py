from flightanalysis.schedule import Schedule, Manoeuvre, Element, Categories
from flightanalysis.schedule.element import ElClass
import unittest
from json import load


with open("schedules/P21.json", 'r') as seqfile:
    schedule = load(seqfile)


class TestElement(unittest.TestCase):
    def test_from_dict(self):
        half_roll = Element.from_dict(schedule["manoeuvres"][0]["elements"][0])
        self.assertEqual(
            half_roll.classification,
            ElClass.LINE
        )

        self.assertEqual(
            half_roll.size,
            0.2
        )


class TestManoeuvre(unittest.TestCase):
    def test_from_dict(self):
        vertical8 = Manoeuvre.from_dict(
            schedule["manoeuvres"][0]
        )
        self.assertEqual(vertical8.name, "vertical 8")
        self.assertEqual(vertical8.k, 3)
        self.assertEqual(vertical8.elements[0].classification, ElClass.LINE)


class TestSchedule(unittest.TestCase):
    def test_from_dict(self):
        p21 = Schedule.from_dict(schedule)
        self.assertEqual(p21.name, "P21")
        self.assertEqual(p21.category, Categories.F3A)
        self.assertEqual(p21.manoeuvres[0].name, "vertical 8")
