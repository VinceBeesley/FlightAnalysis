from flightanalysis.Sequence import Sequence
from flightanalysis.box import Box, FlightLine
import unittest

from flightdata import Flight, Fields

flight = Flight.from_log('./p21.BIN')


class TestSequence(unittest.TestCase):
    def test_from_flight(self):
        pass
        #seq = Sequence.from_flight(flight, flightline)
