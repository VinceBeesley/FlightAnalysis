from json import load

from flightanalysis.schedule.scoring.criteria import Criteria


class Crit:
    def __init__(self, data):
        self.data = data

    def __getattr__(self, name):
        return self.data[name]
    

with open('flightanalysis/schedule/scoring/criteria/f3a_criteria.json', 'r') as f:
    data = load(f)

f3adicts = {}
for cname, crits in data.items():
    ndict = {}
    for name, crit in crits.items():
        ndict[name] = Criteria.from_dict(crit)
    f3adicts[cname] = Crit(ndict)

f3a = Crit(f3adicts)

if __name__=='__main__':
    print(f3a.inter.radius)
    print(f3a.intra.radius)
    print(f3a.intra.roll)