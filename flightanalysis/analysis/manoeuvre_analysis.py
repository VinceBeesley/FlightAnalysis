from __future__ import annotations
import numpy as np
import pandas as pd
from json import load
from flightanalysis import State, Manoeuvre, State, ManDef, ElDef, Box, get_schedule_definition, Collection
from flightanalysis.schedule.elements import El
from geometry import Transformation, Quaternion, Q0
from typing import Any, List, Tuple



class ElementAnalysis:
    def __init__(self, edef:ElDef, el: El, fl: State, tp: State):
        self.edef = edef
        self.el = el
        self.fl=fl
        self.tp = tp
        self.coord = self.el.coord(self.tp)

    def __repr__(self) -> str:
        return f"ElementAnalysis({self.edef.name}, {self.el.__class__.__name__})"

    def plot_3d(self, **kwargs):
        fig = plotsec(self.fl, color="red", **kwargs)
        return plotsec(self.tp, color="green", fig=fig, **kwargs)



class ManoeuvreAnalysis:
    def __init__(self, mdef: ManDef, aligned: State, intended: Manoeuvre, intended_template: State, corrected: Manoeuvre, corrected_template: State):
        self.mdef = mdef
        self.aligned = aligned
        self.intended = intended
        self.intended_template = intended_template
        self.corrected = corrected
        self.corrected_template = corrected_template
    
    def __getitem__(self, i):
        return self.get_ea(self.mdef.eds[i])

    def __getattr__(self, name):
        if name in self.mdef.eds.data.keys():
            return self.get_ea(self.mdef.eds[name])
        raise AttributeError()

    def get_ea(self, edef):
        el = getattr(self.intended.elements, edef.name)
        st = el.get_data(self.aligned)
        return ElementAnalysis(
            edef,
            el,
            st,
            el.get_data(self.intended_template).relocate(st.pos[0])
        )

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
    def initial_transform(mdef: ManDef, flown: State):
        initial = flown[0]
        return Transformation(
            initial.pos,
            mdef.info.start.initial_rotation(
                mdef.info.start.d.get_wind(initial.direction()[0])
        ))
    
    @staticmethod
    def template(mdef: ManDef, itrans: Transformation) -> Tuple[Manoeuvre, State]:
        man = mdef.create(itrans).add_lines()
        return man, man.create_template(itrans)

    @staticmethod
    def alignment(template: State, man: Manoeuvre, flown: State) -> State:
        aligned = State.align(flown, template, radius=10)[1]
        int_tp = man.match_intention(template[0], aligned)[1]
        
        return State.align(aligned, int_tp, radius=10, mirror=False)[1]

    @staticmethod
    def intention(man: Manoeuvre, aligned: State, template: State) -> Tuple[Manoeuvre, State]:
        return man.match_intention(template[0], aligned)

    @staticmethod
    def correction(mdef: ManDef, intended: Manoeuvre, int_tp: State, aligned: State) -> Tuple(Manoeuvre, State):
        mdef.mps.update_defaults(intended)       

        corr = mdef.create(int_tp[0].transform).add_lines()
        corr_tp = corr.create_template(int_tp[0].transform, aligned)
        
        return corr, corr_tp

    @staticmethod
    def build(mdef: ManDef, flown: State):
        itrans = ManoeuvreAnalysis.initial_transform(mdef, flown)
        man, tp = ManoeuvreAnalysis.template(mdef, itrans)
        aligned = ManoeuvreAnalysis.alignment(tp, man, flown)
        intended, int_tp = ManoeuvreAnalysis.intention(man, aligned, tp)
        corr, corr_tp = ManoeuvreAnalysis.correction(mdef, intended, int_tp, aligned)
        return ManoeuvreAnalysis(mdef, aligned, intended, int_tp, corr, corr_tp)

    def plot_3d(self, **kwargs):
        from flightplotting import plotsec, plotdtw
        fig = plotsec(self.aligned, color="red", **kwargs)
        return plotsec(self.corrected_template, color="green", fig=fig, **kwargs)



class ScheduleAnalysis(Collection):
    VType=ManoeuvreAnalysis


if __name__ == "__main__":
    from flightdata import Flight
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
    

    

    
