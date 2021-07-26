from re import L
from flightanalysis.schedule import p21
from flightanalysis import Section
import numpy as np
import timeit



sched = p21.scale_distance(170.0)


for freq in np.linspace(1, 10, 5)**2:
    Section._construct_freq = freq

    starttime = timeit.default_timer()

    temp = sched.create_raw_template("left", 50.0, 170.0)

    print("freq = {}, data_points={}, ex_time ={}".format(
        freq,
        len(temp.data),
        timeit.default_timer() - starttime)
    )

Section._construct_freq = 20

temp = sched.create_raw_template("left", 50.0, 170.0)

sec = Section.from_flight(
    "test/P21_new.csv", "test/gordano_box.json").subset(106, 505)

for radius in [1, 2, 3, 5, 10, 20]:
    starttime = timeit.default_timer()
    fit_qual_b, aligned_b = Section.align(sec, temp, int(radius))
    print("radius = {}, fit_qual={}, ex_time ={}".format(
        int(radius),
        fit_qual_b,
        timeit.default_timer() - starttime)
    )