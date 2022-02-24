


from flightanalysis.schedule.elements import StallTurn
import pytest
from geometry import Transformation, Points, Point, Quaternion
import numpy as np


def test_create_template():
    template = StallTurn().create_template(Transformation(), 30.0)

    np.testing.assert_array_almost_equal(
        template[-1].pos.to_list(),
        [0.0, 0.0, 0.0]
    )
    
    np.testing.assert_array_almost_equal(
        Point.X(-1.0).to_list(),
        template[-1].att.transform_point(Point.X(1.0)).to_list()
    )


def test_match_axis_rate():
    template = StallTurn(1).match_axis_rate(15.0, 30.0).create_template(Transformation(), 30.0)

    
    pytest.approx(template.brvy.mean(), 15.0)

