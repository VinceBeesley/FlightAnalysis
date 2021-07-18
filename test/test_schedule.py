import unittest
from flightanalysis.schedule import p21, Schedule
from flightanalysis.schedule.element import get_rates, LineEl, LoopEl, SnapEl, SpinEl, StallTurnEl
from flightanalysis import Section


class TestSchedule(unittest.TestCase):
    def test_create_template(self):
        sched = p21.scale_distance(170.0)
        out = sched.create_template("left", 30.0, 170.0)

        self.assertIsInstance(out, Section)

        stallturn = p21.manoeuvres[1].get_data(out)
        self.assertEqual(len(stallturn.element.unique()), 10)
    

    def test_match_axis_rate(self):
        
        sec = Section.from_flight("test/P21_new.csv","test/gordano_box.json").subset(110, 200)

        rates = get_rates(sec)

        rate_matched = p21.match_rates(rates)

        for manoeuvre in rate_matched.manoeuvres:
            for i, elm in enumerate(manoeuvre.elements):
                if isinstance(elm, LineEl):
                    self.assertGreater(elm.length, 0.0, "manoeuvre {}, elm {}, length {}".format(manoeuvre.name, i, elm.length))