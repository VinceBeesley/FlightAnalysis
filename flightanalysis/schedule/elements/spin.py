import numpy as np
from geometry import Transformation, Point, Points
from flightanalysis import Section
    
from . import El


class Spin(El):
    _speed_factor = 1 / 10

    def __init__(self, turns: float, opp_turns: float = 0.0, rate:float=1.0, uid: str = None):
        super().__init__(uid)
        self.turns = turns
        self.opp_turns = opp_turns
        self.rate = rate

    def set_parameter(self, turns: float = None, opp_turns: float = None, rate: float = None):
        return Spin(
            turns if turns is not None else self.turns,
            opp_turns if opp_turns is not None else self.opp_turns,
            rate if rate is not None else self.rate,
            self.uid
        )

    def scale(self, factor):
        return self.set_parameter(length=self.length * factor)

    def create_template(self, transform: Transformation, speed: float, simple: bool = False):
        _inverted = np.sign(transform.rotate(Point(0, 0, 1)).z)

        nose_drop = Section.from_loop(
            transform, 5.0, -0.25 * _inverted, 2.0, False, freq=1.0 if simple else None)
        nose_drop.data["sub_element"] = "nose_drop"

        rotation = Section.from_line(
            nose_drop.get_state_from_index(-1).transform,
            speed * self._speed_factor,
            self.length * self.turns / (self.turns + self.opp_turns),
            freq=1000 if simple else None
        ).superimpose_roll(self.turns)
        rotation.data["sub_element"] = "rotation"

        if self.opp_turns == 0.0:
            sec = Section.stack([nose_drop, rotation])
        else:
            rotation2 = Section.from_line(
                rotation.get_state_from_index(-1).transform,
                speed * self._speed_factor,
                self.length * self.opp_turns / (self.turns + self.opp_turns),
                freq=1000 if simple else None
            ).superimpose_roll(self.opp_turns)

            rotation2.data["sub_element"] = "opp_rotation"

            sec = Section.stack([nose_drop, rotation, rotation2])
        return self._add_rolls(sec, 0.0)

    def match_axis_rate(self, spin_rate, speed: float):
        return self.set_parameter(
            length=2 * np.pi * (abs(self.turns) + abs(self.opp_turns)) * speed *
            Spin._speed_factor / spin_rate
        )

    def match_intention(self, transform: Transformation, flown: Section):
        # TODO doesnt cover opposite turns
        length = abs(flown.get_state_from_index(-1).pos.z -
                     flown.get_state_from_index(0).pos.z)

        return self.set_parameter(
            length=length,
            turns=np.sign(np.mean(Points.from_pandas(
                flown.brvel).x)) * abs(self.turns),
            opp_turns=0.0
        )