# FlightAnalysis

WIP Tools for analysing flight log data

The general Idea
1. Read the sequence defintion from the serialisation of it (currently schedule/p_21.py)
2. Read, trim and rotate flight log to a Sequence object
3. generate a roughly scaled and flipped template sequence using the geometry package
4. run a dynamic time warping algorithm to align the flight to the template
5. analyse each element according to the judging criteria of that element.

# TODO:
- detect areas in the box
- calculate angle between wings and the Y axis + other useful juding info
- scale templates based on axis rates
- scale templates based on flight data and criteria
- seperate default template scalings from the definition
- connect to arusti output
- redo f_21, p_23 and f_23 templates to match new definition


# Dependencies:
python (3.6+?)
numpy
pandas
flightdata
geometry
scipy?
