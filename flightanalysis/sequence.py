from flightdata import Flight, Fields
from .flightline import FlightLine, Box
from .state import State
import numpy as np
import pandas as pd
from geometry import Point


class Sequence():
    columns = 'x,y,z,dx,dy,dz,dx2,dy2,dz2,rw,rx,ry,rz,drw,drx,dry,drz,drw2,drx2,dry2,drz2'.split(
        ',')

    def __init__(self, data):
        self.data = data
        
    @staticmethod
    def from_flight(flight: Flight, flightline: FlightLine):
        df = pd.DataFrame(columns=Sequence.columns)
        df.x, df.y, df.z = flightline.transform_to.pos_vec(
            *flight.read_field_tuples(Fields.POSITION))
        df.rw, df.rx, df.ry, df.rz = flightline.transform_to.eul_vec(
            *flight.read_field_tuples(Fields.ATTITUDE))
        df.index = flight.data.index

        dt = pd.Series(df.index).diff()
        
        for nam in 'x,y,z,rx,ry,rz'.split(','):
            df['d' + nam] = np.vectorize(lambda n, d: n / d)(df[nam].diff(), dt)
            df['d' + nam + '2'] = np.vectorize(lambda n, d: n / d)(df['d' + nam].diff(), dt)

        return Sequence(df.iloc[2:-2])

    def __getattr__(self, name):
        if name in Sequence.columns:
            return self.data[name]
        else:
            raise AttributeError

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
