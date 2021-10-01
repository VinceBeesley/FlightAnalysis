from flightanalysis import Section
from flightplotting.plots import plotsec

sec = Section.from_csv("tests/test_inputs/test_log_00000052_section.csv")

plotsec(sec.subset(110, 200), 10, 10).show()
