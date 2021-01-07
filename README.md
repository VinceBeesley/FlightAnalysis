# FlightAnalysis

WIP Tools for analysing flight log data

The general Idea
1. Read the sequence defintion from the serialisation of it (currently ./schedules/p21.json)
2. Read, trim and rotate flight log to a Sequence object
3. generate a roughly scaled and flipped template sequence using the geometry package
4. run a dynamic time warping algorithm to align the flight to the template
5. analyse each element according to the judging criteria of that element.

# TODO:
- the Sequence class contains sequence frame data, add support for an equivalent body frame Class
- Expand the schedule module to generate a perfect sequence
- detect areas in the box
- calculate angle between wings and the Y axis + other useful juding info
- some of the tests are failing for box definition(I think code is right, tests wrong)
