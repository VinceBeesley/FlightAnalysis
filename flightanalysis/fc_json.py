from flightanalysis import Section, Box, Schedule
from flightanalysis.schedule import p21, f21
from flightdata import Flight
from typing import IO, Union
from json import loads, load
from io import open
from warnings import warn
from geometry import GPSPosition, Points, Quaternions, Point, Quaternion, Transformation, Coord
import numpy as np
import pandas as pd


class FCJson:
    def __init__(self, name: str, box: Box, sec: Section, schedule: Schedule):
        self.name = name
        self.box = box
        self.sec = sec
        self.schedule = schedule


    @staticmethod
    def _parse_fc_json(fc_json: dict):
        if not fc_json['version'] == "1.2":
            raise warn("fc_json version {} not supported".format(
                fc_json['version']))

        box = Box.from_points(
            fc_json['name'].partition('_')[0] if '_' in fc_json['name'] else 'unknown',
            GPSPosition(fc_json['parameters']['pilotLat'],fc_json['parameters']['pilotLng']),
            GPSPosition(fc_json['parameters']['centerLat'],fc_json['parameters']['centerLng'])
        )
        flight = Flight.from_fc_json(fc_json)
        sec = Section.from_flight(flight, box)
        
        schedule = Schedule() # TODO populate from splitter
        return FCJson(fc_json['name'], box, sec, schedule)

    @staticmethod
    def parse_fc_json(fc_json: Union[str, dict, IO]):
        if isinstance(fc_json, dict):
            return FCJson._parse_fc_json(fc_json)
        elif isinstance(fc_json, str):
            return FCJson._parse_fc_json(loads(fc_json))
        elif isinstance(fc_json, IO):
            with open(fc_json, 'r') as f:
                fcj = FCJson._parse_fc_json(load(f))
            return fcj


    def create_anonymous_json(self):
        fcdata = pd.DataFrame(columns=["N","E","D","VN","VE","VD","r","p","yw","wN","wE","roll","pitch","yaw"])

        fcdata["N"] = self.sec.x
        fcdata["E"] = -self.sec.y
        fcdata["D"] = -self.sec.z

        wvels = self.sec.body_to_world(Points.from_pandas(self.sec.bvel))

        fcdata["VN"] = wvels.x
        fcdata["VE"] = -wvels.y
        fcdata["VD"] = -wvels.z
        transform = Transformation.from_coords(
            Coord.from_xy(Point(0,0,0), Point(1,0,0), Point(0,1,0)),
            Coord.from_xy(Point(0,0,0), Point(1,0,0), Point(0,-1,0))
            )

        eul = transform.quat(Quaternions.from_pandas(self.sec.att)).to_euler()
        ex, ey, ez =  eul.x, eul.y, eul.z

        fcdata["roll"] = ex
        fcdata["pitch"] = ey
        fcdata["yaw"] = ez

        fcdata["r"] = np.degrees(fcdata["roll"])
        fcdata["p"] = np.degrees(fcdata["pitch"])
        fcdata["yw"] = np.degrees(fcdata["yaw"])

        fcdata["wN"] = np.zeros(len(ex))
        fcdata["wE"]= np.zeros(len(ex))

        fcdata = fcdata.reset_index()
        fcdata.columns = ["time", "N","E","D","VN","VE","VD","r","p","yw","wN","wE","roll","pitch","yaw"]
        dout = fcdata.to_dict("records")

        with open(header, "r") as f:
            data = load(f)

        data["data"] = dout

        print("populating splitter")

        self.sec.data.loc[:3.5, ["manoeuvre"]] = "tkoff"

        temp = self.sec.data.reset_index()
        
        for tman, fcman in zip(self.sec.manoeuvre.unique(), data["mans"]):
            fcman["stop"] = int(temp.loc[temp.manoeuvre == tman].index[-1])+1
            fcman["start"] = int(temp.loc[temp.manoeuvre == tman].index[0])
            fcman["wd"]=100*self.sec.get_manoeuvre(tman).duration / self.sec.duration

        data["mans"][0]["wd"] = data["mans"][0]["wd"] + 0.3

        print("saving file")
        with open(file, "w") as f:
            dump(data, f)
