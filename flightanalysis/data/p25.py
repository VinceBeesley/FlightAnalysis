from flightplotting import plotsec
from flightanalysis.schedule.definition import *
from flightanalysis.schedule.elements import *
from flightanalysis.criteria import *

p25_def = SchedDef([
    f3amb.create(ManInfo(
            "Triangle", "tri", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi/4),
            f3amb.roll("2x4"),
            f3amb.loop(-np.pi*3/4), 
            f3amb.roll("1/1",line_length="btm_line_length"),
            f3amb.loop(-np.pi*3/4),
            f3amb.roll("2x4"),
            f3amb.loop(np.pi/4)
        ], btm_line_length = "(line_length*1.4142135623730951)", line_length=150),
    f3amb.create(ManInfo(
            "half square", "hsq", k=2, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll("1/1"),
            f3amb.loop(np.pi/2), 
        ]),
    f3amb.create(ManInfo(
            "Square on Corner", "sqc", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/4),
            f3amb.roll("1/2"),
            f3amb.loop(-np.pi/2),
            f3amb.roll("1/2"), 
            f3amb.loop(np.pi/2),
            f3amb.roll("1/2"), 
            f3amb.loop(-np.pi/2),
            f3amb.roll("1/2"), 
            f3amb.loop(np.pi/4),
        ], line_length=80),
    f3amb.create(ManInfo(
            "Figure P", "figP", k=3, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.MID)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll("1/2"),
            f3amb.loop(np.pi*3/2),
        ]),
#    f3amb.create(ManInfo(
#            "Square on Corner", "sqc", k=4, position=Position.CENTRE, 
#            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
#            end=BoxLocation(Height.BTM)
#        ),[
#            f3amb.roll(np.pi*np.array([])),
#        ], line_length=80)
])


if __name__ == "__main__":
    p25, template = p25_def.create_template(170, 1)
    from flightplotting import plotsec
    
    plotsec(template).show()