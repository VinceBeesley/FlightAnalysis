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
        df = pd.DataFrame(columns=Sequence.columns)
        df.index = flight.data.index
        df.x, df.y, df.z = flightline.transform.pos_vec(
            flight.read_field_tuples(Fields.POSITION))
        df.rw, df.rx, df.ry, df.rz = flightline.transform.eul_vec(
            flight.read_field_tuples(Fields.POSITION))

        return Sequence(df)

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
