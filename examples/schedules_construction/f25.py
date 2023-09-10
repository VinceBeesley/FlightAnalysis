from flightanalysis.schedule.definition import *
from flightanalysis.schedule.elements import *
from flightanalysis.schedule.scoring.criteria import *
import numpy as np

c45 = np.cos(np.radians(45))



f25_def = SchedDef([
    f3amb.create(ManInfo(
            "Square on Corner", "sqc", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/4, roll="roll_option[0]"),
            f3amb.line(),
            f3amb.loop("roll_option[1]", roll=np.pi, ke=True),
            f3amb.line(),
            f3amb.loop("roll_option[2]", roll=np.pi, ke=True),
            f3amb.line(),
            f3amb.loop("roll_option[3]", roll=np.pi, ke=True),
            f3amb.line(),
            f3amb.loop("roll_option[4]", roll="roll_option[5]", ke=True),
        ], 
        roll_option=ManParm("roll_option", Combination(desired=[
            [np.pi/2, -np.pi/2, np.pi/2, -np.pi/2, np.pi/4, -np.pi/2], 
            [-np.pi/2, np.pi/2, -np.pi/2, np.pi/2, -np.pi/4, -np.pi/2]
        ]), 0),
        line_length=70
        ),
    f3amb.create(ManInfo(
            "Figure P", "P", k=4, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.MID)
        ),[
            f3amb.loop(-np.pi/2),
            f3amb.roll([2*np.pi,-np.pi]),
            f3amb.loop(-3*np.pi/2),
        ], full_roll_rate=np.pi, partial_roll_rate=np.pi ),
    f3amb.create(ManInfo(
            "Roll Combo", "Rc", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.MID, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.roll([np.pi/2, np.pi/2, -np.pi/2, -np.pi/2, -np.pi/2, -np.pi/2, np.pi/2, np.pi/2], padded=False)
        ], ),
    f3amb.create(ManInfo(
            "Half Loop", "Hlp", k=4, position=Position.END, 
            start=BoxLocation(Height.MID, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(-np.pi, roll=np.pi)
        ], ),
    f3amb.create(ManInfo(
            "Humpty", "Hb", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.snap(1.5),
            f3amb.loop(np.pi, roll=np.pi),
            f3amb.roll('3/2'),
            f3amb.loop(-np.pi/2)
        ], full_roll_rate=np.pi),
    f3amb.create(ManInfo(
            "Spins", "Sp", k=4, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.spin(3),
            f3amb.roll("1/2", line_length=147),
            f3amb.loop(np.pi/2)
        ], ),
    f3amb.create(ManInfo(
            "Rolling Circle", "Cir", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop("roll_option[0]", roll="roll_option[1]", ke=True),
            f3amb.loop("roll_option[2]", roll="roll_option[3]", ke=True),
            f3amb.loop("roll_option[4]", roll="roll_option[5]", ke=True)
        ], 
        loop_radius=100,
         roll_option=ManParm("roll_option", Combination(desired=[
            [np.pi/2, np.pi, -np.pi, -np.pi, np.pi/2, np.pi], 
            [-np.pi/2, -np.pi, np.pi, np.pi, -np.pi/2, -np.pi]
        ]), 1),
        ),
    f3amb.create(ManInfo(
            "Shark Fin", "sFin", k=4, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(-np.pi/2),
            f3amb.roll('2/2'),
            f3amb.loop(-3*np.pi/4),
            f3amb.snap([1, -1], line_length=str(f3amb.mps.line_length / c45 + 2*f3amb.mps.loop_radius)),
            #L2 = (L1 + 2*R - 2*R(1-c45)) / c45
            #L2 = (L1/c45 + 2*R)
            f3amb.loop(np.pi/4)
        ], line_length=80, full_roll_rate=np.pi, loop_radius=40),
    f3amb.create(ManInfo(
            "Square Octagonal Loop", "SqOL", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll('1/2'),
            f3amb.loop(-np.pi/2),
            f3amb.roll('1/1'),
            f3amb.loop(np.pi/2),
            f3amb.roll("roll_option[0]"),
            f3amb.loop("roll_option[1]", ke=True),
            f3amb.roll('1/1'),
            f3amb.loop("roll_option[2]", ke=True),
            f3amb.roll("roll_option[3]"),
            f3amb.loop(-np.pi/2),
            f3amb.roll('1/1'),
            f3amb.loop(np.pi/2),
            f3amb.roll('1/2'),
            f3amb.loop(-np.pi/2)
        ], line_length=60, full_roll_rate=3*np.pi/2, partial_roll_rate=3*np.pi/2, loop_radius=35,
        roll_option=ManParm("roll_option", Combination(desired=[
                [np.pi/2, -np.pi/2, -np.pi/2, np.pi/2], 
                [-np.pi/2, np.pi/2, np.pi/2, -np.pi/2]
            ]), 0),
        ),
    f3amb.create(ManInfo(
            "Humpty_2", "Hb2", k=4, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED), 
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(-np.pi/2),
            f3amb.roll('1/2'),
            f3amb.loop(-np.pi),
            f3amb.roll('3/2'),
            f3amb.loop(np.pi/2),
        ], ),
    f3amb.create(ManInfo(
            "Triangular Loop", "Tri", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(3*np.pi/4, roll="roll_option[0]"),
            f3amb.roll('1/2'),
            f3amb.loop("roll_option[1]", roll=np.pi, ke=True),
            f3amb.roll('1/2'),
            f3amb.loop("roll_option[2]", roll="roll_option[3]", ke=True)
        ], 
        roll_option=ManParm("roll_option", Combination(desired=[
                [-np.pi/2, -np.pi/2, -3*np.pi/4, -np.pi/2], 
                [np.pi/2, np.pi/2, 3*np.pi/4, np.pi/2]
            ]), 0),
        ),
    f3amb.create(ManInfo(
            "Half 8 Sided Loop", "h8lp", k=4, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi/4),
            f3amb.roll("roll_option[0]"),
            f3amb.loop("roll_option[1]", ke=True),
            f3amb.line(),
            f3amb.loop("roll_option[2]", ke=True),
            f3amb.roll("roll_option[3]"),
            f3amb.loop(np.pi/4)
        ], line_length=65, loop_radius=35,
        roll_option=ManParm("roll_option", Combination(desired=[
                [np.pi/2, -np.pi/4, -np.pi/4, -np.pi/2], 
                [-np.pi/2, np.pi/4, np.pi/4, np.pi/2]
            ]), 0),
        ),
    f3amb.create(ManInfo(
            "45 degree downline", "d45", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/4),
            f3amb.roll([9*np.pi/4, -9*np.pi/4]),
            f3amb.loop(-np.pi/4)
        ], full_roll_rate=np.pi, line_length=231/c45 - (2/c45-2)*55 ),
        #231/c45 - (2/c45-2)*R)= L
    f3amb.create(ManInfo(
            "Half Square Loop", "Hsq", k=4, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(-np.pi/2),
            f3amb.roll([2*np.pi, - np.pi]),
            f3amb.loop(np.pi/2)
        ], full_roll_rate=np.pi, partial_roll_rate=np.pi ),
    f3amb.create(ManInfo(
            "Avalanche", "Av", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi/2, roll="roll_option[0]"),
            f3amb.loop("roll_option[1]", ke=True),
            f3amb.snap(1, padded=False),
            f3amb.loop("roll_option[2]", ke=True),
            f3amb.loop("roll_option[3]", roll="roll_option[4]", ke=True)
        ], loop_radius=100, 
        roll_option=ManParm("roll_option", Combination(desired=[
                [np.pi/2, -np.pi/2, -np.pi/2, -np.pi/2, -np.pi/2], 
                [-np.pi/2, np.pi/2, np.pi/2, np.pi/2, np.pi/2]
            ]), 0),
        ),
    f3amb.create(ManInfo(
            "Split S", "SpS", k=4, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.roll("roll_option[0]", padded=False),
            f3amb.loop("roll_option[1]", ke=True),
            f3amb.roll("roll_option[2]", padded=False)
        ], loop_radius=122.5,
        roll_option=ManParm("roll_option", Combination(desired=[
                [np.pi/2, -np.pi, np.pi/2], 
                [-np.pi/2, np.pi, -np.pi/2],
            ]), 0),
        ),
    f3amb.create(ManInfo(
            "Stall Turn", "St", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.roll('1/2', padded=False),
            f3amb.line(length="ee_pause"),
            f3amb.loop(np.pi/2),
            f3amb.roll("3x4"),
            f3amb.stallturn(),
            f3amb.snap(0.75),
            f3amb.loop(-np.pi/2),
            f3amb.line(length="ee_pause"),
            f3amb.roll('1/2', padded=False),
        ], 
        line_length=150,
        partial_roll_rate=np.pi,
        ee_pause=10,
        #roll_option=need to thing about how to do this
    )
])



if __name__ == "__main__":

 
#    f25_def.plot().show()
    f25_def.create_fcj('F25', 'f25_template_fcj.json')
#    f25_def.save_json("flightanalysis/data/f25_schedule.json")