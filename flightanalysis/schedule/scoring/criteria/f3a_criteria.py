from json import loads
from flightanalysis.schedule.scoring.criteria import Criteria, Exponential, Continuous, Comparison, free, Single
from flightanalysis.data import get_json_resource

import numpy as np

class F3ASingle:
    track=Criteria(Exponential(3.8197186342054863,1.000000000000001), 'absolute')
    roll=Criteria(Exponential(3.1486776615143057,1.4278157399964433), 'absolute')
    angle=Criteria(Exponential(3.8197186342054863,1.000000000000001), 'absolute')
    distance=Criteria(Exponential(0.005968628275915933,1.7095112913516006), 'absolute')
class F3AIntra:
    track=Continuous(Exponential(4.186644340484932,0.7968859864249862), 'absolute')
    roll=Continuous(Exponential(3.1486776615143057,1.4278157399964433), 'absolute')
    radius=Continuous(Exponential(1.1177196883578588,1.1605584217036227), 'ratio')
    speed=Continuous(Exponential(0.5,0.25192963641259203), 'ratio')
    roll_rate=Continuous(Exponential(0.5,0.25192963641259203), 'ratio')
class F3AInter:
    radius=Comparison(Exponential(0.5,0.861353116146786), 'ratio')
    speed=Comparison(Exponential(0.5,0.25192963641259203), 'ratio')
    roll_rate=Comparison(Exponential(0.5,0.4306765580733929), 'ratio')
    length=Comparison(Exponential(1.0,0.6826061944859854), 'ratio')
    free=Comparison(Exponential(0,1), 'ratio')


class F3A:
    inter = F3AInter
    intra = F3AIntra
    single = F3ASingle


if __name__=='__main__':
    print(F3A.inter.radius)
    print(F3A.intra.radius)
    print(F3A.intra.roll)