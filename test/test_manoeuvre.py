import numpy as np
import unittest
from flightanalysis.schedule import Manoeuvre
from flightanalysis.schedule.element import LineEl, LoopEl
from geometry import Point, Quaternion, Transformation, Coord


class TestManoeuvre(unittest.TestCase):
    def setUp(self):
        self.v8 = Manoeuvre("v8", 3, [
            LineEl(0.8, 0.0),
            LineEl(0.2, 0.5),
            LoopEl(0.45, 1.0),
            LoopEl(0.45, -1.0),
            LineEl(0.2, 0.5),
        ])
        self.scaled_v8 = self.v8.scale(100.0)

    def test_create_template(self):
        v8_template = self.scaled_v8.create_template(
            Transformation.from_coords(
                Coord.from_nothing(), Coord.from_nothing()),
            30.0
        )

        np.testing.assert_array_almost_equal(
            v8_template.get_state_from_index(-1).pos.to_list(),
            [120, 0.0, 0.0]
        )

        self.assertGreater(
            len(self.v8.elements[1].get_data(v8_template).data), 
            1
        )

        self.assertEqual(v8_template.get_state_from_time(0.0).pos, v8_template.get_state_from_index(0).pos)
    
    def test_get_elm_by_type(self):
        lines = self.v8.get_elm_by_type(LineEl)
        self.assertEqual(len(lines),3)

    
    def test_replace_elms(self):
        elms = [elm.set_parameter(length=10) for elm in self.v8.elements[:2]]
        new_v8 = self.v8.replace_elms(elms)
        self.assertEqual(new_v8.elements[0].uid, elms[0].uid)
        self.assertEqual(new_v8.elements[0].length, 10)


    def test_fix_loop_diameters(self):
        new_v8 = self.v8.replace_elms([self.v8.elements[3].set_parameter(diameter=10.0)])
        fixed_v8 = new_v8.fix_loop_diameters()
        self.assertEqual(fixed_v8.elements[3].diameter, 0.45)
