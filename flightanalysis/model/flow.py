
from flightanalysis.base.table import Table, Time, SVar
from typing import Union
from flightdata import Flight, Fields
from pathlib import Path
from flightanalysis.base.constructs import Constructs, SVar
from flightanalysis.state import State
from flightanalysis.environment import Environment
from geometry import Point, Quaternion, Base, PX
import numpy as np



class Attack(Base):
    cols = ['alpha', 'beta', 'q']


class Flow(Table):
    constructs = Table.constructs + Constructs(dict(
        aspd = SVar(Point, ["asx", "asy", "asz"], None),
        flow = SVar(Point, ["alpha", "beta", "q"], None)
    ))

    @staticmethod
    def build(body: State, env: Environment):
#        wind = judge.judging_to_wind(env.wind)
        airspeed = body.vel - body.att.inverse().transform_point(env.wind)

        sym_airspeed = Point(1,0,1) * airspeed

        beta = airspeed.angle_between(sym_airspeed)

        x_arspd = Point(1,0,0) * sym_airspeed

        alpha = sym_airspeed.angle_between(x_arspd)

        q = 0.5 * env.rho * abs(airspeed)**2

        return Flow.from_constructs(
            body.time, 
            airspeed,
            Attack(alpha, beta, q)
        )