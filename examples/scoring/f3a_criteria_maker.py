from flightanalysis.schedule.scoring.criteria import *
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from json import dump


f3a=dict(
    single=dict(
        track=Criteria(Exponential.fit_points(np.radians([30, 90]), [2, 6]), 'absolute'),
        roll=Criteria(Exponential.fit_points(np.radians([30, 90]), [1.25, 6]), 'absolute'),
        angle=Criteria(Exponential.fit_points(np.radians([30, 90]), [2, 6]), 'absolute'),
        distance=Criteria(Exponential.fit_points([20, 30], [1,2]), 'absolute')
    ),
    intra=dict(
        track=Continuous(Exponential.fit_points(np.radians([30, 90]), [2.5, 6]), 'absolute'),
        roll=Continuous(Exponential.fit_points(np.radians([30, 90]), [1.25, 6]), 'absolute'),
        radius=Continuous(Exponential.fit_points([0.5,3], [0.5, 4]), 'ratio'),
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

    with open('examples/scoring/temp.py', 'w') as f:
        for group, v in f3a.items():
            f.write(f'class F3A{group.capitalize()}:\n')
            for n, crit in v.items():
                f.write(f'    {n}={crit.to_py()}\n')

