from .element_definition import ElDef, ElDefs, ManParm, ManParms
from flightanalysis.schedule.elements import *
from flightanalysis.base.collection import Collection


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
    for i, r in enumerate(rolls):
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
    
    pad_length = 0.5 * (line_length - eds.collector_sum("length"))
    
    e1 = line(f"e_{eds[0].id}_0", speed, pad_length, 0)
    e3 = line(f"e_{eds[0].id}_2", speed, pad_length, 0)
    return ElDefs([e1] + [ed for ed in eds] + e3), ManParms([pad_length])

