import unittest
from flightanalysis.schedule import p21, Schedule
from flightanalysis import Section


class TestSchedule(unittest.TestCase):
    def test_create_template(self):
        out = p21.create_template("left", 170.0)

        self.assertIsInstance(out, Section)

        stallturn = p21.manoeuvres[1].get_data(out)
        self.assertEqual(len(stallturn.element.unique()), 10)
        