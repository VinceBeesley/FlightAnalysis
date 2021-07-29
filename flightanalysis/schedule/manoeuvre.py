from uuid import uuid4
from geometry import Transformation
from flightanalysis import Section
from flightanalysis.schedule.element import LoopEl, LineEl, StallTurnEl, SnapEl, SpinEl
from flightanalysis.schedule.figure_rules import F3AEnd, F3ACentre, F3AEndB, IMAC
from uuid import uuid4
import numpy as np
import pandas as pd
from enum import Enum


class Manoeuvre():
    def __init__(self, name: str, k: float, elements: list, rule=IMAC, uid: str = None):
        self.name = name
        self.k = k
        self.elements = elements   # TODO I'd like to access element info like in a dataframe
        self.rule = rule #

#        self._elmdf = pd.DataFrame([elm.to_dict() for elm in self.elements])

        self._elm_lookup = {elm.uid: elm for elm in self.elements}
        if not uid:
            self.uid = str(uuid4())
        else:
            self.uid = uid

    def scale(self, factor: float):
        return self.replace_elms([elm.scale(factor) for elm in self.elements])

    def create_template(self, transform: Transformation, speed: float) -> Section:
        itrans = transform
        #print("Manoeuvre : {}".format(manoeuvre.name))
        templates = []
        for i, element in enumerate(self.elements):
            templates.append(element.create_template(itrans, speed))
            itrans = templates[-1].get_state_from_index(-1).transform
            #print("element {0}, {1}".format(element.classification, (itrans.translation / scale).to_list()))

        template = Section.stack(templates)
        template.data["manoeuvre"] = self.uid
        return template

    def get_data(self, sec: Section):
        return Section(sec.data.loc[sec.data.manoeuvre == self.uid])

    def match_intention(self, transform: Transformation, flown: Section, speed: float):
        elms = []

        for elm in self.elements:
            elms.append(elm.match_intention(transform, elm.get_data(flown)))
            transform = elms[-1].create_template(
                transform, speed, True).get_state_from_index(-1).transform

        return self.replace_elms(elms), transform

    def correct_intention(self):
        new_man = self.replace_elms([])
        if self.rule.line_lengths:
            new_man = new_man.correct_line_lengths()
        if self.rule.loop_diameter:
            new_man = new_man.fix_loop_diameters()
        if self.rule.centering:
            #new_man = new_man.fix_centering()
            pass
        if self.rule.roll_centering:
            #new_man = new_man.correct_roll_centering()
            pass
        return new_man

    def get_elm_by_type(self, Elm):
        if not isinstance(Elm, list):
            Elm = [Elm]
        return [el for el in self.elements if el.__class__ in Elm]

    def get_id_for_element(self, elms):
        if not isinstance(elms, list):
            elms = [elms]
        uids = [elm.uid for elm in elms]
        return [i for i, elm in enumerate(self.elements) if elm.uid in uids]

    def get_elms_by_id(self, elms):
        if not isinstance(elms, list):
            elms = [elms]
        return [elm for i, elm in enumerate(self.elements) if i in elms]

    def replace_elms(self, elms):
        elm_search = {elm.uid: elm for elm in elms}
        return Manoeuvre(
            self.name, self.k,
            [elm_search[elm.uid] if elm.uid in elm_search.keys() else elm.set_parameter()
             for elm in self.elements],
            self.rule,
            self.uid
        )

    def fix_loop_diameters(self):
        loops = self.get_elm_by_type(LoopEl)
        if len(loops) > 0:
            diameter = loops[0].diameter
            return self.replace_elms(
                [loop.set_parameter(diameter=diameter)
                 for loop in self.get_elm_by_type(LoopEl)]
            )
        else:
            return self.replace_elms([])

    def get_bounded_lines(self):
        """Return the line (and snap) elements that are bounded on each side by a radius.
        a bounded line is a list of lines between two loops, so return is a list of lists of lines
        """
        loop_ids = self.get_id_for_element(self.get_elm_by_type(LoopEl))
        line_ids = np.array(self.get_id_for_element(
            self.get_elm_by_type([LineEl, SnapEl])))

        line_groups = np.split(line_ids, np.array(
            np.where(np.diff(line_ids) > 1)[0]) + 1)

        return [self.get_elms_by_id(list(grp)) for grp in line_groups if grp[-1] + 1 in loop_ids and grp[0] - 1 in loop_ids]

    @staticmethod
    def create_elm_df(elm_list):
        return pd.DataFrame([elm.to_dict() for elm in elm_list])

    @staticmethod
    def set_bounded_line_length(bline: list, length: float):
        """Set the length of a bounded line, equalise lengths before and after rolls
        some thought given to setting lengths shorter than the roll elements, needs
        to be re visited.
        TODO this needs to be seperated from roll centering.
        """
        df = Manoeuvre.create_elm_df(bline)

        roll_length = df[df.rolls != 0.0].length.sum()
        
        if roll_length > length:
            new_line_length = length / len(bline) # TODO define a min line length
            return [
                elm.set_parameter(length=new_line_length) for elm in bline
            ]
        else:
            line_count = len(df[df.rolls == 0])

            new_line_length = (length - roll_length) / line_count

            return [
                elm.set_parameter(length=new_line_length) if elm.rolls == 0 else elm.set_parameter() for elm in bline
            ]

    @staticmethod
    def calc_bounded_line_length(bline):
        return sum([line.length for line in bline])

    def correct_line_lengths(self):
        """Equalise all the bounded line lengths. For now to the maximum. To be revisited.
        put rolls in the middle of lines
        """
        blines = self.get_bounded_lines()
        if len(blines) == 0:
            return self.replace_elms([])
        lengths = [Manoeuvre.calc_bounded_line_length(line) for line in blines]
        length = np.mean(lengths)  # TODO this is probably not the best choice
        new_lines = [Manoeuvre.set_bounded_line_length(bline, length) for bline in blines ]
        
        new_elms = []
        for newline in new_lines:
            new_elms += newline
        return self.replace_elms(new_elms)

