from flightdata import Flight
from flightanalysis import Section, FlightLine
from flightanalysis.flightline import Box
from flightplotting.plots import plotsec
from examples.model import obj
from geometry import GPSPosition

flight = Flight.from_csv("test/P21_new.csv")
sec = Section.from_flight(
    flight,
    FlightLine.from_box(Box.from_json("test/gordano_box.json"), GPSPosition(**flight.origin())),
)


plotsec(sec, obj, 10, 10).show()

plotsec(sec.subset(110, 200), obj, 10, 10).show()
