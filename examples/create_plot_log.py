from flightanalysis import Section
from flightplotting.plots import plotsec

sec = Section.from_csv("tests/test_inputs/test_log_00000052_section.csv").subset(110, 200)

plotsec(sec, 10, 10).show()
