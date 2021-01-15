from flightdata import Flight, Fields
from geometry import Point, Quaternion
from .flightline import FlightLine, Box
from .state import State
import numpy as np
import pandas as pd
from .schedule import Element
from typing import Dict


# TODO not really happy with the name, not very descriptive.
class Section(State):
    def __init__(self, data: pd.DataFrame):
        super().__init__(data)

    @staticmethod
    def from_flight(flight: Flight, flightline: FlightLine):
        df = pd.DataFrame(columns=State.columns)
        df.x, df.y, df.z = flightline.transform_to.pos_vec(
            *flight.read_field_tuples(Fields.POSITION))
        df.rw, df.rx, df.ry, df.rz = flightline.transform_to.eul_vec(
            *flight.read_field_tuples(Fields.ATTITUDE))
        df.index = flight.data.index

        dt = pd.Series(df.index).diff()

        for nam in 'x,y,z,rx,ry,rz'.split(','):
            df['d' + nam] = np.vectorize(lambda n,
                                         d: n / d)(df[nam].diff(), dt)
            df['d' + nam +
                '2'] = np.vectorize(lambda n, d: n / d)(df['d' + nam].diff(), dt)

        return Section(df.iloc[2:-2])

    @property
    def pos(self):
        return self.data[['x', 'y', 'z']]

    @property
    def att(self):
        return self.data[['rw', 'rx', 'ry', 'rz']]

    @property
    def vel(self):
        return self.data[['dx', 'dy', 'dz']]

    @property
    def rvel(self):
        return self.data[['drw', 'drx', 'dry', 'drz']]

    @property
    def acc(self):
        return self.data[['dx2', 'dy2', 'dz2']]

    @property
    def racc(self):
        return self.data[['drw2', 'drx2', 'dry2', 'drz2']]

    @staticmethod
    def from_line(initial: State, length: float, npoints: int):
        df = initial.data.copy()

        return df

    @staticmethod
    def from_element(element: Element, initial, space):
        """This function will generate a template set of data for a specified element
        and initial condition. The element will be as big as it can be within the supplied
        space.

        Args:
            element (Element): The element to generate, from the schedule description
            initial (Sequence): The previous sequence, last value will be taken as the starting point
            space (?Point?): TBC Limits of an available space, in A/C body frame (Xfwd, Yright, Zdwn)
        """
