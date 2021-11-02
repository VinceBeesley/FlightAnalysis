from flightanalysis import Section, Box, Schedule, get_schedule, Categories
from flightanalysis.schedule.elements import get_rates
from flightdata import Flight
from typing import Union, IO
from json import loads, load
from io import open
from warnings import warn
from geometry import GPSPosition, Points, Quaternions, Point, Quaternion, Transformation, Coord
import numpy as np
import pandas as pd


class FCJson:
    def __init__(self, name: str, flight: Flight, box: Box, sec: Section, schedule: Schedule, dists=[]):
        self.name = name
        self.flight = flight
        self.box = box
        self.sec = sec
        self.schedule = schedule
        self._dists = dists

    

    @staticmethod
    def read_box(name, parms):
        return Box.from_points(
            name.partition('_')[0] if '_' in name else 'unknown',
            GPSPosition(float(parms['pilotLat']), float(parms['pilotLng'])),
            GPSPosition(float(parms['centerLat']), float(parms['centerLng']))
        )

    @staticmethod
    def _parse_fc_json(fc_json: dict):
        if not fc_json['version'] == "1.2":
            raise warn("fc_json version {} not supported".format(
                fc_json['version']))

        box = FCJson.read_box(fc_json["name"], fc_json['parameters'])
        flight = Flight.from_fc_json(fc_json)
        sec = Section.from_flight(flight, box)
        
        schedule = get_schedule(*fc_json["parameters"]["schedule"]).share_seperators()
        labelled = schedule.label_from_splitter(sec, fc_json["mans"])
        templates = schedule.create_man_matched_template(labelled)
        
        secs = []
        _dists = []
        for man, templ in zip(schedule.manoeuvres, templates):
            dist, nsec =Section.align(man.get_data(labelled).remove_labels(), templ)
            secs.append(nsec)
            _dists.append(dist)

        #
        aligned = Section.stack([Schedule.get_takeoff(labelled)] + secs)

        return FCJson(fc_json['name'], flight, box, aligned, schedule, _dists)

    

    @staticmethod
    def parse_fc_json(fc_json: Union[IO, str, dict]):
        if isinstance(fc_json, dict):
            fcj = FCJson._parse_fc_json(fc_json)
        elif isinstance(fc_json, str):
            fcj = FCJson._parse_fc_json(loads(fc_json))
        elif hasattr(fc_json, "read"):
            fcj = FCJson._parse_fc_json(load(fc_json))
        else:
            raise TypeError("{} not supported".format(fc_json.__class__))
        return fcj

    def create_json_data(self) -> pd.DataFrame:
        fcd = pd.DataFrame(
            columns=["N", "E", "D", "VN", "VE", "VD", "r",
                     "p", "yw", "wN", "wE", "roll", "pitch", "yaw"]
        )

        fcd["N"], fcd["E"], fcd["D"] = self.sec.x, -self.sec.y, -self.sec.z
        wvels = self.sec.body_to_world(Points.from_pandas(self.sec.bvel))

        fcd["VN"], fcd["VE"], fcd["VD"] = wvels.x, -wvels.y, -wvels.z

        transform = Transformation.from_coords(
            Coord.from_xy(Point(0, 0, 0), Point(1, 0, 0), Point(0, 1, 0)),
            Coord.from_xy(Point(0, 0, 0), Point(1, 0, 0), Point(0, -1, 0))
        )

        eul = transform.quat(Quaternions.from_pandas(self.sec.att)).to_euler()
        ex, ey, ez = eul.x, eul.y, eul.z

        fcd["roll"], fcd["pitch"], fcd["yaw"] = ex, ey, ez

        fcd["r"] = np.degrees(fcd["roll"])
        fcd["p"] = np.degrees(fcd["pitch"])
        fcd["yw"] = np.degrees(fcd["yaw"])

        fcd["wN"] = np.zeros(len(ex))
        fcd["wE"] = np.zeros(len(ex))

        fcd = fcd.reset_index()
        fcd.columns = ["time", "N", "E", "D", "VN", "VE", "VD",
                       "r", "p", "yw", "wN", "wE", "roll", "pitch", "yaw"]
        fcd["time"] = np.int64(fcd["time"] * 1e6)
        return fcd

    def create_fc_json(self):
        fcdata = self.create_json_data()
        fcmans = self.create_json_mans()
        return {
            "version": "1.2",
            "comments": "DO NOT EDIT\n",
            "name": self.name,
            "view": {
                "position": {
                    "x": -120,
                    "y": 130.50000000000003,
                    "z": 264.99999999999983
                },
                "target": {
                    "x": -22,
                    "y": 160,
                    "z": -204
                }
            },
            "parameters": {
                "rotation": -1.5707963267948966,
                "start": int(fcmans.iloc[1].start),
                "stop": int(fcmans.iloc[1].stop),
                "moveEast": 0.0,
                "moveNorth": 0.0,
                "wingspan": 3,
                "modelwingspan": 25,
                "elevate": 0,
                "originLat": 0.0,
                "originLng": 0.0,
                "originAlt": 0.0,
                "pilotLat": "0.0",
                "pilotLng": "0.0",
                "pilotAlt": "0.00",
                "centerLat": "0.0",
                "centerLng": "0.0",
                "centerAlt": "0.00",
                "schedule": [self.schedule.category.name, self.schedule.name]
            },
            "mans": fcmans.to_dict("records"),
            "data": fcdata.to_dict("records")
        }

    def create_json_mans(self) -> pd.DataFrame:
        mans = pd.DataFrame(
            columns=["name", "id", "sp", "wd", "start", "stop", "sel", "background"])
        mans["name"] = ["tkoff"] + [man.name for man in self.schedule.manoeuvres]
        mans["id"] = ["sp_{}".format(i) for i in range(len(self.schedule.manoeuvres) + 1)]
        mans["sp"] = list(range(len(self.schedule.manoeuvres) + 1))
        
        itsecs = self.schedule.get_manoeuvre_data(self.sec, True)

        mans["wd"] = [100 * sec.duration / self.sec.duration for sec in itsecs]
        
        sec = self.sec.data.reset_index()

        mans["start"] = [0] + [sec.loc[sec.manoeuvre==man.uid].index[0] for man in self.schedule.manoeuvres]
        mans["stop"] = [mans["start"][1] + 1] + [sec.loc[sec.manoeuvre==man.uid].index[-1] + 1 for man in self.schedule.manoeuvres]
        
        #mans["stop"] = [sec.index.get_loc[st] for st in mans["stop"]]
        #mans["stop"] = [sec.index.get_loc[st] for st in mans["start"]]
       
        mans["sel"] = np.full(len(self.schedule.manoeuvres) + 1, False)
        mans.loc[1,"sel"] = True
        mans["background"] = np.full(len(self.schedule.manoeuvres) + 1, "")
        #data["mans"][0]["wd"] = data["mans"][0]["wd"] + 0.3
        return mans
