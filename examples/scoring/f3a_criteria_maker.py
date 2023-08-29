from flightanalysis.schedule.scoring import *
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from json import dump


f3a=dict(
    single=dict(
        track=Criteria(Exponential.fit_points(np.radians([30, 90]), [2, 6]), 'absolute'),
        roll=Criteria(Exponential.fit_points(np.radians([30, 90]), [1.25, 6]), 'absolute')
    ),
    intra=dict(
        track=Continuous(Exponential.fit_points(np.radians([30, 90]), [2.5, 6]), 'absolute'),
        roll=Continuous(Exponential.fit_points(np.radians([30, 90]), [1.25, 6]), 'absolute'),
        radius=Continuous(Exponential.fit_points([1,5], [2, 4]), 'ratio'),
        speed=Continuous(Exponential.fit_points([1,5], [0.5, 0.75]), 'ratio'),
        roll_rate=Continuous(Exponential.fit_points([1,5], [0.5, 0.75]), 'ratio'),
    ),
    inter=dict(
        radius=Comparison(Exponential.fit_points([1,5], [0.5, 2]), 'ratio'),
        speed=Comparison(Exponential.fit_points([1,5], [0.5, 0.75]), 'ratio'),
        roll_rate=Comparison(Exponential.fit_points([1,5], [0.5, 1]), 'ratio'),
        length=Comparison(Exponential.fit_points([1,5], [1, 3]), 'ratio'),
        free=Comparison(free, 'ratio'),
    )
)


if __name__ == "__main__":
    f3adicts = {}
    for cname, crits in f3a.items():
        f3adicts[cname] = {}
        for name, crit in crits.items():
            f3adicts[cname][name] = crit.to_dict()

    with open('flightanalysis/schedule/scoring/criteria/f3a_criteria.json', 'w') as f:
        dump(f3adicts, f)

