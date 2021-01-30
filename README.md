# FlightAnalysis

WIP Tools for analysing flight log data

The general Idea
1. Read the sequence defintion from the serialisation of it (currently ./schedules/p21.json)
2. Read, trim and rotate flight log to a Sequence object
3. generate a roughly scaled and flipped template sequence using the geometry package
4. run a dynamic time warping algorithm to align the flight to the template
5. analyse each element according to the judging criteria of that element.

# TODO:
- Expand the section module to generate artificial elements
- detect areas in the box
- calculate angle between wings and the Y axis + other useful juding info
- some of the tests are failing for box definition(I think code is right, tests wrong)


# Dependencies:
python (3.6+?)
numpy
pandas
flightdata
geometry
scipy?
