from __future__ import annotations
import numpy as np
import pandas as pd
from json import load
from flightanalysis import State, Manoeuvre, State, ManDef, ElDef, Box, get_schedule_definition, Collection
from flightanalysis.schedule.elements import Element
from flightanalysis.schedule.scoring import *
from flightanalysis.schedule.definition.manoeuvre_info import Position
from geometry import Transformation, Quaternion, Q0, Coord
from typing import Any, List, Tuple
from dataclasses import dataclass


@dataclass
class ElementAnalysis:
    edef:ElDef
    el: Element
    fl: State
    tp: State
    coord: Coord

    def plot_3d(self, **kwargs):
        from flightplotting import plotsec
        fig = plotsec(self.fl, color="red", **kwargs)
        return plotsec(self.tp, color="green", fig=fig, **kwargs)


@dataclass
class ManoeuvreAnalysis:
    mdef: ManDef
    aligned: State
    intended: Manoeuvre
    intended_template: State
    corrected: Manoeuvre
    corrected_template: State
    
    def __getitem__(self, i):
        return self.get_ea(self.mdef.eds[i])

    def __getattr__(self, name):
        if name in self.mdef.eds.data.keys():
            return self.get_ea(self.mdef.eds[name])
        raise AttributeError()

    def get_ea(self, edef):
        el = getattr(self.intended.elements, edef.name)
        st = el.get_data(self.aligned)
        tp = el.get_data(self.intended_template).relocate(st.pos[0])
        return ElementAnalysis(edef,el,st,tp, el.coord(tp))

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
        from flightplotting import plotsec
        from flightplotting import plotsec, plotdtw
        fig = plotsec(self.aligned, color="red", **kwargs)
        return plotsec(self.corrected_template, color="green", fig=fig, **kwargs)


    def side_box(self):
        al = self.aligned#.get_element(slice(1,-1,None))
        side_box_angle = np.arctan2(al.pos.x, al.pos.y)

        if self.mdef.info.position == Position.CENTRE:
            if self.mdef.info.centre_loc == -1:
                centre = max(side_box_angle) + min(side_box_angle)
            else:
                centre_pos = self.intended.elements[self.mdef.info.centre_loc].get_data(self.aligned).pos[0]
                centre = np.arctan2(centre_pos.x, centre_pos.y)[0]
            box_dg = f3a.angle(centre)
            return Result("centering",np.array([centre]),np.array([box_dg]))
        else:
            max_sb = max(abs(side_box_angle))
            min_sb = min(abs(side_box_angle))

            outside = 1 - (1.0471975511965976 - min_sb) / (max_sb - min_sb)
            box_dg = max(outside, 0) * 5
            return Result("box",np.array([outside]),np.array([box_dg]))

    def top_box(self):
        top_box_angle = max(np.arctan(self.aligned.pos.z / self.aligned.pos.y))

        outside_tb = (top_box_angle - 1.0471975511965976) / 1.0471975511965976
        top_box_dg = max(outside_tb, 0) * 6
        return Result("top box", np.array([outside_tb]), np.array([top_box_dg]))

    def distance(self):
        #only downgrade distance if the template is narrow
        #TODO doesnt quite cover it, stalled manoeuvres need to be considered
        dist = np.mean(self.aligned.pos.y)

        tp_width = max(self.corrected_template.y) - min(self.corrected_template.y)

        if tp_width < 10:
            dist_dg = f3a.distance(max(dist, 170))
        else:
            dist_dg = 0.0
        return Result("distance", np.array([dist]), np.array([dist_dg])) 

class ScheduleAnalysis(Collection):
    VType=ManoeuvreAnalysis


if __name__ == "__main__":
    from flightdata import Flight
    from flightplotting import plotsec
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
    

    

    
