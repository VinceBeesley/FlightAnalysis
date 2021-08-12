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
        self.elements = elements   # TODO better to work with a custom element collection rather than a list
        self.rule = rule
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

        return self.label(Section.stack(templates))

    def get_data(self, sec: Section):
        return Section(sec.data.loc[sec.data.manoeuvre == self.uid])

    def match_intention(self, transform: Transformation, flown: Section, speed: float):
        elms = []

        for elm in self.elements:
            elms.append(elm.match_intention(transform, elm.get_data(flown)))
            transform = elms[-1].create_template(
                transform, speed, True).get_state_from_index(-1).transform

        return self.replace_elms(elms), transform

    def fix_intention(self):
        new_man = self.replace_elms([])
        if self.rule.line_lengths:
            new_man = new_man.fix_line_lengths()
        if self.rule.loop_diameter:
            new_man = new_man.fix_loop_diameters()
        if self.rule.centering:
            new_man = new_man.fix_centering()
        if self.rule.roll_rate:
            new_man = new_man.fix_roll_rates()
        if self.rule.roll_centering:
            new_man = new_man.fix_roll_centering()
            pass
        return new_man

    def replace_elms(self, elms):
        elm_search = {elm.uid: elm for elm in elms}
        return Manoeuvre(
            self.name, self.k,
            [elm_search[elm.uid] if elm.uid in elm_search.keys() else elm.set_parameter()
             for elm in self.elements],
            self.rule,
            self.uid
        )

    def replace_blines(self, blines):
        new_elms = []
        for newline in blines:
            new_elms += newline
        return self.replace_elms(new_elms)


    def fix_loop_diameters(self):
        loops = Manoeuvre.filter_elms_by_attribute(self.get_elm_by_type(LoopEl), r_tag=True)
        if len(loops) > 0:
            diameter = np.mean([loop.diameter for loop in loops])  # Factor by the amount of loop flown
            return self.replace_elms(
                [loop.set_parameter(diameter=diameter)
                 for loop in self.get_elm_by_type(LoopEl)]
            )
        else:
            return self.replace_elms([])

    def fix_line_lengths(self):
        """Equalise all the bounded line lengths. For now to the maximum. To be revisited.
        put rolls in the middle of lines
        """
        blines = self.get_bounded_lines()
        if len(blines) == 0:
            return self.replace_elms([])
        
        blines=[bline for bline in blines if np.all([line.l_tag for line in bline])] # TODO only modifies lines where all constituents have l_tag=True. seems logical to do opposite of default

        lengths = [Manoeuvre.calc_line_length(line) for line in blines]
        length = np.mean(lengths)  # TODO this is probably not the best choice
        new_lines = [Manoeuvre.set_bounded_line_length(bline, length) for bline in blines ]
        
        return self.replace_blines(new_lines)

    def fix_roll_centering(self):
        blines = [Manoeuvre.correct_roll_centering(bline) for bline in self.get_bounded_lines()]
        return self.replace_blines(blines)

    def fix_roll_rates(self):
        return self.replace_elms([]) # TODO this

    def fix_centering(self):
        return self.replace_elms([]) # TODO this

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
    def set_bounded_line_length(bline: list, length: float):
        """Set the length of a bounded line, some thought given to setting lengths shorter than the roll elements.
        """
        total_length = sum([line.length for line in bline])
        
        padding_lines = Manoeuvre.get_padding_lines(bline)
        pad_length = Manoeuvre.calc_line_length(padding_lines) 
        pad_uids = [el.uid for el in padding_lines]

        rolls = [line for line in bline if not line.rolls == 0]
        roll_uids = [line.uid for line in rolls]
        roll_length = Manoeuvre.calc_line_length(rolls)


        new_pad_length = max(total_length / 20, length - total_length + pad_length)
        if roll_length == 0:
            roll_mod_ratio = 1.0    
        else:
            roll_mod_ratio = max(1.0, (length - new_pad_length) / roll_length)


        new_bline = []
        for line in bline:
            nline = line.set_parameter()
            if line.uid in pad_uids:
                nline = line.set_parameter(length=new_pad_length / len(padding_lines))
            if line.uid in roll_uids:
                nline = line.set_parameter(length=line.length * roll_mod_ratio)
            new_bline.append(nline)

        return new_bline         

    @staticmethod
    def calc_line_length(bline):
        return sum([line.length for line in bline])


    @staticmethod
    def correct_roll_centering(bline: list):
        """correct roll centering in a bounded line."""
        padding_lines = Manoeuvre.get_padding_lines(bline)
        if len(padding_lines) == 0:
            pad_length = 0
        else:
            pad_length = Manoeuvre.calc_line_length(padding_lines) / len(padding_lines)
        pad_uids = [el.uid for el in padding_lines]

        return [line.set_parameter(length=pad_length) if line.uid in pad_uids else line.set_parameter() for line in bline]        
    
    @staticmethod
    def get_padding_lines(bline: list):
        padding_lines = []
        
        if len(bline) > 0 and bline[0].rolls == 0:
            padding_lines.append(bline[0])
        if len(bline) > 1 and bline[-1].rolls == 0:
            padding_lines.append(bline[-1])
        return padding_lines



    def get_elm_by_type(self, Elm):
        if not isinstance(Elm, list):
            Elm = [Elm]
        return [el for el in self.elements if el.__class__ in Elm]

    @staticmethod
    def filter_elms_by_attribute(elms, **kwargs):
        for key, value in kwargs.items():
            elms = [el for el in elms if getattr(el, key, None) == value]
        return elms

    def get_id_for_element(self, elms):
        if not isinstance(elms, list):
            elms = [elms]
        uids = [elm.uid for elm in elms]
        return [i for i, elm in enumerate(self.elements) if elm.uid in uids]

    def get_elms_by_id(self, elms):
        if not isinstance(elms, list):
            elms = [elms]
        return [elm for i, elm in enumerate(self.elements) if i in elms]

    @staticmethod
    def create_elm_df(elm_list):
        return pd.DataFrame([elm.to_dict() for elm in elm_list])

    def label(self, sec: Section):
        new_data = sec.data.copy()
        new_data.loc[:,"manoeuvre"] = self.uid
        return Section(new_data)