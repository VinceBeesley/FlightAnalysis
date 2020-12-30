import unittest
from flightanalysis.state import State
from flightdata import Flight, Fields
from geometry import Point, Quaternion
from math import pi
from collections import namedtuple


class TestState(unittest.TestCase):
    def setUp(self):
        self.state_dict = {val: 0 for val in Fields.all_names()}

    def test_from_flight(self):
        stest = self.state_dict
        stest['position_x'] = 1
        stest['position_z'] = 3
        stest['attitude_yaw'] = pi / 2
        state = State.from_flight(self.state_dict)
        self.assertEqual(state.pos.x, 1)
        self.assertEqual(state.pos.z, 3)

        self.assertAlmostEqual(state.att.z, 0.7071067811865475)
        self.assertAlmostEqual(state.att.x, 0)
        self.assertAlmostEqual(state.att.y, 0)
        self.assertAlmostEqual(state.att.w, 0.7071067811865475)

    def test_from_to_dict(self):
        sdict = dict(Point(1, 2, 3).to_dict(), **
                     Quaternion(1, Point(1, 2, 3)).to_dict('q'))
        state = State.from_dict(
            {'testprefix' + key: value for key, value in sdict.items()})
        self.assertEqual(state.pos.x, 1)
        self.assertEqual(state.pos.y, 2)
        self.assertEqual(state.att.w, 1)
        self.assertEqual(state.att.x, 1)

        sd2 = state.to_dict('tt')

        self.assertEqual(sd2['ttx'], sdict['x'])
        self.assertEqual(sd2['ttqx'], sdict['qx'])
