from flightanalysis.sequence import Sequence
from flightanalysis.flightline import Box, FlightLine
import unittest

from flightdata import Flight, Fields
import numpy as np
import pandas as pd


flight = Flight.from_csv('test/P21.csv')


class TestSequence(unittest.TestCase):
    def test_from_flight(self):
        seq = Sequence.from_flight(flight, FlightLine.from_initial_position(flight))
        self.assertIsInstance(seq.x, pd.Series)
        self.assertIsInstance(seq.y, pd.Series)
        self.assertIsInstance(seq.z, pd.Series)
        self.assertIsInstance(seq.rw, pd.Series)
        self.assertIsInstance(seq.rx, pd.Series)
        self.assertIsInstance(seq.ry, pd.Series)
        self.assertIsInstance(seq.rz, pd.Series)
        self.assertGreater(seq.z.mean(), 0)


    def test_from_line(self):
        dat = np.zeros(shape=(1,len(Sequence.columns)))
        dat[:,0:3] = [-30, 170, 100] # initial position
        dat[:,3:6] = [-30, 0, 0] # initial velocity
        dat[:,9:13] = [0, np.cos(np.pi / 4), np.cos(np.pi / 4), 0] # initial attitude (I think)
        initial = pd.DataFrame(data=dat, columns=Sequence.columns)

        