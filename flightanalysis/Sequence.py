from flightdata import Flight, Fields
from .box import FlightLine, Box
from .state import State
import numpy as np
import pandas as pd
from geometry import Point


class Sequence():
    columns = 'x,y,z,dx,dy,dz,dx2,dy2,dz2,rw,rx,ry,rx,drw,drx,dry,drz,drw2,drx2,dry2,drz2'.split(
        ',')

    def __init__(self, data):
        self.data = data

    @staticmethod
    def from_flight(flight: Flight, flightline: FlightLine):
        dat = flight.read_fields([
            Fields.GLOBALPOSITION,
            Fields.POSITION,
            Fields.VELOCITY,
            Fields.AXISRATE,
            Fields.TXCONTROLS,
            Fields.WIND
        ])

        df = pd.DataFrame(columns=Sequence.columns)

        pos_transform = np.vectorize(flightline.transform.pos)

        quat_transform = np.vectorize(flightline.transform.eul_to_quat)

        df.x, df.y, df.z = pos_transform(
            flight.read_field_tuples(Fields.POSITION))
        df.rx, df.ry, df.rz = quat_transform(
            flight.read_field_tuples(Fields.POSITION))

        return Sequence(data)

    @staticmethod
    def _generate_row(pos: Point, eul: Point, flightline: FlightLine):
        pass

    def __getattr__(self, name):
        if name in Sequence.columns:
            return self.data[name]
        else:
            raise AttributeError

    @property
    def pos(self):
        return self.data[['x', 'y', 'z']]

    @property
    def vel(self):
        return self.data[['dx', 'dy', 'dz']]

    @property
    def acc(self):
        return self.data[['dx2', 'dy2', 'dz2']]
