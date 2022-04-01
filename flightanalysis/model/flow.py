
from flightanalysis.base.table import Table, Time, SVar
from typing import Union
from flightdata import Flight, Fields
from pathlib import Path
from flightanalysis.base.constructs import Constructs, SVar
from flightanalysis.state import State
from flightanalysis.environment import Environment
from geometry import Point, Quaternion, Base, PX, Euler
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

        np.seterr(invalid='ignore')
        alpha =  np.arctan(airspeed.z / airspeed.x) 
        
        stab_airspeed = Euler(
            np.zeros(len(alpha)), 
            alpha, 
            np.zeros(len(alpha))
        ).transform_point(airspeed)
        #assert np.app(stab_airspeed.z == 0)

        beta = np.arctan(stab_airspeed.y / stab_airspeed.x)

        np.seterr(invalid='warn')
        q = 0.5 * env.rho * abs(airspeed)**2

        return Flow.from_constructs(
            body.time, 
            airspeed,
            Attack(alpha, beta, q)
        )
