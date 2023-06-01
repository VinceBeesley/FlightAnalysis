from geometry import Transformation, Coord, Quaternion, Point
from flightanalysis.state import State
import numpy as np
import pandas as pd



def _create_json_data(self: State) -> pd.DataFrame:
    fcd = pd.DataFrame(columns=["N", "E", "D", "VN", "VE", "VD", "r", "p", "yw", "wN", "wE", "roll", "pitch", "yaw"])
    fcd["N"], fcd["E"], fcd["D"] = self.x, -self.y, -self.z
    wvels = self.body_to_world(Point(self.vel))
    fcd["VN"], fcd["VE"], fcd["VD"] = wvels.x, -wvels.y, -wvels.z

    transform = Transformation.from_coords(
        Coord.from_xy(Point(0, 0, 0), Point(1, 0, 0), Point(0, 1, 0)),
        Coord.from_xy(Point(0, 0, 0), Point(1, 0, 0), Point(0, -1, 0))
    )
    eul = transform.rotate(Quaternion(self.att)).to_euler()
    ex, ey, ez = eul.x, eul.y, eul.z
    fcd["roll"], fcd["pitch"], fcd["yaw"] = ex, ey, ez

    fcd["r"] = np.degrees(fcd["roll"])
    fcd["p"] = np.degrees(fcd["pitch"])
    fcd["yw"] = np.degrees(fcd["yaw"])

    fcd["wN"] = np.zeros(len(ex))
    fcd["wE"] = np.zeros(len(ex))

    fcd = fcd.reset_index()
    fcd.columns = ["time", "N", "E", "D", "VN", "VE", "VD", "r", "p", "yw", "wN", "wE", "roll", "pitch", "yaw"]
    fcd["time"] = np.int64(fcd["time"] * 1e6)
    return fcd


def _create_json_mans(self: State, sdef) -> pd.DataFrame:
    mans = pd.DataFrame(columns=["name", "id", "sp", "wd", "start", "stop", "sel", "background", "k"])

    mans["name"] = ["tkoff"] + [man.info.short_name for man in sdef]
    mans["k"] = [0] + [man.info.k for man in sdef]
    mans["id"] = ["sp_{}".format(i) for i in range(len(sdef.data)+1)]

    mans["sp"] = list(range(len(sdef.data) + 1))
    
    itsecs = [self.get_manoeuvre(m.info.short_name) for m in sdef] 

    mans["wd"] = [0.0] + [100 * st.duration / self.duration for st in itsecs]
    
    dat = self.data.reset_index(drop=True)

    mans["start"] = [0] + [dat.loc[dat.manoeuvre==man.info.short_name].index[0] for man in sdef]

    mans["stop"] = [mans["start"][1] + 1] + [dat.loc[dat.manoeuvre==man.info.short_name].index[-1] + 1 for man in sdef]
        
    mans["sel"] = np.full(len(sdef.data) + 1, False)
    mans.loc[1,"sel"] = True
    mans["background"] = np.full(len(sdef.data) + 1, "")

    return mans


def create_fc_json(self: State, sdef, schedule_name: str, schedule_category: str="F3A"):
    fcdata = _create_json_data(self)
    fcmans = _create_json_mans(self, sdef)
    return {
        "version": "1.3",
        "comments": "DO NOT EDIT\n",
        "name": schedule_name,
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
            "schedule": [schedule_category, schedule_name]
        },
        "scored": False,
        "scores": [0,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,600],
        "mans": fcmans.to_dict("records"),
        "data": fcdata.to_dict("records")
    }
