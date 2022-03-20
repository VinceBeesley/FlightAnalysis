from flightanalysis.state.state import State
from flightanalysis.state.tools.builders import extrapolate
from pytest import approx, fixture, raises
from geometry import Transformation, PX


def test_extrapolate():
    initial = State.from_transform(
        Transformation(),
        vel=PX(30)
    )

    extrapolated = extrapolate(initial, 10, 30)
    



