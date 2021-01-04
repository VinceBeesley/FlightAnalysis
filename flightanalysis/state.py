from flightdata import Fields
from geometry import Point, Quaternion
from operator import itemgetter


class State():
    """Describes the position and orientation of a body in 3D space"""

    def __init__(self, pos: Point, att: Quaternion):
        self.pos = pos
        self.att = att


    @staticmethod
    def from_flight(props: dict):
        return State(
            Point(*itemgetter(*Fields.POSITION.names)(props)),
            Quaternion.from_euler(
                Point(*itemgetter(*Fields.ATTITUDE.names)(props)))
        )

    def to_dict(self, prefix=''):
        return dict(self.pos.to_dict(prefix), **self.att.to_dict(prefix + 'q'))

    @staticmethod
    def from_dict(value: dict):
        # TODO this will fail if the prefix contains the letter q
        return State(
            Point.from_dict(
                {key[-1]: value for key, value in value.items() if not 'q' in key}
            ),
            Quaternion.from_dict(
                {key[-1]: value for key, value in value.items() if 'q' in key}
            )
        )
