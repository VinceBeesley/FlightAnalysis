from .element_definition import ElDef, ElDefs, ManParm, ManParms
from flightanalysis.schedule.elements import *
from flightanalysis.base.collection import Collection
from flightanalysis.schedule.definition.collectors import Collectors


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
    #this creates pauses between opposing rolls and has a different rate for full and
    #part rolls.
    eds = ElDefs()
    
    last_direction = np.sign(rolls.value[0])
    for i, r in enumerate(rolls.value):
        new_roll = eds.add(roll(
            f"{name}_{i}",
            speed,
            partial_rate if abs(rolls.value[i]) < 1 else full_rate,
            rolls.value[i]
        ))

        if i < rolls.n - 1 and np.sign(rolls.value[i]) == np.sign(rolls.value[i+1]):
            new_pause = eds.add(line(
                f"{name}_{i+1}_pause",
                speed, pause_length, 0
            ))
                
    return eds, ManParms()


def pad(speed, line_length, eds: ElDefs):
    
    pad_length = 0.5 * (line_length - eds.builder_sum("length"))
    
    e1, mps = line(f"e_{eds[0].id}_pad1", speed, pad_length, 0)
    e3, mps = line(f"e_{eds[0].id}_pad2", speed, pad_length, 0)
    
    mp = ManParm(
        f"e_{eds[0].id}_pad_length", 
        criteria, 
        None, 
        Collectors([e1.get_collector("length"), e3.get_collector("length")])
    )
    
    return ElDefs([e1] + [ed for ed in eds] + [e3]), ManParms([mp])

def roll_f3a(name, rolls, speed, partial_rate, full_rate, pause_length, line_length=100, reversible=True, padded=True):
    if isinstance(rolls, str):
        _rolls = ManParm(f"{name}_rolls", Combination.rollcombo(rolls, reversible), 0)
    elif isinstance(rolls, list):
        _rolls = ManParm(f"{name}_rolls", Combination.rolllist(rolls, reversible), 0) 
    else:
        _rolls=rolls
    
    if isinstance(_rolls, ManParm):
        eds, mps = roll_combo_f3a(name, speed, _rolls, partial_rate, full_rate, pause_length)
    else:
        eds = ElDefs([roll(f"{name}_roll", speed, partial_rate, _rolls)[0]])
        
    if padded:
        eds, mps = pad(speed, line_length, eds)

    return eds, mps.add(_rolls)

    
def snap(name, rolls, break_angle, rate, speed, break_rate, line_length=100, padded=True):
    pitch_break = ElDef.build(PitchBreak, f"{name}_break", speed=speed, 
                      length=speed * break_angle/break_rate, break_angle=break_angle)
    
    autorotation = ElDef.build(Autorotation, f"{name}_autorotation", speed=speed,
                        length=speed * rolls*2*np.pi/rate, roll=rolls)
    
    if isinstance(rate, ManParm):
        rate.append(autorotation.get_collector("rate"))
    
    recovery = ElDef.build(Recovery, f"{name}_recovery", speed=speed,
                    length=speed * break_angle/break_rate)
    
    eds = ElDefs([pitch_break, autorotation, recovery])
    
    if padded:
        return pad(speed, line_length, eds)
    else:
        return eds, ManParms()
        

def spin(name, turns, break_angle, rate, speed, break_rate, reversible):
    
    nose_drop = ElDef.build(NoseDrop, f"{name}_break", speed=speed, 
                      radius=speed * break_angle/break_rate, break_angle=break_angle)
    
    autorotation = ElDef.build(Autorotation, f"{name}_autorotation", speed=speed,
                        length=(2 * np.pi * speed * turns)/rate, roll=turns)
            
    recovery = ElDef.build(Recovery, f"{name}_recovery", speed=speed,
                    length=speed * break_angle/break_rate)
    return ElDefs([nose_drop, autorotation, recovery]), ManParms()
    