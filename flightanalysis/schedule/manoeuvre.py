from geometry import Transformation
from flightanalysis.state import State
from flightanalysis.schedule.elements import Loop, Line, StallTurn, Snap, Spin, get_rates, El
from flightanalysis.schedule.figure_rules import IMAC, rules, Rules
import numpy as np
import pandas as pd


_els = {c.__name__: c for c in El.__subclasses__()}


class Manoeuvre():
    _counter = 0

    @staticmethod
    def reset_counter():
        Manoeuvre._counter = 0
        El.reset_counter()

    def __init__(self, name: str, k: float, elements: list, rule=IMAC, uid: int = None):
        self.name = name
        self.k = k

        if all(isinstance(x, El) for x in elements):
            self.elements = elements  
        elif all(isinstance(x, dict) for x in elements):
            self.elements = [_els[x.pop("type")](**x) for x in elements]
        else:
            self.elements = []

        if isinstance(rule,str):
            rule = rules[rule]
        self.rule = rule
        
        if not uid:
            Manoeuvre._counter += 1
            self.uid = Manoeuvre._counter
        else:
            self.uid = uid

    def to_dict(self):
        data = self.__dict__.copy()
        data["elements"] = [elm.to_dict() for elm in self.elements]
        data["rule"] = self.rule.__name__
        return data
    
    def scale(self, factor: float):
        return self.replace_elms([elm.scale(factor) for elm in self.elements])

    def create_template(self, transform: Transformation, speed: float) -> State:
        itrans = transform
        templates = []
        for i, element in enumerate(self.elements):
            templates.append(element.create_template(itrans, speed))
            itrans = templates[-1][-1].transform
        
        return self.label(State.stack(templates))

    def get_data(self, sec: State):
        return State(sec.data.loc[sec.data.manoeuvre == self.uid])

    def match_intention(self, transform: Transformation, flown: State, speed: float=None):
        """Create a new manoeuvre with all the elements scaled to match the corresponding flown element"""
        elms = []

        for elm in self.elements:
            edata=elm.get_data(flown)
            elms.append(elm.match_intention(transform, edata))
            transform = elms[-1].create_template(
                transform, 
                edata.data.bvx.mean(), 
                True
            )[-1].transform

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
            [elm_search[elm.uid] if elm.uid in elm_search.keys() else elm.set_parms()
             for elm in self.elements],
            self.rule,
            self.uid
        )

    def append_element(self, elm):
        nman = self.replace_elms([])
        nman.elements.append(elm)
        return nman

    def remove_element(self, elm):
        nman = self.replace_elms([])
        nman.elements.remove(elm)
        return nman

    def replace_blines(self, blines):
        new_elms = []
        for newline in blines:
            new_elms += newline
        return self.replace_elms(new_elms)


    def fix_loop_diameters(self):
        loops = Manoeuvre.filter_elms_by_attribute(self.get_elm_by_type(Loop), r_tag=True)
        if len(loops) > 0:
            diameter = np.mean([loop.diameter for loop in loops])  # TODO Factor by the amount of loop flown
            return self.replace_elms(
                [loop.set_parms(diameter=diameter)
                 for loop in self.get_elm_by_type(Loop)]
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
        
        blines=[bline for bline in blines if np.all([line.l_tag for line in bline])]
        
        lengths = [Manoeuvre.calc_line_length(line) for line in blines]
        length = np.mean(lengths) 
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
        loop_ids = self.get_id_for_element(self.get_elm_by_type([Loop, StallTurn]))
        line_ids = np.array(self.get_id_for_element(
            self.get_elm_by_type([Line, Snap])))

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
            nline = line.set_parms()
            if line.uid in pad_uids:
                nline = line.set_parms(length=new_pad_length / len(padding_lines))
            if line.uid in roll_uids:
                if not isinstance(line, Snap):
                    nline = line.set_parms(length=line.length * roll_mod_ratio)
                else:
                    nline = line.set_parms()
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

        return [line.set_parms(length=pad_length) if line.uid in pad_uids else line.set_parms() for line in bline]        
    
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

    def label(self, sec: State):
        return State(sec.data.assign(manoeuvre=self.uid))

    def share_seperator(self, next_man): 
        """Take the following manoeuvre and share the entry line (first element)"""
        if self.elements[-1] != next_man.elements[0]:
            return self.append_element(next_man.elements[0].set_parms())
        else:
            return self.replace_elms([])

    def unshare_seperator(self, next_man): 
        """remove the final element if it matches the first element of the next one"""
        if self.elements[-1] == next_man.elements[0]:
            return self.remove_element(self.elements[-1])
        else:
            return self.replace_elms([])


    def match_rates(self, rates):
        new_elms = [elm.match_axis_rate(rates[elm.__class__], rates["speed"]) for elm in self.elements]
        return self.replace_elms(new_elms)

    
    def get_subset(self, sec: State, first_element: int, last_element: int):
        subsec = self.get_data(sec)
        fmanid = self.elements[first_element].uid
        if last_element == -1:
            lmanid = self.elements[-1].uid + 1
        else:
            lmanid = self.elements[last_element].uid

        return State(subsec.data.loc[(subsec.data.element >= fmanid) & (subsec.data.element < lmanid)])

