import pytest
from pytest import fixture
from flightanalysis.fc_json import parse_fcj
from flightanalysis.flightline import Box
from flightanalysis.state import  State
from flightanalysis.schedule import Schedule, SchedDef
from io import open
from json import load
import numpy as np
import pandas as pd
from flightdata import Flight, Fields


@fixture(scope="session")
def fcjson():
    with open("tests/test_inputs/fcjson/manual_F3A_P23_22_08_23_00000055_1.json", 'r') as f:
        return load(f)

    
def test_parse_fc_json(fcjson):
    st, sd = parse_fcj(fcjson)
    
    assert isinstance(st, State)
    assert isinstance(sd, SchedDef)

    for manoeuvre in sd:
        assert manoeuvre.info.short_name in st.data.manoeuvre.unique()

    data = pd.DataFrame.from_dict(fcjson['data'])
    #assert len(data) == len(st.data)


def test_create_json_mans(fcjson):
    fcj = parse_fcj(fcjson)

    old_mans = pd.DataFrame.from_dict(fcjson["mans"])

    mans = fcj.create_json_mans()
    old_mans["name"] = mans["name"]
    check_cols = ["name", "id", "sp", "wd", "start", "stop"]
    check_frame = mans.loc[:, check_cols]
    old_check_frame = old_mans.loc[:, check_cols]

    pd.testing.assert_frame_equal(check_frame, old_check_frame, check_less_precise=2)
#
#@pytest.mark.skip("expected to fail at the moment")
#def test_create_json_data():
#    fcj = FCJson.parse_fc_json(fcjson)
#    
#    data = fcj.create_json_data()
#    old_data = pd.DataFrame.from_dict(fcjson["data"])
#    
#    data["time"] = (data["time"] + old_data["time"].iloc[0]) / 10
#    old_data["time"] = old_data["time"] / 10
#    pd.testing.assert_frame_equal(data, old_data, check_less_precise=1)
#
#@pytest.mark.skip("")
#def test_create_json(fcjson):
#    fcj = FCJson.parse_fc_json(fcjson)
#
#    fcj2 = FCJson.parse_fc_json(fcj.create_fc_json())
#    fcj3 = FCJson.parse_fc_json(fcj2.create_fc_json())
#
#    pd.testing.assert_frame_equal(fcj2.sec.data, fcj3.sec.data)
#
#
#def test_unique_identifier():
#    with open("tests/test_inputs/manual_F3A_P21_21_09_24_00000052.json", "r") as f:
#        fcj1 = FCJson.parse_fc_json(f)
#
#    _fl = Flight.from_csv("tests/test_inputs/test_log_00000052_flight.csv")
#        
#    assert fcj1.flight.unique_identifier() == _fl.unique_identifier()