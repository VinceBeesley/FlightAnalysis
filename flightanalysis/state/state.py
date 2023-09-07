from __future__ import annotations
from typing import Union, List
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from pandas.api.types import is_list_like
from geometry import Point, Quaternion, Transformation, PX, PY, PZ, P0, Q0, Coord
from flightanalysis import Table, Constructs, SVar, Time, FlightLine, Box, Flow, Environment

from warnings import warn
try:
    from scipy.spatial.distance import euclidean
except ImportError as ex:
    pass
try:
    from fastdtw import fastdtw
except ImportError as ex:
    pass


class State(Table):
    constructs = Table.constructs + Constructs([
        SVar("pos", Point,       ["x", "y", "z"]           , lambda self: P0(len(self))       ), 
        SVar("att", Quaternion,  ["rw", "rx", "ry", "rz"]  , lambda self : Q0(len(self))       ),
        SVar("vel", Point,       ["u", "v", "w"]           , lambda st: P0() if len(st)==1 else st.att.inverse().transform_point(st.pos.diff(st.dt))  ),
        SVar("rvel", Point,       ["p", "q", "r"]           , lambda st: P0() if len(st)==1 else st.att.body_diff(st.dt).remove_outliers(3)  ),
        SVar("acc", Point,       ["du", "dv", "dw"]        , lambda st : P0() if len(st)==1 else st.att.inverse().transform_point(st.att.transform_point(st.vel).diff(st.dt) + PZ(9.81, len(st)))),
        SVar("racc", Point,       ["dp", "dq", "dr"]        , lambda st: P0() if len(st)==1 else st.rvel.diff(st.dt)),
    ])
    _construct_freq = 30

    @property
    def transform(self):
        return Transformation.build(self.pos, self.att)
    
    @property
    def back_transform(self):
        return Transformation(-self.pos, self.att.inverse())
     
    @staticmethod
    def from_transform(transform: Transformation, **kwargs):
        if not "time" in kwargs: 
            kwargs["time"] = Time.from_t(np.linspace(0, State._construct_freq*len(transform), len(transform)))
        return State.from_constructs(pos=transform.p, att=transform.q, **kwargs)

    def body_to_world(self, pin: Point, rotation_only=False) -> Point:
        """Rotate a point in the body frame to a point in the data frame

        Args:
            pin (Point): Point on the aircraft

        Returns:
            Point: Point in the world
        """
        if rotation_only:
            return self.transform.rotate(pin)
        else:
            return self.transform.point(pin)

    def world_to_body(self, pin: Point, rotation_only=False) -> Point:
        if rotation_only:
            self.back_transform.rotate(pin)
        else:
            return self.back_transform.point(pin)

    def fill(self, time: Time) -> State:
        vel = self.vel.tile(len(time))   
        rvel = self.rvel.tile(len(time))
        att = self.att.body_rotate(rvel * time.t)
        #pos = Point.concatenate([P0(), (att[1:].transform_point(vel[1:]) * time.dt[1:]).cumsum()]) + istate.pos
        #TODO improve the position accuracy by extrapolating the points round a circle
        pos = (att.transform_point(vel) * time.dt).cumsum() + self.pos
        return State.from_constructs(time,pos, att, vel, rvel)

    def extrapolate(self: State, duration: float) -> State:
        """extrapolate the input state, currently ignores input accelerations

        Args:
            istate (State): initial state of length 1
            duration (float): duration of extrapolation in seconds

        Returns:
            State: state projected forwards
        """

        npoints = np.max([int(np.ceil(duration / self.dt[0])), 3])

        time = Time.from_t(np.linspace(0,duration, npoints))

        return self.fill(time)

    @staticmethod
    def from_csv(filename) -> State:
        df = pd.read_csv(filename)

        if "time_index" in df.columns: # This is for back compatability with old csv files where time column was labelled differently
            if "t" in df.columns:
                df.drop("time_index", axis=1)
            else:
                df = df.rename({"time_index":"t"}, axis=1)
        return State(df.set_index("t", drop=False))

    @staticmethod
    def from_flight(flight, box:Union[FlightLine, Box, str] = None) -> State:
        from flightdata import Flight, Fields
        if isinstance(flight, str):
            flight = {
                ".csv": Flight.from_csv,
                ".BIN": Flight.from_log
            }[Path(flight).suffix](flight)
        if box is None:
            box = Box.from_initial(flight)
        if isinstance(box, FlightLine):
            return State._from_flight(flight, box)
        if isinstance(box, Box):
            return State._from_flight(flight, FlightLine.from_box(box, flight.origin))
        if isinstance(box, str):
            box = Box.from_json(box)
            return State._from_flight(flight, FlightLine.from_box(box, flight.origin))
        raise NotImplementedError()

    @staticmethod
    def _from_flight(flight, flightline: FlightLine) -> State:
        from flightdata import Fields
        """Read position and attitude directly from the log(after transforming to flightline)"""
        time = Time.from_t(np.array(flight.data.time_flight))
        pos = flightline.transform_from.point(Point(flight.read_fields(Fields.POSITION)))
        qs = flight.read_fields(Fields.QUATERNION)
        
        if not pd.isna(qs).all().all():  # for back compatibility with old csv files
            att = flightline.transform_from.rotate(
                Quaternion(flight.read_fields(Fields.QUATERNION))
            )
        else:
            att = flightline.transform_from.rotate(
                Quaternion.from_euler(Point(
                    flight.read_numpy(Fields.ATTITUDE).T
                )))

        
        vel = att.inverse().transform_point(
            flightline.transform_from.rotate(
                Point(flight.read_numpy(Fields.VELOCITY).T)
            )
        )
        accs=flight.read_fields(Fields.ACCELERATION)
        acc = Point(accs) if not pd.isna(accs).all().all() else None

        rvels=flight.read_fields(Fields.AXISRATE)
        rvel = Point(rvels) if not pd.isna(rvels).all().all() else None
        
        return State.from_constructs(time, pos, att, vel, rvel, acc)

    @staticmethod
    def stack(sections: list) -> State:
        """stack a list of States on top of each other. last row of each is replaced with first row of the next, 
            indexes are offset so they are sequential

        Args:
            States (List[State]): list of States to stacked

        Returns:
            State: the resulting State
        """
        # first build list of index offsets, to be added to each dataframe
        offsets = [0] + [sec.duration for sec in sections[:-1]]
        offsets = np.cumsum(offsets)

        # The sections to be stacked need their last row removed, as the first row of the next replaces it
        dfs = [section.data.iloc[:-1] for section in sections[:-1]] + \
            [sections[-1].data.copy()]

        # offset the df indexes
        for df, offset in zip(dfs, offsets):
            df.index = np.array(df.index) - df.index[0] + offset
        combo = pd.concat(dfs)
        combo.index.name = "t"

        combo["t"] = combo.index

        return State(combo)



    @staticmethod
    def align(flown: State, template: State, radius=5, mirror=True, white=False, weights = Point(1,1,1)) -> State:
        """Perform a temporal alignment between two sections. return the flown section with labels 
        copied from the template along the warped path

        Args:
            flown (Section): An un-labelled Section
            template (Section): A labelled Section
            radius (int, optional): The DTW search radius. Defaults to 5.
            whiten (bool, optional): Whether to whiten the data before performing the alignment. Defaults to False.

        """
        
        if white:
            warnings.filterwarnings("ignore", message="Some columns have standard deviation zero. ")

        def get_brv(brv):
            if mirror:
                brv.data[:,0] = abs(brv.data[:,0])
                brv.data[:,2] = abs(brv.data[:,2])

            if white:
                brv = brv.whiten()

            return brv * weights

        fl = get_brv(flown.rvel)

        tp = get_brv(template.rvel)

        distance, path = fastdtw(
            tp.data,
            fl.data,
            radius=radius,
            dist=euclidean
        )

        return distance, State.copy_labels(template, flown, path)

    @staticmethod
    def copy_labels(template: State, flown: State, path=None) -> State:
        """Copy the labels from a template section to a flown section along the index warping path

        Args:
            template (Section): A labelled section
            flown (Section): An unlabelled section
            path (List): A list of lists containing index pairs from template to flown

        Returns:
            Section: a labelled section
        """

        flown = flown.remove_labels()

        keys = [k for k in ["manoeuvre", "element", "sub_element"] if k in template.data.columns]
        if path is None:
            return State(
                pd.concat(
                    [flown.data.reset_index(drop=True), template.data.loc[:,keys].reset_index(drop=True)], 
                    axis=1
                ).set_index("t", drop=False)
            )
        else:
            mans = pd.DataFrame(path, columns=["template", "flight"]).set_index("template").join(
                    template.data.reset_index(drop=True).loc[:, keys]
                ).groupby(['flight']).last().reset_index().set_index("flight")

            return State(flown.data.reset_index(drop=True).join(mans).set_index("t", drop=False))


    def splitter_labels(self: State, mans: List[dict]) -> State:
            """label the manoeuvres in a State based on the flight coach splitter information

            TODO this assumes the state only contains the dataset contained in the json

            Args:
                mans (list): the mans field of a flight coach json

            Returns:
                State: State with labelled manoeuvres
            """

            takeoff = self.data.iloc[0:int(mans[0]["stop"])+1]

            labels = [mans[0]["name"]]
            labelled = [State(takeoff).label(manoeuvre=labels[0])]
            
            for split_man in mans[1:]:
                
                while split_man["name"] in labels:
                    split_man["name"] = split_man["name"] + "2"

                labelled.append(
                    State(
                        self.data.iloc[int(split_man["start"]):int(split_man["stop"])+1]
                    ).label(manoeuvre=split_man["name"])
                )
                labels.append(split_man["name"])

            return State.stack(labelled)


    def get_subset(self: State, mans: Union[list, slice], col="manoeuvre"):
        selectors = self.data.loc[:,col].unique()
        if isinstance(mans, slice):
            mans = selectors[mans]

        if not is_list_like(mans):
            mans = [mans]
        
        if not all(isinstance(m, str) for m in mans):
            mans = [m.uid if m.__class__.__name__ == "Manoeuvre" else m for m in mans]
            mans = [m.uid if m.__class__.__bases__[0].__name__ == "El" else m for m in mans]    
            mans = [selectors[m] if isinstance(m, int) else m for m in mans]
            
        assert all(isinstance(m, str) for m in mans)

        return State(self.data.loc[self.data.loc[:, col].isin(mans)])

    def get_manoeuvre(self: State, manoeuvre: Union[str, list, int]):
        return self.get_subset(manoeuvre, "manoeuvre")

    def get_element(self: State, element: Union[str, list, int]):
        return self.get_subset(element, "element") 

    def get_man_or_el(self: State, el: str):
        if el in self.data.element.unique():
            return self.get_element([el])
        elif el in self.data.manoeuvre.unique():
            return self.get_manoeuvre([el])
        
    def get_meid(self: State, manid: int, elid: int=None):
        st = self.get_manoeuvre(manid)
        if not elid is None:
            return st.get_element(elid)
        else:
            return st

    def convert_state(self: State, r: Point) -> State:
        att = self.att.body_rotate(r)
        q =  att.inverse() * self.att
        return State.from_constructs(
            time=self.time,
            pos=self.pos,
            att=att,
            vel=q.transform_point(self.vel),
            rvel=q.transform_point(self.rvel),
            acc=q.transform_point(self.acc),
            racc=q.transform_point(self.racc),
        )

    def to_judging(self: State) -> State:
        """This rotates the body so the x axis is in the velocity vector"""
        return self.body_to_wind()

    def body_to_stability(self: State, flow: Flow=None) -> State:
        if not flow:
            env = Environment.from_constructs(self.time)
            flow = Flow.build(self, env)
        return self.convert_state(-Point(0,1,0) * flow.alpha)    

    def stability_to_wind(self: State, flow: Flow=None) -> State:
        if not flow:
            env = Environment.from_constructs(self.time)
            flow = Flow.build(self, env)
        return self.convert_state(Point(0,0,1) * flow.beta)

    def body_to_wind(self: State, flow: Flow=None) -> State:
        return self.body_to_stability(flow).stability_to_wind(flow)


    def judging_to_wind(self: State, env: Environment) -> State:
        """I think the correct way to go from judging axis to wind axis is to do a yaw rotation then a pitch 
        rotation, as this keeps the wing vector in the judging axis XY plane.

        Args:
            self (State): the judging axis data
            env (Environment): the environment

        Returns:
            State: the wind axis data
        """
        # the local wind vector in the judging frame:
        jwind = self.att.inverse().transform_point(env.wind)  

        # the yaw rotation required to align the xz plane with the local wind vector:
        yaw_rotation = (jwind + self.vel).angles(
            self.att.inverse().transform_point(PX())
        ) * Point(0,0,1) 

        #transform the data by this yaw rotation:
        int_axis = self.convert_state(yaw_rotation)

        #the local wind vector in the intermediate frame:
        intwind = int_axis.att.inverse().transform_point(env.wind) 

        #the pitch rotation required to align the xy plane with the local wind vector:
        pitch_rotation = (intwind + int_axis.vel).angles(
            int_axis.att.inverse().transform_point(PX())
        ) * Point(0,1,0)

        #transform by this pitch rotation to get the wind axis state
        return int_axis.convert_state(pitch_rotation)

    def wind_to_body(self: State, flow: Flow) -> State:

        stability_axis = self.convert_state(-Point(0,0,1) * flow.beta)
        body_axis = stability_axis.convert_state(Point(0,1,0) * flow.alpha)

        return body_axis

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
        fcdata = self._create_json_data()
        fcmans = self._create_json_mans(sdef)
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


    def direction(self):
        """returns 1 for going right, -1 for going left"""
        return np.sign(self.att.transform_point(Point(1, 0, 0)).x)
        
    def inverted(self):
        return np.sign(self.att.transform_point(Point(0, 0, 1)).z) > 0

    def upright(self):
        return not self.inverted()

    def judging_itrans(self: State, template_itrans: Transformation):
        """The judging initial transform has its X axis in the states velocity vector and
        its wings aligned with the template"""
        return Transformation(
            self.pos[0], 
            Quaternion.from_rotation_matrix(
                Coord.from_xy(
                    P0(), 
                    self.att[0].transform_point(self.vel[0]),
                    template_itrans.att.transform_point(PY()) 
                ).rotation_matrix()
            ).inverse()
        )


    def move(self: State, transform: Transformation) -> State:
        return State.copy_labels(self, State.from_constructs(
            time=self.time,
            pos=transform.point(self.pos),
            att=transform.rotate(self.att),
            vel=self.vel,
            rvel=self.rvel,
            acc=self.acc,
            racc=self.racc,
        ))

    def move_back(self:State, transform:Transformation) -> State:
        self = self.move(Transformation(-transform.pos, Q0()))
        return self.move(Transformation(P0(), transform.att.inverse()))


    def relocate(self:State, start_pos: Point) -> State:
        offset = start_pos - self.pos[0]
        return self.move(Transformation(offset, Q0()))

    def superimpose_angles(self: State, angles: Point, reference:str="body"): 
        assert reference in ["body", "world"]
        sec = State.copy_labels(
            self, 
            State.from_constructs(
                self.time,
                self.pos,
                self.att.rotate(angles) if reference=="world" else self.att.body_rotate(angles)
            )
        ) 

        #if "sub_element" in self.data.columns:
        #   sec = sec.append_columns(self.data["sub_element"])
        return sec


    def superimpose_rotation(self: State, axis: Point, angle: float, reference:str="body"):
        """Generate a new section, identical to self, but with a continous rotation integrated
        """
        t = self.time.t - self.time.t[0]
        rate = angle / self.time.t[-1]
        superimposed_rotation = t * rate

        angles = axis.unit().tile(len(t)) * superimposed_rotation

        return self.superimpose_angles(angles, reference)



    def superimpose_roll(self: State, angle: float) -> State:
        """Generate a new section, identical to self, but with a continous roll integrated

        Args:
            angle (float): the amount of roll to integrate
        """
        return self.superimpose_rotation(PX(), angle)


    def smooth_rotation(self: State, axis: Point, angle: float, reference:str="body", w: float=0.25, w2=0.1):
        """Accelerate for acc_prop * t, flat rate for middle, slow down for acc_prop * t.

        Args:
            axis (Point): Axis to rotate around.
            angle (float): angle to rotate.
            reference (selfr, optional): rotate about body or world. Defaults to "body".
            acc_prop (float, optional): proportion of total rotation to be accelerating for. Defaults to 0.1.
        """

        t = self.time.t - self.time.t[0]

        T = t[-1]

        V = angle / (T*(1-0.5*w-0.5*w2))  # The maximum rate

        #between t=0 and t=wT
        x = t[t<=w*T]
        angles_0 = (V * x**2) / (2 * w * T)    

        #between t=wT and t=T(1-w)
        y=t[(t>w*T) & (t<=(T-w2*T))]
        angles_1 = V * y - V * w * T / 2
        
        #between t=T(1-w2) and t=T
        z = t[t>(T-w2*T)] - T + w2*T
        angles_2 = V*z - V * z **2 / (2*w2*T) + V*T - V * w2 * T  - 0.5*V*w*T

        angles = Point.full(axis.unit(), len(t)) * np.concatenate([angles_0, angles_1, angles_2])

        return self.superimpose_angles(angles, reference)

    def shift_labels(self, col, elname, offset, allow_label_loss=True) -> State:
        
        new_t = self.label_ts("element")[elname][1] +  offset
        
        odata = self.data.copy()

        elnames = list(odata[col].unique())
        elid = elnames.index(elname)
        elt = odata.loc[odata[col] == elname].index.to_numpy()       
        nelt = self.data.loc[odata[col] == elnames[elid+1]].index.to_numpy()
        
        if allow_label_loss:
            new_t = max(new_t, self.data.index[0])
            new_t = min(new_t, self.data.index[-1])
        else:
            new_t = max(new_t, elt[0])
            new_t = min(new_t, nelt[-1])

        if elt[-1] > new_t:    
            odata.loc[new_t:nelt[-1], col] = elnames[elid+1]
        else:
            odata.loc[elt[0]:new_t, col] = elname
        
        return State(odata)
    
    def label_ts(self, col, t=False):
        labels = list(self.data[col].unique())
        rng = lambda arr: (min(arr), max(arr))
        if t:
            return {lab: rng(self.data.loc[self.data[col]==lab].t.to_numpy()) for lab in labels}    
        else:
            return {lab: rng(self.data.loc[self.data[col]==lab].index.to_numpy()) for lab in labels}
        
    
    def zero_g_acc(self):
        return self.att.inverse().transform_point(PZ(-9.81)) + self.acc

    def arc_centre(self) -> Point:
        acc = Point.vector_rejection(self.zero_g_acc(), self.vel)

        return acc.unit() * abs(self.vel) ** 2 / abs(acc)