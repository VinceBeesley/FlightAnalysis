from flightdata import Flight, Fields
import numpy as np
import pandas as pd


class Sequence():
    def __init__(self, data):
        self.data = data

    @staticmethod
    def from_flight(flight):
        dat = flight.read_fields([
            Fields.GLOBALPOSITION,
            Fields.POSITION
            Fields.VELOCITY,
            Fields.AXISRATE,
            Fields.TXCONTROLS,
            Fields.WIND
        ])

    @property
    def pos(self):
        return self.data[['x', 'y', 'z']]

    @property
    def vel(self):
        return self.data[['dx', 'dy', 'dz']]

    @property
    def acc(self):
        return self.data[['dx2', 'dy2', 'dz2']]
