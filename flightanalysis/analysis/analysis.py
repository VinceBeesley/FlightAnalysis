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
        pass
    
    @staticmethod
    def initial_transform(mdef: ManDef, flown: State):
        initial = flown[0]
        return Transformation(
            initial.pos,
            mdef.info.start.initial_rotation(
                mdef.info.start.d.get_wind(initial.direction()[0])
        ))

    @staticmethod
    def alignment(mdef: ManDef, flown: State):
        itrans = ManoeuvreAnalysis.initial_transform(mdef, flown)

        #add the exit line to the manoeuvre, which is present in the flown data
        man = Manoeuvre.from_all_elements(mdef.info.short_name, mdef.create(itrans).all_elements(True)) 
        tp = man.create_template(itrans)

        aligned = State.align(flown, tp, radius=10)[1]
        intended = man.match_intention(tp[0], aligned)[0]
        int_tp = intended.create_template(tp[0].transform, aligned)

        aligned = State.align(aligned, int_tp, radius=10, mirror=False)[1]
        aligned = aligned.get_subset(slice(None, -1, None), "element")

        #now the alignment is done, exit line can be removed from the flown data and the manoeuvre:        
        intended = Manoeuvre.from_all_elements(man.uid, intended.all_elements()[:-1])

        return ManoeuvreAnalysis.build_intended(mdef, intended, int_tp, aligned)    

    @staticmethod
    def build_aligned(mdef: ManDef, aligned: State):
        pass

    @staticmethod
    def build_intended(mdef, intended: Manoeuvre, int_tp: Manoeuvre,  aligned: State):       
        mdef.mps.update_defaults(intended)       

        corr = Manoeuvre(intended.entry_line, mdef._create().elements, mdef.info.short_name)
        corr_tp = corr.create_template(int_tp[0].transform, aligned)
        
        return ManoeuvreAnalysis(mdef, aligned, intended, int_tp, corr, corr_tp)
    

    def plot_3d(self, **kwargs):
        fig = plotsec(self.aligned, color="red", **kwargs)
        return plotsec(self.corrected_template, color="green", fig=fig, **kwargs)


class ScheduleAnalysis(Collection):
    VType=ManoeuvreAnalysis


if __name__ == "__main__":
    with open("examples/data/manual_F3A_P23_22_05_31_00000350.json", "r") as f:
        data = load(f)


    flight = Flight.from_fc_json(data)
    box = Box.from_fcjson_parmameters(data["parameters"])
    state = State.from_flight(flight, box).splitter_labels(data["mans"])
    sdef = get_schedule_definition(data["parameters"]["schedule"][1])

    analyses = ScheduleAnalysis()

    for mid in range(17):
        analyses.add(ManoeuvreAnalysis.build(sdef[mid], state.get_meid(mid+1)))

    scores = []

    for ma in analyses:
        scores.append(dict(
            name=ma.mdef.info.name,
            k=ma.mdef.info.k,
            pos_dg=np.sum(abs(ma.aligned.pos - ma.corrected_template.pos) * ma.aligned.dt / 500),
            roll_dg = np.sum(np.abs(Quaternion.body_axis_rates(ma.aligned.att, ma.corrected_template.att).x) * ma.aligned.dt / 40)
        ))

    scores = pd.DataFrame(scores)
    scores["score"] = 10 - scores.pos_dg - scores.roll_dg
    if "scores" in data:
        scores["manual_scores"] = data["scores"][1:-1]
        
    print(scores)
    print(f"total = {sum(scores.score * scores.k)}")
    

    

    
