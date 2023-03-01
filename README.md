# FlightAnalysis

This package contains tools for analysing flight log data. 

The Main Idea
1. Read the sequence defintion from the serialisation of it (currently schedule/p_21.py)
2. Read, trim and rotate flight recorded flight data
3. generate a roughly scaled template sequence
4. run a dynamic time warping algorithm to align the flight to the template
5. generate scaled templates based on the rules and the flown manoeuvre
6. Expose an environment for grading criteria to be encoded based on rules of the aerobatic competition disciplines

# Side Projects
- Estimate winds from flight data without airspeed sensor. see examples/wind.ipynb
- Construct a FD model from the flight data with MLP regression or something.
- The templates are constructed in some kind of 'Judging' axis, similar to the aircraft wind axis but with atmospheric wind removed. Consider accounting for some aerodynamic characteristics here and constructing templates at some alpha and beta.
- Compare logged control inputs to ideal control inputs calculated using the templates and the FDmodel.


# External Dependencies:
scipy
fastdtw
ardupilot_log_reader
flightdata
pfc-geometry
