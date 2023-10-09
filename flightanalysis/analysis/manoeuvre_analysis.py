from __future__ import annotations
import numpy as np
import pandas as pd
from json import load

from flightdata import Flight
from flightanalysis import State, Manoeuvre, State, ManDef, ElDef, Box, Collection, SchedDef
from flightanalysis.schedule.elements import Element
from flightanalysis.schedule.scoring import *
from flightanalysis.schedule.scoring.criteria.f3a_criteria import F3A
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
    ref_frame: Transformation

    def plot_3d(self, **kwargs):
        from flightplotting import plotsec
        return plotsec([self.fl, self.tp], 2, 5, origin=True)

    def to_dict(self):
        return {k: v.to_dict() for k, v in self.__dict__.items()}


@dataclass
class ManoeuvreResults:
    inter: Results
    intra: ElementsResults
    side_box: Result
    top_box: Result
    centre: Result
    distance: Result

    def summary(self):
        return {k: v.total for k, v in self.__dict__.items() if not v is None} 

    def score(self):
        return max(0, 10 - sum([v for v in self.summary().values()]))
    
    def to_dict(self):
        return dict(
            inter=self.inter.to_dict(),
            intra=self.intra.to_dict(),
            side_box=self.side_box.to_dict() if self.side_box else 0,
            top_box=self.top_box.to_dict(),
            centre=self.centre.to_dict() if self.centre else 0,
            distance=self.distance.to_dict(),
            summary=self.summary(),
            score=self.score()
        )

    @staticmethod
    def from_dict(data):
        return Manoeuvre(
            Results.from_dict(data['inter']),
            ElementsResults.from_dict(data['intra']),
            Result.from_dict(data['side_box']) if data['side_box'] else None,
            Result.from_dict(data['top_box']),
            Result.from_dict(data['centre']) if data['centre'] else None,
            Result.from_dict(data['distance'])
        )


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
        return ElementAnalysis(edef,el,st,tp, el.ref_frame(tp))

    def to_dict(self):
        return dict(
            mdef = self.mdef.to_dict(),
            aligned = self.aligned.to_dict(),
            intended = self.intended.to_dict(),
            intended_template = self.intended_template.to_dict(),
            corrected = self.corrected.to_dict(),
            corrected_template = self.corrected_template.to_dict()
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
    def initial_transform(mdef: ManDef, flown: State) -> Transformation:
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
    def alignment(template: State, man: Manoeuvre, flown: State, radius=10) -> Tuple(float, State):
        aligned = State.align(flown, template, radius=10)[1]
        int_tp = man.match_intention(template[0], aligned)[1]
        return State.align(aligned, int_tp, radius=radius, mirror=False)

    @staticmethod
    def intention(man: Manoeuvre, aligned: State, template: State) -> Tuple[Manoeuvre, State]:
        return man.match_intention(template[0], aligned)

    @staticmethod
    def correction(mdef: ManDef, intended: Manoeuvre, int_tp: State, aligned: State) -> Manoeuvre:
        mdef.mps.update_defaults(intended)       
        return mdef.create(int_tp[0].transform).add_lines()

    @staticmethod
    def build(mdef: ManDef, flown: State):
        itrans = ManoeuvreAnalysis.initial_transform(mdef, flown)
        man, tp = ManoeuvreAnalysis.template(mdef, itrans)
        aligned = ManoeuvreAnalysis.alignment(tp, man, flown)[1]
        intended, int_tp = ManoeuvreAnalysis.intention(man, aligned, tp)
        corr = ManoeuvreAnalysis.correction(mdef, intended, int_tp, aligned)
        return ManoeuvreAnalysis(mdef, aligned, intended, int_tp, corr, corr.create_template(int_tp[0], aligned))

    def plot_3d(self, **kwargs):
        from flightplotting import plotsec
        fig = plotsec(self.aligned, color="red", **kwargs)
        return plotsec(self.intended_template, color="green", fig=fig, **kwargs)


    def side_box(self):
        al = self.aligned#.get_element(slice(1,-1,None))
        side_box_angle = np.arctan2(al.pos.x, al.pos.y)

        max_sb = max(abs(side_box_angle))
        min_sb = min(abs(side_box_angle))

        outside = 1 - (1.0471975511965976 - min_sb) / (max_sb - min_sb)
        box_dg = max(outside, 0.0) * 5.0
        return Result(
            "box",
            [max_sb, min_sb],
            [],
            [outside],
            [box_dg],
            []
        )

    def top_box(self):
        top_box_angle = np.arctan(self.aligned.pos.z / self.aligned.pos.y)
        tb = max(top_box_angle)
        outside_tb = (tb - 1.0471975511965976) / 1.0471975511965976
        top_box_dg = max(outside_tb, 0) * 6
        return Result("top box", [], [tb], [outside_tb], [top_box_dg], [])

    def centre(self):
        al = self.aligned.get_element(slice(1,-1,None))
        side_box_angle = np.arctan2(al.pos.x, al.pos.y)
        if self.mdef.info.centre_loc == -1:
            centre = max(side_box_angle) + min(side_box_angle)
        else:
            centre_pos = self.intended.elements[self.mdef.info.centre_loc].get_data(self.aligned).pos[0]
            centre = np.arctan2(centre_pos.x, centre_pos.y)[0]
        box_dg = F3A.single.angle.lookup(abs(centre))
        return Result("centering",[],[],[centre],[box_dg],[0])

    def distance(self):
        #TODO doesnt quite cover it, stalled manoeuvres could drift to > 170 for no downgrade
        tp_width = max(self.corrected_template.y) - min(self.corrected_template.y) #only downgrade distance if the template is narrow
        dist_key = np.argmax(self.aligned.pos.y)
        dist = self.aligned.pos.y[dist_key]
        if tp_width < 10:
            dist_key = np.argmax(self.aligned.pos.y)
            dist = self.aligned.pos.y[dist_key]
            dist_dg = F3A.single.distance.lookup(max(dist, 170) - 170)
        else:
            dist_dg = 0.0
        return Result("distance", [], [],[dist],[dist_dg],dist_key)

    def intra(self):
        return self.intended.analyse(self.aligned, self.intended_template)

    def inter(self):
        return self.mdef.mps.collect(self.intended, self.intended_template)

    def scores(self):
        
        intra = self.intra()
        
        inter = self.inter()

        return ManoeuvreResults(
            inter, intra, 
            self.side_box() if self.mdef.info.position == Position.END else None, 
            self.top_box(), 
            self.centre()if self.mdef.info.position == Position.CENTRE else None, 
            self.distance()
        )
    
    @staticmethod
    def from_fcj(file: str, mid: int):
        with open(file, 'r') as f:
            data = load(f)
        flight = Flight.from_fc_json(data)
        box = Box.from_fcjson_parmameters(data["parameters"])

        sdef = SchedDef.load(data["parameters"]["schedule"][1])

        state = State.from_flight(flight, box).splitter_labels(
            data["mans"],
            [m.info.short_name for m in sdef]
        )
        mas=[]
        mdef= sdef[mid]
        return ManoeuvreAnalysis.build(
            mdef, 
            state.get_manoeuvre(mdef.info.short_name)
        )


class ScheduleAnalysis(Collection):
    VType=ManoeuvreAnalysis

    @staticmethod
    def from_fcj(file: str):
        with open(file, 'r') as f:
            data = load(f)

        flight = Flight.from_fc_json(data)
        box = Box.from_fcjson_parmameters(data["parameters"])

        sdef = SchedDef.load(data["parameters"]["schedule"][1])

        state = State.from_flight(flight, box).splitter_labels(
            data["mans"],
            [m.info.short_name for m in sdef]
        )
        mas=[]
        for mdef in sdef:
            mas.append(ManoeuvreAnalysis.build(
                mdef, 
                state.get_manoeuvre(mdef.info.short_name)
            ))
        
        return ScheduleAnalysis(mas)



if __name__ == "__main__":
    from flightdata import Flight
    from flightplotting import plotsec
    from flightanalysis import SchedDef
    with open("examples/data/manual_F3A_P23_22_05_31_00000350.json", "r") as f:
        data = load(f)


    flight = Flight.from_fc_json(data)
    box = Box.from_fcjson_parmameters(data["parameters"])
    state = State.from_flight(flight, box).splitter_labels(data["mans"])
    sdef = SchedDef.load(data["parameters"]["schedule"][1])

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
    

    

    
