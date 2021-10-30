
from flightanalysis.schedule.elements import Snap
import unittest
from geometry import Transformation
import numpy as np


class TestSnap(unittest.TestCase):
    def test_create_template(self):
        raw_el = Snap(1.0)
        template = raw_el.create_template(Transformation(), 30.0)
        np.testing.assert_array_almost_equal(
            template.get_state_from_index(-1).pos.to_list(),
            [27, 0.0, 0.0]
        )
        self.assertEqual(len(raw_el.get_data(template).data),
                         len(template.data))

    def test_scale(self):
        raw_el = Snap(1.0)
        scaled = raw_el.scale(150)