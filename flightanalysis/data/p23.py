"""This file defines a P23 sequence using the ManDef Classes and helper functions."""
from flightplotting import plotsec
from flightanalysis.schedule.definition import *
from flightanalysis.schedule.elements import *
from flightanalysis.criteria import *



def tHat():
    md = ManDef(
        ManInfo(
            "Top Hat", 
            "tHat", 
            4,
            Position.CENTRE,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
    ))

    md.add_loop(np.pi/2)
    md.add_simple_roll("2x4")
    md.add_loop(np.pi/2)
    md.add_simple_roll("1/2",l=100)
    md.add_loop(-np.pi/2)
    md.add_simple_roll("2x4")
    md.add_loop(-np.pi/2)
    return md


def hSqL():
    md = ManDef(
        ManInfo(
            "Half Square Loop", 
            "hSqL", 
            2,
            Position.END,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED),
            BoxLocation(Height.TOP)
        )
    )
    md.add_loop(-np.pi/2)
    md.add_simple_roll("1/2")
    md.add_loop(np.pi/2)
    return md

def hB():
    md = ManDef(
        ManInfo(
            "Humpty Bump", 
            "hB", 
            4,
            Position.CENTRE,
            BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.INVERTED),
            BoxLocation(Height.TOP)
        )
    )
    md.add_loop(np.pi/2)
    md.add_simple_roll("1/1") # TODO this should change to 1 sometime
    md.add_loop(np.pi)
    md.add_simple_roll("1/2")
    md.add_loop(-np.pi/2)
    return md

def hSqLC():
    md = ManDef(
        ManInfo(
            "Half Square on Corner", 
            "hSqLC", 
            3,
            Position.END,
            BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),
        ManParms.create_defaults_f3a(line_length=130*np.cos(np.radians(45)))
    )
    md.add_loop(-np.pi/4)
    md.add_simple_roll("1/2") 
    md.add_loop(np.pi/2)
    md.add_simple_roll("1/2")
    md.add_loop(-np.pi/4)
    return md

def upL():
    md = ManDef(
        ManInfo(
            "45 Upline Snaps", 
            "upL", 
            5,
            Position.CENTRE,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED),
            BoxLocation(Height.TOP)
        ),
        ManParms.create_defaults_f3a(line_length=110 + 130/np.cos(np.radians(45)))
    )
    md.add_loop(-np.pi/4)
    md.add_padded_snap([[1.5], [-1.5]])
    md.add_loop(-np.pi/4)
    return md

def h8L():
    md = ManDef(
        ManInfo(
            "Half 8 Sided Loop", 
            "h8L", 
            3,
            Position.END,
            BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),
        ManParms.create_defaults_f3a(line_length=50)
    )
    md.add_loop(-np.pi/4)
    md.add_line()
    md.add_loop(-np.pi/4)
    md.add_line()
    md.add_loop(-np.pi/4)
    md.add_line()
    md.add_loop(-np.pi/4)
    return md

def rollc():
    md = ManDef(
        ManInfo(
            "Roll Combo", 
            "rollc", 
            4,
            Position.CENTRE,
            BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.INVERTED),
            BoxLocation(Height.BTM)
        )
    )

    md.add_roll_combo([np.pi, np.pi, -np.pi, -np.pi])
    return md

def pImm():
    md = ManDef(
        ManInfo(
            "Immelman Turn", 
            "pImm", 
            2,
            Position.END,
            BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.INVERTED),
            BoxLocation(Height.TOP)
        ),
        ManParms.create_defaults_f3a(loop_radius=100)
    )

    md.add_loop(-np.pi)
    md.add_roll_combo([np.pi])
    return md

def iSp():
    md = ManDef(
        ManInfo(
            "Inverted Spin", 
            "iSp", 
            4,
            Position.CENTRE,
            BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            BoxLocation(Height.BTM)
        ),
        ManParms.create_defaults_f3a(
            speed=ManParm("speed", inter_free, 30.0)
        )
    )

    md.add_spin([[1.5], [-1.5]])
    md.add_line()
    md.add_loop(np.pi/2)
    return md

def hB2(option: int=0):
    md = ManDef(
        ManInfo(
            "Humpty Bump", 
            "hB2", 
            3,
            Position.END,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        )
    )

    ropts = md.mps.add(ManParm("roll_option", Combination(
        [
            [np.pi, np.pi],
            [np.pi, -np.pi],
            [-np.pi, np.pi],
            [-np.pi, -np.pi],
            [np.pi*1.5, -np.pi/2], 
            [-np.pi*1.5, np.pi/2]
        ]
        ), 
        option
    ))

    md.add_loop(np.pi/2)
    md.add_and_pad_els(
        ElDefs([ElDef.roll(
            md.eds.get_new_name(),
            md.mps.speed,
            md.mps.partial_roll_rate,
            ropts.valuefunc(0)
        )])
    )
    md.add_loop(np.pi)
    md.add_and_pad_els(
        ElDefs([ElDef.roll(
            md.eds.get_new_name(),
            md.mps.speed,
            md.mps.partial_roll_rate,
            ropts.valuefunc(1)
        )])
    )
    md.add_loop(-np.pi/2)
    return md

