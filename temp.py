from flightdata import Flight
from flightanalysis import State, Box

fl = Flight.from_csv('tests/data/p23.csv')
box = Box.from_f3a_zone('tests/data/p23_box.f3a')
st = State.from_flight(fl, box)

from flightplotting import plotsec


plotsec(st[:200]).show()