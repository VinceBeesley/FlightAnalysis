
import pytest
from flightanalysis.schedule.elements.snap import Snap


def test_length():
    snap = Snap(1.0)    
    pytest.approx(snap.length, 27)
