"""This file defines a P23 sequence using the ManDef Classes and helper functions."""
from flightplotting import plotsec
from geometry import Transformation
from pytest import fixture

from flightanalysis.schedule.definition import *
from flightanalysis.schedule.elements import *
from flightanalysis.criteria.comparison import *
from flightanalysis.criteria.local import *



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
        )
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
        )
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
        )
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
        )
        )

    md.add_spin([[1.5], [-1.5]])
    md.add_line()
    md.add_loop(np.pi/2)
    return md

def hB2():
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
        0
    ))

    md.add_loop(np.pi/2)
    md.add_simple_roll(ropts.valuefunc(0), l=100)
    md.add_loop(np.pi)
    md.add_simple_roll(ropts.valuefunc(1), l=100)
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
        )
    )

    md.add_loop(-np.pi/4)
    md.add_and_pad_els(
        ElDefs.create_roll_combo(
            md.eds.get_new_name(),
            ManParm(
                md.mps.get_new_name("roll_"),
                Combination([[np.pi, -np.pi],[-np.pi, np.pi]]),
                0
            ),
            md.mps.s
            [md.mps.partial_roll_rate, md.mps.partial_roll_rate],
            md.mps.point_length
        ),
        l=lambda mps: 2 * mps.loop_radius
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

def M():
    md = ManDef(
        ManInfo(
            "Figure M", 
            "M", 
            5,
            Position.CENTRE,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        )
    )

    ropts = md.mps.add(ManParm("roll_option", Combination(
        [
            [np.pi*3/2, np.pi*3/2],
            [-np.pi*3/2, -np.pi*3/2],
        ]
    ),0))

    md.add_loop(np.pi/2)
    md.add_and_pad_els(
        ElDefs.from_list([ElDef.roll(
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
        ElDefs.from_list([ElDef.roll(
            md.eds.get_new_name(),
            md.mps.speed,
            md.mps.partial_roll_rate,
            ropts.valuefunc(1)
        )])
    )
    md.add_loop(np.pi/2)
    return md

def fTrn():
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
            [np.pi*2, -np.pi/2],
            [-np.pi/2, np.pi/2],
        ]
    ),0))

    md.add_loop(np.pi/4)
    md.add_and_pad_els(
        ElDefs.from_list([ElDef.roll(
            md.eds.get_new_name(),
            md.mps.speed,
            md.mps.partial_roll_rate,
            ropts.valuefunc(0)
        )])
    )
    md.add_loop(-np.pi)
    md.add_and_pad_els(
        ElDefs.from_list([ElDef.roll(
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

    e1 = md.add_roll_combo([np.pi/2])
    bline_length = lambda mps: mps.line_length.value * np.cos(45) - e1.pfuncs["length"](mps)
    md.add_line(l=bline_length)
    md.add_loop(-np.pi*3.4)
    md.add_simple_roll("2x4")
    md.add_loop(np.pi/2)
    md.add_simple_roll("2x4")
    md.add_loop(-np.pi*3.4)
    md.add_line(l=bline_length)
    e1 = md.add_roll_combo([np.pi/2])
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
        )
    )

    md.add_loop(np.pi)
    md.add_simple_roll("1/2")
    md.add_loop(-np.pi*3/4)
    md.add_simple_roll("2X4", l=150)
    md.add_loop(-np.pi/4)
    return md


def lop():
    md = ManDef(
        ManInfo(
            "Shark Fin", 
            "lop", 
            3,
            Position.CENTRE,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED),
            BoxLocation(Height.BTM)
        )
    )


    md.add_loop(-np.pi*3/4)
    md.add_loop(
        np.pi/2, 
        md.mps.add(ManParm(
            md.mps.get_new_name("roll_"), 
            Combination([[np.pi, -np.pi]]), 0
        ))
    )
    md.add_loop(np.pi*3/4)
    return md

p23funcs = [tHat,hSqL,hB,hSqLC,upL,h8L,rollc,pImm,iSp,hB2,rEt,sqL,M,fTrn,trgle,sFin,lop]

def create_p23():
    sd =  SchedDef("P23")
    for mfunc in p23funcs:
        sd.add(mfunc())
    return sd


if __name__ == "__main__":
    for mfunc in p23funcs[8:]:
        md = mfunc()
        man = md.create()
        itrans = md.info.initial_transform(170, 1)
        eld = md.create_entry_line(itrans)
        el = eld(md.mps)
        et = el.create_template(itrans)
        template = man.create_template(et[-1].transform)
        
        

        from flightplotting import plotsec

        plotsec(State.stack([et, template]), nmodels=3).show()
        pass
