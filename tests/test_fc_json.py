import unittest
from flightanalysis.fc_json import FCJson
from flightanalysis import Box, Section, Schedule
from io import open
from json import load
import numpy as np
import pandas as pd
from flightdata import Flight, Fields
class TestFCJson(unittest.TestCase):
    def setUp(self):
        with open("tests/fc_json.json", 'r') as f:
            self.json = load(f)
    def test_parse_fc_json(self):
        fcj = FCJson.parse_fc_json(self.json)

        self.assertIsInstance(fcj.flight, Flight)
        self.assertIsInstance(fcj.box, Box)
        self.assertIsInstance(fcj.sec, Section)
        self.assertIsInstance(fcj.schedule, Schedule)
        self.assertIn(0, fcj.sec.data.manoeuvre.unique())

        for manoeuvre in fcj.schedule.manoeuvres:
            self.assertIn(manoeuvre.uid, fcj.sec.data.manoeuvre.unique(), "{} data not found in section".format(manoeuvre.name))

        data = pd.DataFrame.from_dict(self.json['data'])
        self.assertEqual(len(data), len(fcj.sec.data))


    def test_create_json_mans(self):
        fcj = FCJson.parse_fc_json(self.json)

        old_mans = pd.DataFrame.from_dict(self.json["mans"])

        mans = fcj.create_json_mans()
        old_mans["name"] = mans["name"]
        check_frame = mans.loc[:-1, ["name", "id", "sp", "wd", "start", "stop", "background"]]
        old_check_frame = old_mans.loc[:-1, ["name", "id", "sp", "wd", "start", "stop", "background"]]

        pd.testing.assert_frame_equal(check_frame, old_check_frame, check_less_precise=2)
    
    @unittest.skip("expected to fail at the moment")
    def test_create_json_data(self):
        fcj = FCJson.parse_fc_json(self.json)
        
        data = fcj.create_json_data()
        old_data = pd.DataFrame.from_dict(self.json["data"])
        
        data["time"] = (data["time"] + old_data["time"].iloc[0]) / 10
        old_data["time"] = old_data["time"] / 10
        pd.testing.assert_frame_equal(data, old_data, check_less_precise=1)

    @unittest.skip("")
    def test_create_json(self):
        fcj = FCJson.parse_fc_json(self.json)

        fcj2 = FCJson.parse_fc_json(fcj.create_fc_json())
        fcj3 = FCJson.parse_fc_json(fcj2.create_fc_json())

        pd.testing.assert_frame_equal(fcj2.sec.data, fcj3.sec.data)


    def test_unique_identifier(self):
        with open("tests/test_inputs/manual_F3A_P21_21_09_24_00000052.json", "r") as f:
            fcj1 = FCJson.parse_fc_json(f)

        
        _fl = Flight.from_csv("tests/test_inputs/test_log_00000052_flight.csv")
         
        assert fcj1.flight.unique_identifier() == _fl.unique_identifier()