import unittest
from flightanalysis.schedule import p21, Schedule, get_schedule, LineEl
from flightanalysis.schedule.element import get_rates
from flightanalysis import Section
from json import load
from flightanalysis.fc_json import FCJson
from flightdata import Flight


class TestSchedule(unittest.TestCase):
    def test_create_raw_template(self):
        sched = p21.scale_distance(170.0)
        out = sched.create_raw_template("left", 30.0, 170.0)

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

    def test_from_splitter(self):
        with open("test/fc_json.json", 'r') as f:
            fcj = load(f)
        box = FCJson.read_box(fcj["name"], fcj['parameters'])
        flight = Flight.from_fc_json(fcj)
        sec = Section.from_flight(flight, box)

        sched = get_schedule(*fcj["parameters"]["schedule"])
        labelled = sched.label_from_splitter(sec, fcj["mans"])
        self.assertIsInstance(labelled, Section)
        self.assertGreater(sec.duration, labelled.duration)
        self.assertAlmostEqual(sec.duration /10 , labelled.duration / 10, 0)


