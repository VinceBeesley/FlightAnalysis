
from flightanalysis import Table, Time, SVar, Constructs, SVar
from geometry import Point, Base, PX, Euler
import numpy as np


class Attack(Base):
    cols = ['alpha', 'beta', 'q']


class Flow(Table):
    constructs = Table.constructs + Constructs([
        SVar("aspd", Point, ["asx", "asy", "asz"], None),
        SVar("flow", Point, ["alpha", "beta", "q"], None)
    ])

    @staticmethod
    def build(body, env):
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