def rEt():
    md = ManDef(
        ManInfo(
            "Reverese Figure Et", 
            "rEt", 
            4,
            Position.CENTRE,
            BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.INVERTED),
            BoxLocation(Height.TOP)
        ),
        ManParms.create_defaults_f3a(loop_radius=70.0, line_length=100.0)
    )

    md.add_loop(-np.pi/4)
    md.add_and_pad_els(
        ElDefs.create_roll_combo(
            f"{md.eds.get_new_name()}_1",
            md.mps.add(ManParm(
                md.mps.next_free_name("roll_"),
                Combination([[np.pi, -np.pi],[-np.pi, np.pi]]),
                0
            )),
            md.mps.speed,
            [md.mps.partial_roll_rate, md.mps.partial_roll_rate],
            md.mps.point_length
        ),
        l=lambda mps: 2 * mps.loop_radius.value
    )
    md.add_loop(7*np.pi/4)
    md.add_simple_roll("2x4")
    md.add_loop(-np.pi/2)
    return md

def sqL():
    md = ManDef(
        ManInfo(
            "Half Square Loop", 
            "sqL", 
            2,
            Position.END,
            BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        )
    )

    md.add_loop(-np.pi/2)
    md.add_simple_roll("1/2")
    md.add_loop(np.pi/2)
    return md

def M(option:int=1):
    md = ManDef(
        ManInfo(
            "Figure M", 
            "M", 
            5,
            Position.CENTRE,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),
        ManParms.create_defaults_f3a(
            line_length=150.0,
            speed=ManParm("speed", inter_free, 30.0)
        )
    )

    ropts = md.mps.add(ManParm("roll_option", Combination(
        [
            [np.pi*3/2, np.pi*3/2],
            [-np.pi*3/2, -np.pi*3/2],
        ]
    ),option))

    md.add_loop(np.pi/2)
    md.add_and_pad_els(
        ElDefs([ElDef.roll(
            md.eds.get_new_name(),
            md.mps.speed,
            md.mps.partial_roll_rate,
            ropts.valuefunc(0)
        )])
    )
    md.add_stallturn()
    md.add_line()
    md.add_loop(-np.pi)
    md.add_line()
    md.add_stallturn()
    md.add_and_pad_els(
        ElDefs([ElDef.roll(
            md.eds.get_new_name(),
            md.mps.speed,
            md.mps.partial_roll_rate,
            ropts.valuefunc(1)
        )])
    )
    md.add_loop(np.pi/2)
    return md

def fTrn(option:int=1):
    md = ManDef(
        ManInfo(
            "Fighter Turn", 
            "fTrn", 
            4,
            Position.END,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        )
    )

    ropts = md.mps.add(ManParm("roll_option", Combination(
        [
            [np.pi/2, -np.pi/2],
            [-np.pi/2, np.pi/2],
        ]
    ),option))

    md.add_loop(np.pi/4)
    md.add_and_pad_els(
        ElDefs([ElDef.roll(
            md.eds.get_new_name(),
            md.mps.speed,
            md.mps.partial_roll_rate,
            ropts.valuefunc(0)
        )])
    )
    md.add_loop(-np.pi)
    md.add_and_pad_els(
        ElDefs([ElDef.roll(
            md.eds.get_new_name(),
            md.mps.speed,
            md.mps.partial_roll_rate,
            ropts.valuefunc(1)
        )])
    )
    md.add_loop(np.pi/4)
    return md

def trgle():
    md = ManDef(
        ManInfo(
            "Triangular Loop", 
            "trgle", 
            3,
            Position.CENTRE,
            BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        )
    )

    e1 = md.add_roll_combo([np.pi])
    bline_length = lambda mps: mps.line_length.value * np.cos(np.pi/4) - 0.5*e1[0].pfuncs["length"](mps)
    md.add_line(l=bline_length)
    md.add_loop(-np.pi*3/4)
    md.add_simple_roll("2x4")
    md.add_loop(np.pi/2)
    md.add_simple_roll("2x4")
    md.add_loop(-np.pi*3/4)
    md.add_line(l=bline_length)
    e1 = md.add_roll_combo([np.pi])
    return md

def sFin():
    md = ManDef(
        ManInfo(
            "Shark Fin", 
            "sFin", 
            3,
            Position.END,
            BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),
        ManParms.create_defaults_f3a(loop_radius=30.0)
    )

    md.add_loop(np.pi/2)
    md.add_simple_roll("1/2", l=80)
    md.add_loop(-np.pi*3/4)
    md.add_simple_roll("2X4", l=80/np.cos(np.radians(45)) + 60)
    md.add_loop(-np.pi/4)
    return md


def lop():
    md = ManDef(
        ManInfo(
            "Loop", 
            "lop", 
            3,
            Position.CENTRE,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED),
            BoxLocation(Height.BTM)
        ),
        ManParms.create_defaults_f3a(loop_radius=100.0)
    )


    md.add_loop(-np.pi*3/4)
    md.add_loop(
        -np.pi/2, 
        md.mps.add(ManParm(
            md.mps.next_free_name("roll_"), 
            Combination([[np.pi], [-np.pi]]), 0
        ))
    )
    md.add_loop(np.pi*3/4)
    return md

p23funcs = [tHat,hSqL,hB,hSqLC,upL,h8L,rollc,pImm,iSp,hB2,rEt,sqL,M,fTrn,trgle,sFin,lop]

def create_p23(wind=-1) -> SchedDef:
    sd =  SchedDef()
      

    for mfunc in p23funcs:
        if mfunc is M:
            mfunc = lambda : M(1 if wind==-1 else 0)
        if mfunc is fTrn:
            mfunc = lambda : fTrn(1 if wind==-1 else 0)
        sd.add(mfunc())
    return sd


if __name__ == "__main__":
     
    p23 = create_p23()
    from flightplotting import plotsec, plotdtw
    sched, template = p23.create_template()
    plotsec(template, nmodels=0).show()
    pass
