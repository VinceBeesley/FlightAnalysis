from json import loads
from flightanalysis.schedule.scoring.criteria import Criteria, Exponential, Continuous, Comparison, free, Single
from flightanalysis.data import get_json_resource

class F3ASingle:
    track=Single(Exponential(3.8197186342054863,1.000000000000001), 'absolute')
    roll=Single(Exponential(3.393716180082528,1.2618595071429148), 'absolute')
    angle=Single(Exponential(3.8197186342054863,1.000000000000001), 'absolute')
    distance=Single(Exponential(0.02499999999999858,1.0000000000000155), 'absolute')
class F3AIntra:
    track=Continuous(Exponential(3.8197186342054863,1.000000000000001), 'absolute')
    roll=Continuous(Exponential(3.393716180082528,1.2618595071429148), 'absolute')
    radius=Continuous(Exponential(0.25,1.8927892607143724), 'ratio')
    speed=Continuous(Exponential(0.14999999999999858,1.0000000000000058), 'ratio')
    roll_rate=Continuous(Exponential(0.14999999999999858,1.0000000000000058), 'ratio')
class F3AInter:
    radius=Comparison(Exponential(0.5,0.861353116146786), 'ratio')
    speed=Comparison(Exponential(0.25,0.861353116146786), 'ratio')
    roll_rate=Comparison(Exponential(0.14999999999999858,1.1787469216608066), 'ratio')
    length=Comparison(Exponential(0.5,1.1132827525593783), 'ratio')
    free=Comparison(Exponential(0,1), 'ratio')


class F3A:
    inter = F3AInter
    intra = F3AIntra
    single = F3ASingle


if __name__=='__main__':
    print(F3A.inter.radius)
    print(F3A.intra.radius)
    print(F3A.intra.roll)