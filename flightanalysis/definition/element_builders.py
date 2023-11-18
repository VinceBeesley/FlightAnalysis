from .element_definition import ElDef, ElDefs, ManParm, ManParms
from flightanalysis.elements import *
from flightdata import Collection
from flightanalysis.definition.collectors import Collectors
from flightanalysis.definition import Opp, ItemOpp
from flightanalysis.scoring.criteria.f3a_criteria import F3A
from flightanalysis.scoring import Combination
from numbers import Number
import numpy as np


def line(name, speed, length, roll):
    return ElDef.build(Line, name, speed, length, roll), ManParms()

def loop(name, speed, radius, angle, roll, ke):
    if isinstance(roll, str):
        roll = ManParm.parse(roll)
    if isinstance(angle, str):
        angle = ManParm.parse(angle)
    return ElDef.build(Loop, name, speed, radius, angle, roll, ke), ManParms()

def roll(name, speed, rate, rolls):
    el = ElDef.build(Line, name, speed, abs(rolls) * speed / rate, rolls)
    if isinstance(rate, ManParm):
        rate.collectors.add(el.get_collector("rate"))
    return el, ManParms()

def stallturn(name, speed, yaw_rate):
    return ElDef.build(StallTurn, name, speed, yaw_rate), ManParms()


def snap(name, rolls, break_angle, rate, speed, break_rate):
    '''This will create a snap'''
    eds = ElDefs()
    mps = ManParms()

    if isinstance(break_angle, Number):
        break_angle = ManParm(
            f"break_angle_{name}",
            Combination(desired=[[break_angle], [-break_angle]]),
            0
        )
        mps.add(break_angle)
    
    eds.add(ElDef.build(PitchBreak, f"{name}_break", speed=speed, 
        length=speed * abs(break_angle.value[0])/break_rate, break_angle=break_angle.value[0]))
    
    eds.add(ElDef.build(Autorotation, f"{name}_autorotation", speed=speed,
        length=speed*abs(rolls)/rate, roll=rolls))
    
    eds.add(ElDef.build(Recovery, f"{name}_recovery", speed=speed,
                    length=speed * abs(break_angle.value[0])/break_rate))
     
    return eds, mps


def roll_combo(
        name, speed, rolls, rolltypes, 
        partial_rate, full_rate, pause_length,
        break_angle, snap_rate, break_rate, mode) -> ElDefs:
    '''This creates a set of ElDefs to represent a list of rolls or snaps
      and pauses between them if mode==f3a it does not create pauses when roll direction is reversed
    '''
    eds = ElDefs()
    if rolltypes == 'roll' or rolltypes is None:
        rolltypes = ''.join(['r' for _ in rolls.value])
    elif rolltypes == 'snap':
        rolltypes = ''.join(['s' for _ in rolls.value])
    for i, r in enumerate(rolls.value):
        if rolltypes[i] == 'r':
            eds.add(roll(
                f"{name}_{i}", speed,
                partial_rate if abs(rolls.value[i]) < 2*np.pi else full_rate,
                r
            )[0])
        else:
            ed, mps = snap(
                f"{name}_{i}", r, break_angle, snap_rate, speed, break_rate
            )
            eds.add(ed)

        if rolltypes[i] == 'r':
            if rolls.value[i] < 2*np.pi and mode=='f3a':
                if isinstance(partial_rate, ManParm):
                    partial_rate.collectors.add(eds[-1].get_collector("rate"))
            else:
                if isinstance(full_rate, ManParm):
                    full_rate.collectors.add(eds[-1].get_collector("rate"))
        else:
            snap_rate.collectors.add(eds[-2].get_collector("rate"))

        if i < rolls.n - 1 and (mode=='imac' or np.sign(rolls.value[i]) == np.sign(rolls.value[i+1])):
            eds.add(line(
                f"{name}_{i+1}_pause",
                speed, pause_length, 0
            ))
                
    return eds, ManParms()


def pad(speed, line_length, eds: ElDefs):
    if isinstance(eds, ElDef):
        eds = ElDefs([eds])

    pad_length = 0.5 * (line_length - eds.builder_sum("length"))
    
    e1, mps = line(f"e_{eds[0].id}_pad1", speed, pad_length, 0)
    e3, mps = line(f"e_{eds[0].id}_pad2", speed, pad_length, 0)
    
    mp = ManParm(
        f"e_{eds[0].id}_pad_length", 
        F3A.inter.length,
        None, 
        Collectors([e1.get_collector("length") + 40, e3.get_collector("length") + 40])
    ) # TODO added 40 here as pads tend to be short. This needs to be more transparent.
    eds = ElDefs([e1] + [ed for ed in eds] + [e3])

    if isinstance(line_length, ManParm):
        line_length.append(eds.collector_sum("length", f"e_{eds[0].id}"))
    
    return eds, ManParms([mp])


def rollmaker(name, rolls, rolltypes, speed, partial_rate, 
    full_rate, pause_length, line_length, reversible, 
    break_angle, snap_rate, break_rate,
    padded, mode):

    mps = ManParms()
    if not isinstance(rolls, ManParm) and not isinstance(rolls, Opp):
        if isinstance(rolls, str):
            try:
                _rolls = ManParm.parse(rolls)
            except Exception as e:
                _rolls = ManParm(f"{name}_rolls", Combination.rollcombo(rolls, reversible), 0)
        else:
            _rolls = ManParm(f"{name}_rolls", 
                Combination.rolllist(
                    [rolls] if np.isscalar(rolls) else rolls, 
                    reversible
            ), 0) 
        mps.add(_rolls)
    else:
        _rolls = rolls
    
    if isinstance(_rolls, ItemOpp):
        _r=_rolls.a.value[_rolls.item]
        rate = full_rate if abs(_r)>=2*np.pi else partial_rate
        eds, rcmps = roll(f"{name}_roll", speed, rate, _rolls)
    else:
        eds, rcmps = roll_combo(
            name, speed, _rolls, rolltypes, 
            partial_rate, full_rate, pause_length,
            break_angle, snap_rate, break_rate, mode
        )
        
    mps.add(rcmps)
            
    if padded:
        eds, padmps = pad(speed, line_length, eds)
        mps.add(padmps)

    return eds, mps


def spin(name, turns, break_angle, rate, speed, break_rate, reversible):
    
    nose_drop = ElDef.build(NoseDrop, f"{name}_break", speed=speed, 
                      radius=speed * break_angle/break_rate, break_angle=break_angle)
    
    autorotation = ElDef.build(Autorotation, f"{name}_autorotation", speed=speed,
                        length=(speed * abs(turns))/rate, roll=turns)
    
    if isinstance(rate, ManParm):
        if isinstance(rate, ManParm):
            rate.collectors.add(autorotation.get_collector("rate"))

    recovery = ElDef.build(Recovery, f"{name}_recovery", speed=speed,
                    length=speed * break_angle/break_rate)
    return ElDefs([nose_drop, autorotation, recovery]), ManParms()
    