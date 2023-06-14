from json import load
from flightanalysis.base import Collection
from flightanalysis.state import State
from flightanalysis.flightline import Box
from flightanalysis.data import get_schedule_definition
from flightanalysis.schedule import *
from flightdata import Flight
from geometry import Transformation, Quaternion, Q0
import numpy as np
import pandas as pd
from flightplotting import plotsec, plotdtw
from typing import List


class ManoeuvreAnalysis:
    def __init__(self, mdef: ManDef, aligned: State, intended: Manoeuvre, intended_template: State, corrected: Manoeuvre, corrected_template: State):
        self.mdef = mdef
        self.aligned = aligned
        self.intended = intended
        self.intended_template = intended_template
        self.corrected = corrected
        self.corrected_template = corrected_template

        self.pos_error = self.aligned.pos - self.corrected_template.pos
        self.roll_error = Quaternion.body_axis_rates(self.aligned.att, self.corrected_template.att).x

        #TODO factor by visibility, replace abs here with something cleverer. Add some logic to the arbitrary fudge factors
        self.pos_dg = np.cumsum(abs(self.pos_error) * self.aligned.dt / 500)
        self.roll_dg = np.cumsum(np.abs(self.roll_error) * self.aligned.dt / 40)

        self.score = 10 - self.pos_dg[-1] - self.roll_dg[-1]
    
    def to_dict(self):
        return dict(
            mdef = self.mdef.to_dict(),
            aligned = self.aligned.to_dict(),
            intended = self.intended.to_dict(),
            intended_template = self.intended_template.to_dict(),
            corrected = self.corrected.to_dict(),
            corrected_template = self.corrected_template.to_dict(),
        )

    @staticmethod
    def from_dict(data:dict):
        return ManoeuvreAnalysis(
            ManDef.from_dict(data["mdef"]),
            State.from_dict(data["aligned"]),
            Manoeuvre.from_dict(data["intended"]),
            State.from_dict(data["intended_template"]),
            Manoeuvre.from_dict(data["corrected"]),
            State.from_dict(data["corrected_template"]),
        )

    @property
    def uid(self):
        return self.mdef.uid

    @staticmethod
    def build(mdef: ManDef, flown: State):

        itrans = Transformation(
            flown[0].pos,
            mdef.info.start.initial_rotation(
                mdef.info.start.d.get_wind(flown.direction()[0])
        ))

        # this is weird, but it adds the exit line to the manoeuvre, which is present in the flown data
        man = Manoeuvre.from_all_elements(mdef.info.short_name, mdef.create(itrans).all_elements(True)) 
        tp = man.create_template(itrans)

        aligned = State.align(flown, tp, radius=10)[1]

        intended = man.match_intention(tp[0], aligned)[0]
        int_tp = intended.create_template(itrans, aligned)

        aligned = State.align(flown, int_tp, radius=10, mirror=False)[1]

        #now the alignment is done, exit line can be removed from the flown data and the manoeuvre:
        aligned = aligned.get_subset(slice(None, -1, None), "element")
        man = Manoeuvre.from_all_elements(man.uid, man.all_elements()[:-1])

        intended = man.match_intention(tp[0], aligned)[0]
        int_tp = intended.create_template(itrans, aligned)
        
        mdef.mps.update_defaults(intended)       

        corr = Manoeuvre(intended.entry_line, mdef._create().elements, mdef.info.short_name)
        corr_tp = corr.create_template(itrans, aligned)
        
        return ManoeuvreAnalysis(mdef, aligned, intended, int_tp, corr, corr_tp)




    def plot_3d(self, **kwargs):
        fig = plotsec(self.aligned, color="red", **kwargs)
        return plotsec(self.corrected_template, color="green", fig=fig, **kwargs)

    def plot_dg(self):
        import plotly.graph_objects as go

        fig = go.Figure()

        fig.add_trace(go.Line(y=self.pos_dg))
        fig.add_trace(go.Line(y=self.roll_dg , yaxis="y2"))
        fig.update_layout(
            yaxis=dict(
                title="position error"
            ), 
            yaxis2=dict(title="roll error",
                overlaying="y",
                side="right",)
        )
        fig.show()

class ScheduleAnalysis(Collection):
    VType=ManoeuvreAnalysis

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def summary_df(self):
        return pd.DataFrame(
            [[an.mdef.info.short_name, an.mdef.info.k, an.score] for an in self], 
            columns=["name", "k", "score"]
        )

    def total_score(self):
        df = self.summary_df()
        return sum(df.k * df.score)


if __name__ == "__main__":
    with open("examples/data/manual_F3A_P23_22_05_31_00000350.json", "r") as f:
        data = load(f)


    flight = Flight.from_fc_json(data)
    box = Box.from_fcjson_parmameters(data["parameters"])
    state = State.from_flight(flight, box).splitter_labels(data["mans"])
    sdef = get_schedule_definition(data["parameters"]["schedule"][1])

    analyses: List[ManoeuvreAnalysis] = []

    for mid in range(17):
        analyses.append(ManoeuvreAnalysis.build(sdef[mid], state.get_meid(mid+1)))

    df = pd.DataFrame([[an.mdef.info.short_name, an.score, an.mdef.info.k] for an in analyses], columns=["name", "score", "k"])
    if "scores" in data:
        df["manual_scores"] = data["scores"][1:-1]
        
    print(df)
    print(f"total = {sum(df.score * df.k)}")
    pass

    

    
