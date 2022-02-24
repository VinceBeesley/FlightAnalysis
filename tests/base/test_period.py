from flightanalysis.base.period import Period
from flightanalysis.base.instant import Instant
from flightanalysis.section.variables import secvars
import numpy as np
import pandas as pd
from geometry import Points, Point

class Section(Period):
    _cols=secvars

    @property
    def _Instant(self):
        return State


class State(Instant):
    _cols=secvars
    @property
    def _Period(self):
        return Section


df = pd.DataFrame(np.random.random((200,8)), columns=['t', 'x', 'y', 'z', 'rw', 'rx', 'ry', 'rz'])
df['t'] = np.linspace(0, 200/30, 200)
df = df.set_index("t", drop=False)


def test_init():
    sec = Section(df)   
    assert isinstance(sec.x, pd.Series)

    assert isinstance(sec.pos, pd.DataFrame)
    assert isinstance(sec.gpos, Points)

    st = sec[6]
    assert isinstance(st, State)

    assert isinstance(st.pos, Point)

    