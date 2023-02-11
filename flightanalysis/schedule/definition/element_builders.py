from .element_definition import ElDef, ElDefs
from flightanalysis.schedule.elements import *

def line(name, speed, length, roll):
    return ElDef.build(Line, name, speed, length, roll)

def loop(name, speed, radius, angle, roll, ke):
    return ElDef.build(Loop, name, speed, radius, angle, roll, ke)

def roll(name, speed, rate, angle):
    return ElDef.build(Line, name, speed, abs(angle) * speed / rate, angle)

