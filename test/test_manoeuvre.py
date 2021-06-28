import numpy as np
import unittest
from flightanalysis.schedule import Manoeuvre, Element, ElClass
from geometry import Point, Quaternion, Transformation, Coord

class TestManoeuvre(unittest.TestCase):
    def setUp(self):
        self.v8 = Manoeuvre("v8", 3, [
            Element(ElClass.LINE, 0.8, 0.0, 0.0),
            Element(ElClass.LINE, 0.2, 0.5, 0.0),
            Element(ElClass.LOOP, 0.45, 0.0, 1.0),
            Element(ElClass.LOOP, 0.45, 0.0, -1.0),
            Element(ElClass.LINE, 0.2, 0.5, 0.0),
        ])

    def test_create_template(self):
        endpos = self.v8.create_template(
            Transformation.from_coords(Coord.from_nothing(), Coord.from_nothing()),
            100.0
        )

        np.testing.assert_array_almost_equal(
            endpos.translation.to_list(),
            [120, 0.0, 0.0]
        )

        np.testing.assert_array_almost_equal(
            self.v8.elements[0].template.get_state_from_index(-1).transform.translation.to_list(),
            [80.0, 0.0, 0.0]
        )

        self.assertAlmostEqual(
            self.v8.elements[-1].template.data.index[-1],
            self.v8.template.data.index[-1]
        )