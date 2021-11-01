from flightanalysis import Snap

from flightanalysis import Section, Line, Snap
from geometry import Transformation, Point
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flightplotting.plots import plotsec
from flightplotting.traces import axis_rate_trace, control_input_trace, aoa_trace
import numpy as np
from geometry import Quaternion

nb_layout = dict(width=800, 
        height=300, 
        margin=dict(l=5, r=5, t=5, b=1), 
        legend=dict(yanchor="top", xanchor="left", x=0.8, y=0.99)
        )


line_before = Line(2).create_template(Transformation(rotation=Quaternion.from_euler((np.pi, 0, 0))), 30)

snap = Snap(1.25).scale(170).create_template(line_before[-1].transform, 30)

line_after = Line(2).create_template(snap[-1].transform, 30)

snap = Section.stack([line_before, snap,  line_after])


def plotsnap(sec):
    fig = plotsec(sec, nmodels=10, scale=2, show_axes = True, color="grey")
    fig.update_layout(width=1200, height=800, margin=dict(l=0, r=0, t=0, b=0))
    return fig


plotsnap(snap).show()