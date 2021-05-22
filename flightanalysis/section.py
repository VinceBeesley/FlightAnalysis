from flightdata import Flight, Fields
from geometry import Point, Quaternion, Coord, Transformation, transformation, Points, Quaternions, cross_product
from numpy.testing._private.utils import assert_equal
from .flightline import FlightLine, Box
from .state import State
import numpy as np
import pandas as pd
from .schedule import Element
from typing import Callable, Tuple, List, Union
from numbers import Number
from .schedule import Schedule, Manoeuvre, Element, ElClass
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from scipy import optimize


class Section():
    _construct_freq = 20

    def __init__(self, data: pd.DataFrame):
        self.data = data

    def __getattr__(self, name):
        if name in self.data.columns:
            return self.data[name]
        elif name in State.vars.constructs:
            return self.data[State.vars.constructs[name]]
        else:
            raise AttributeError

    def subset(self, start: Number, end: Number):
        if start == -1 and not end == -1:
            return Section(self.data.loc[:end])
        elif end == -1 and not start == -1:
            return Section(self.data.loc[start:])
        elif start == -1 and end == -1:
            return Section(self.data)
        else:
            return Section(self.data[start:end])

    @staticmethod
    def stack(sections):
        offsets = [0] + [sec.data.index[-1] for sec in sections[:-1]]

        dfs = [section.data.iloc[:-1] for section in sections[:-1]] + \
            [sections[-1].data.copy()]

        for df, offset in zip(dfs, np.cumsum(offsets)):
            df.index = np.array(df.index) + offset

        return Section(pd.concat(dfs))

    @staticmethod
    def from_constructs(t, pos, att, bvel, brvel, bacc):

        df = pd.DataFrame(index=t, columns=list(State.vars))

        def savevars(vars: list, data: Union[Points, Quaternions]):
            df[vars] = data.to_pandas(columns=vars).set_index(df.index)

        savevars(State.vars.pos, pos)
        savevars(State.vars.att, att)
        savevars(State.vars.bvel, bvel)
        savevars(State.vars.brvel, brvel)
        savevars(State.vars.bacc, bacc)

        return Section(df)

    @staticmethod
    def from_flight(flight: Flight, flightline: FlightLine):
        # read position and attitude directly from the log(after transforming to flightline)
        t = flight.data.index
        pos = flightline.transform_from.point(
            Points(
                flight.read_numpy(Fields.POSITION).T
            ))

        att = flightline.transform_from.quat(
            Quaternions.from_euler(Points(
                flight.read_numpy(Fields.ATTITUDE).T
            )))

        dt = np.gradient(t)

        brvel = att.body_diff(dt)
        # this is EKF velocity estimate in NED frame transformed to contest frame
        vel = flightline.transform_to.rotate(Points.from_pandas(
            flight.data.loc[:, ["velocity_x", "velocity_y", "velocity_z"]]))
        bvel = att.inverse().transform_point(vel)

        bacc = Points.from_pandas(
            flight.data.loc[:, ["acceleration_x", "acceleration_y", "acceleration_z"]])

        # brvel = Points.from_pandas(flight.data.loc[:,["axis_rate_roll", "axis_rate_pitch", "axis_rate_yaw"]])

        return Section.from_constructs(t, pos, att, bvel, brvel, bacc)

    def to_csv(self, filename):
        self.data.to_csv(filename)
    
    @staticmethod
    def from_csv(filename):
        data = pd.read_csv(filename)
        data.index = data["time_flight"].copy()
        data.index.name = 'time_flight'

        return Section(data)

    def get_state_from_index(self, index):
        return State.from_series(self.data.iloc[index].copy())

    def get_state_from_time(self, time):
        return self.get_state_from_index(
            self.data.index.get_loc(time, method='nearest')
        )

    def body_to_world(self, pin: Union[Point, Points]) -> pd.DataFrame:
        """generate world frame trace of a body frame point

        Args:
            pin (Point): point in the body frame
            pin (Points): points in the body frame

        Returns:
            Points: trace of points
        """

        if isinstance(pin, Points) or isinstance(pin, Point):
            return Quaternions.from_pandas(self.att).transform_point(pin) + Points.from_pandas(self.pos)
        else:
            return NotImplemented

    @staticmethod
    def from_line(itransform: Transformation, speed: float, length: float):
        """generate a section representing a line. Provide an initial rotation rate to represent a roll.

        Args:
            initial (State): The initial state, the line will be drawn in the direction
                            of the initial velocity vector.
            t (np.array): the timesteps to create states for
        Returns:
            Section: Section class representing the line or roll.
        """
        duration = length / speed
        t = np.linspace(0, duration, int(duration * Section._construct_freq))
        ibvel = Point(speed, 0.0, 0.0)
        bvel = Points.from_point(ibvel, len(t))

        pos = Points.from_point(itransform.translation,
                                len(t)) + itransform.rotate(bvel) * t

        att = Quaternions.from_quaternion(itransform.rotation, len(t))

        return Section.from_constructs(
            t,
            pos,
            att,
            bvel,
            Points(np.zeros((len(t), 3))),
            Points(np.zeros((len(t), 3)))
        )

    def evaluate_radius(self, plane: str) -> Tuple[Point, np.ndarray, float]:
        """Calculate the radius, in the plane normal to the passed direction

        Args:
            normal (str): letter defining the normal direction of the desired radius plane in world frame

        Returns:
            Point: the centre of the radius in the world frame
            np.ndarray: the radius at each time index
            float: the mean radius
        """
        if plane == "x":
            x, y = self.y, self.z
        elif plane == "y":
            x, y = self.z, self.x
        elif plane == "z":
            x, y = self.x, self.y

        calc_R = lambda xc, yc : np.sqrt((x-xc)**2 + (y-yc)**2)

        def f_2(c):
            Ri = calc_R(*c)
            return Ri - Ri.mean()

        center_2, ier = optimize.leastsq(f_2, (0.0, 0.0))  # better to take the mean position or something
        Ri_2 = calc_R(*center_2)

        if plane == "x":
            centre = Point(self.x[0], center_2[0], center_2[1])
        elif plane == "y":
            centre = Point(center_2[1], self.y[0], center_2[0])
        elif plane == "z":
            centre = Point(self.x[0], center_2[1], self.z[0])

        return centre, Ri_2, Ri_2.mean()


    @staticmethod
    def from_loop(itransform: Transformation, speed: float, proportion: float, radius: float, ke: bool = False):
        """generate a loop, based on intitial position, speed, amount of loop, radius. 

        Args:
            itransform (Transformation): initial position
            speed (float): forward speed
            proportion (float): amount of loop. +ve offsets centre of loop in +ve body y or z
            r (float): radius of the loop (must be +ve)
            ke (bool, optional): [description]. Defaults to False. whether its a KE loop or normal

        Returns:
            [type]: [description]
        """
        duration = 2 * np.pi * radius * abs(proportion) / speed
        axis_rate = -proportion * 2 * np.pi / duration
        t = np.linspace(0, duration, int(duration * Section._construct_freq))

        # TODO There must be a more elegant way to do this. lots of random signs to make things give the right result
        # not backed by actual maths but it seems to work.
        if axis_rate == 0:
            raise NotImplementedError()
        radius = speed / axis_rate
        if not ke:
            radcoord = Coord.from_xy(
                itransform.point(Point(0, 0, -radius)),
                itransform.rotate(Point(0, 0, 1)),
                itransform.rotate(Point(1, 0, 0))
            )
            angles = Points.from_point(Point(0, axis_rate, 0), len(t)) * t
            radcoordpoints = Points(
                np.array(np.vectorize(
                    lambda angle: tuple(Point(
                        radius * np.cos(angle),
                        radius * np.sin(angle),
                        0
                    ))
                )(angles.y)).T
            )
            axisrates = Points.from_point(Point(0, axis_rate, 0), len(t))
            acceleration = -Points.from_point(cross_product(
                Point(0, axis_rate, 0) * Point(0, axis_rate, 0), Point(speed, 0, 0)), len(t))
        else:
            radcoord = Coord.from_xy(
                itransform.point(Point(0, -radius, 0)),
                itransform.rotate(Point(0, 1, 0)),
                itransform.rotate(Point(1, 0, 0))
            )
            angles = Points.from_point(Point(0, 0, -axis_rate), len(t)) * t
            radcoordpoints = Points(
                np.array(np.vectorize(
                    lambda angle: tuple(Point(
                        radius * np.cos(-angle),
                        radius * np.sin(-angle),
                        0
                    ))
                )(angles.z)).T
            )
            axisrates = Points.from_point(Point(0, 0, -axis_rate), len(t))
            acceleration = Points.from_point(cross_product(
                Point(0, 0, axis_rate) * Point(0, 0, axis_rate), Point(speed, 0, 0)), len(t))

        return Section.from_constructs(
            t,
            Transformation.from_coords(
                Coord.from_nothing(), radcoord).point(radcoordpoints),
            Quaternions.from_quaternion(
                itransform.rotation, len(t)).body_rotate(angles),
            Points.from_point(Point(speed, 0, 0), len(t)),
            axisrates,
            acceleration
        )

    @staticmethod
    def from_spin(itransform: Transformation, height: float, turns: float):
        inverted = itransform.rotate(Point(0, 0, 1)).z > 0

        nose_drop = Section.from_loop(
            itransform, 5.0, -0.25 * inverted, 2.0, False)

        rotation = Section.from_line(
            nose_drop.get_state_from_index(-1).transform,
            5.0,
            height-2.5
        ).superimpose_roll(turns)

        return Section.stack([nose_drop, rotation])

    def superimpose_roll(self, proportion: float):
        """Generate a new section, identical to self, but with a continous roll integrated

        Args:
            proportion (float): the amount of roll to integrate
        """
        t = np.array(self.data.index) - self.data.index[0]

        # roll rate to add:
        roll_rate = 2 * np.pi * proportion / t[-1]
        superimposed_roll = t * roll_rate

        # attitude
        angles = Points.from_point(
            Point(1.0, 0.0, 0.0), len(t)) * superimposed_roll

        new_att = Quaternions.from_pandas(self.att.copy()).body_rotate(
            angles)

        # axis rates:
        axisrates = Points.from_pandas(self.brvel.copy())
        new_rates = Points(np.array([
            np.full(len(t), roll_rate),
            axisrates.y * np.cos(superimposed_roll) +
            axisrates.z * np.sin(superimposed_roll),
            -axisrates.y * np.sin(superimposed_roll) +
            axisrates.z * np.cos(superimposed_roll)
        ]).T)

        acc = Points.from_pandas(self.bacc.copy())
        new_acc = Points(np.array([
            np.zeros(len(t)),
            acc.y * np.cos(superimposed_roll) + acc.z *
            np.sin(superimposed_roll),
            -acc.y * np.sin(superimposed_roll) + acc.z *
            np.cos(superimposed_roll)
        ]).T)

        return Section.from_constructs(
            t,
            Points.from_pandas(self.pos.copy()),
            new_att,
            Points.from_pandas(self.bvel.copy()),
            new_rates,
            new_acc
        )

    @ staticmethod
    def from_element(transform: Transformation, element: Element, speed: float = 30.0, scale: float = 200.0):
        """This function will generate a template set of data for a specified element
        and initial condition. The element will be as big as it can be within the supplied
        space.

        Args:
            element (Element): The element to generate, from the schedule description
            initial (Sequence): The previous sequence, last value will be taken as the starting point
            space (?Point?): TBC Limits of an available space, in A/C body frame (Xfwd, Yright, Zdwn)
        """
        if element.classification == ElClass.LOOP:
            el = Section.from_loop(
                transform, speed, element.loop, 0.5 * scale * element.size, False)
        elif element.classification == ElClass.KELOOP:
            el = Section.from_loop(
                transform, speed, element.loop, 0.5 * scale * element.size, True)
        elif element.classification == ElClass.LINE:
            el = Section.from_line(transform, speed, scale * element.size)
        elif element.classification == ElClass.SPIN:
            return Section.from_spin(transform, scale * element.size, element.roll)
        elif element.classification == ElClass.SNAP:
            el = Section.from_line(transform, speed, scale * element.size)
        elif element.classification == ElClass.STALLTURN:
            return Section.from_loop(transform, 3.0, 0.5, 2.0, True)

        if not element.roll == 0:
            el = el.superimpose_roll(element.roll)
        return el

    @ staticmethod
    def from_manoeuvre(transform: Transformation, manoeuvre: Manoeuvre, scale: float = 200.0):
        elms = []
        itrans = transform
        for i, element in enumerate(manoeuvre.elements):
            elms.append(Section.from_element(itrans, element, 30.0, scale))
            elms[-1].data["element"] = "{}_{}".format(
                i, element.classification.name)
            elms[-1].data["manoeuvre"] = manoeuvre.name
            itrans = elms[-1].get_state_from_index(-1).transform
        return elms

    def get_manoeuvre(self, manoeuvre: str):
        return Section(self.data[self.data.manoeuvre == manoeuvre])

    def split_manoeuvres(self):
        return {
            man: Section(self.data[self.data.manoeuvre == man]) for man in self.data["manoeuvre"].unique()
        }

    def split_elements(self):
        return {elm: Section(self.data[self.data.element == elm])
                for elm in self.data["element"].unique()}

    @ staticmethod
    def from_schedule(schedule: Schedule, distance: float = 170.0, direction: str = "right"):
        box_scale = np.tan(np.radians(60)) * distance

        dmul = -1.0 if direction == "right" else 1.0
        ipos = Point(
            dmul * box_scale * schedule.entry_x_offset,
            distance,
            box_scale * schedule.entry_z_offset
        )

        iatt = Quaternion.from_euler(Point(np.pi, 0, 0))

        if schedule.entry == "inverted":
            iatt = Quaternion.from_euler(Point(0, np.pi, 0)) * iatt
        if direction == "left":
            iatt = Quaternion.from_euler(Point(0, 0, np.pi)) * iatt

        itrans = Transformation(ipos, iatt)

        elms = []
        for manoeuvre in schedule.manoeuvres:
            elms += Section.from_manoeuvre(itrans, manoeuvre, scale=box_scale)
            itrans = elms[-1].get_state_from_index(-1).transform

        #add an exit line
        elms.append(Section.from_element(itrans, Element(ElClass.LINE, 0.25, 0.0, 0.0), 30.0, box_scale))
        elms[-1].data["manoeuvre"] = "exit_line"
        elms[-1].data["element"] = "0_LINE"
        return Section.stack(elms)

    @staticmethod
    def align(flown, template):
        fl = flown.brvel.copy()
        fl.brvr = abs(fl.brvr)
        fl.brvy = abs(fl.brvy)

        tp = template.brvel.copy()

        
        tp.brvr = abs(tp.brvr)
        tp.brvy = abs(tp.brvy)
        distance, path = fastdtw(
            tp.to_numpy(), 
            fl.to_numpy(), 
            radius=1,
            dist=euclidean
        )
        # TODO this join is not correct as length of flown template increases. 
        # TODO write some tests!
        return distance, Section(
            flown.data.reset_index().join(
                pd.DataFrame(path,columns=["template", "flight"]).set_index("flight").join(
                    template.data.reset_index().loc[:, ["manoeuvre", "element"]],
                    on="template"
                )
            ).set_index("time_index"))
