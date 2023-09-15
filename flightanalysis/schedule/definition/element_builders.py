from .element_definition import ElDef, ElDefs, ManParm, ManParms
from flightanalysis.schedule.elements import *
from flightanalysis.base.collection import Collection
from flightanalysis.schedule.definition.collectors import Collectors
from flightanalysis.schedule.definition import Opp, ItemOpp
from flightanalysis.schedule.scoring.criteria.f3a_criteria import F3A
from flightanalysis.schedule.scoring import Combination
from numbers import Number
import numpy as np


def line(name, speed, length, roll):
    return ElDef.build(Line, name, speed, length, roll), ManParms()

def loop(name, speed, radius, angle, roll, ke):
    return ElDef.build(Loop, name, speed, radius, angle, roll, ke), ManParms()

def roll(name, speed, rate, angle):
    el = ElDef.build(Line, name, speed, abs(angle) * speed / rate, angle)
    if isinstance(rate, ManParm):
        rate.collectors.add(el.get_collector("rate"))
    return el, ManParms()

def stallturn(name, speed, yaw_rate):
    return ElDef.build(StallTurn, name, speed, yaw_rate), ManParms()


def roll_combo_f3a(name, speed, rolls, partial_rate, full_rate, pause_length) -> ElDefs:
    #this creates pauses between same direction rolls and has a different rate for full and
    #part rolls.
    eds = ElDefs()
    
    for i, r in enumerate(rolls.value):
        eds.add(roll(
            f"{name}_{i}",
            speed,
            partial_rate if abs(rolls.value[i]) < 2*np.pi else full_rate,
            rolls[i]
        ))

        if rolls.value[i] < 2*np.pi:
            if isinstance(partial_rate, ManParm):
                partial_rate.collectors.add(eds[-1].get_collector("rate"))
        else:
            if isinstance(full_rate, ManParm):
                full_rate.collectors.add(eds[-1].get_collector("rate"))

        if i < rolls.n - 1 and np.sign(rolls.value[i]) == np.sign(rolls.value[i+1]):
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

def roll_f3a(name, rolls, speed, partial_rate, full_rate, pause_length, line_length, reversible=True, padded=True):

    mps = ManParms()
    if not isinstance(rolls, ManParm) and not isinstance(rolls, Opp):
        if isinstance(rolls, str):
            try:
                _rolls = ManParm.parse(rolls)
            except Exception as e:
                _rolls = ManParm(f"{name}_rolls", Combination.rollcombo(rolls, reversible), 0)
        elif isinstance(rolls, list):
            _rolls = ManParm(f"{name}_rolls", Combination.rolllist(rolls, reversible), 0) 
        elif isinstance(rolls, Number):
            if reversible:
                _rolls = ManParm(f"{name}_rolls", Combination([[rolls], [-rolls]]), 0)
            else:
                _rolls = ManParm(f"{name}_rolls", Combination([[rolls]]), 0)
        mps.add(_rolls)

    else:
        _rolls = rolls

    
    if isinstance(_rolls, ItemOpp):
        _r=_rolls.a.value[_rolls.item]
        rate = full_rate if abs(_r)>=2*np.pi else partial_rate
        eds, rcmps = roll(f"{name}_roll", speed, rate, _rolls)
    else:
        eds, rcmps = roll_combo_f3a(name, speed, _rolls, partial_rate, full_rate, pause_length)
    mps.add(rcmps)
            
    if padded:
        eds, padmps = pad(speed, line_length, eds)
        mps.add(padmps)

    return eds, mps

    
def snap(name, rolls, break_angle, rate, speed, break_rate, line_length=100, padded=True, reversible=True, pause_length=10):
    
    eds = ElDefs()
    mps = ManParms()

    if isinstance(break_angle, Number):
        break_angle = ManParm(
            "break_angle", 
            Combination(desired=[[break_angle], [-break_angle]]),
            0
        )
        mps.add(break_angle)
    
    
    #pitch break
    eds.add(ElDef.build(PitchBreak, f"{name}_break", speed=speed, 
        length=speed * abs(break_angle.value[0])/break_rate, break_angle=break_angle.value[0]))
    
    #autorotation
    if isinstance(rolls,ManParm):
        eds.add(ElDef.build(Autorotation, f"{name}_autorotation_{i}", speed=speed,
            length=speed*abs(_rolls)*2*np.pi/rate, roll=_rolls))
    else:
        if isinstance(rolls, Number):
            rolls = [rolls]

        if not isinstance(rolls, list):
            raise ValueError(f"Expected a list, number or ManParm, got {rolls}")

        _rolls = ManParm(f"{name}_rolls", Combination.rolllist(rolls, reversible), 0) 

        #TODO this should be combined with roll_combo_f3a
        for i, r in enumerate(_rolls.value):
            eds.add(
                ElDef.build(Autorotation, f"{name}_autorotation_{i}", speed=speed,
                    length=speed*abs(_rolls.value[i])*2*np.pi/rate, roll=_rolls.value[i])
            )
            if isinstance(rate, ManParm):
                rate.append(eds[-1].get_collector("rate"))
            if i < _rolls.n - 1 and np.sign(_rolls.value[i]) == np.sign(_rolls.value[i+1]):
                eds.add(line(
                    f"{name}_pause_{i+1}",
                    speed, pause_length, 0
                ))
    
    #recovery
    eds.add(ElDef.build(Recovery, f"{name}_recovery", speed=speed,
                    length=speed * abs(break_angle.value[0])/break_rate))
        
    if padded:
        eds, _mps =  pad(speed, line_length, eds)
        mps.add(_mps)

    return eds, mps


def spin(name, turns, break_angle, rate, speed, break_rate, reversible):
    
    nose_drop = ElDef.build(NoseDrop, f"{name}_break", speed=speed, 
                      radius=speed * break_angle/break_rate, break_angle=break_angle)
    
    autorotation = ElDef.build(Autorotation, f"{name}_autorotation", speed=speed,
                        length=(2 * np.pi * speed * turns)/rate, roll=turns)
    
    if isinstance(rate, ManParm):
        if isinstance(rate, ManParm):
            rate.collectors.add(autorotation.get_collector("rate"))

    recovery = ElDef.build(Recovery, f"{name}_recovery", speed=speed,
                    length=speed * break_angle/break_rate)
    return ElDefs([nose_drop, autorotation, recovery]), ManParms()
    