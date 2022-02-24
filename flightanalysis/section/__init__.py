



from .section import Section
from .state import State

Section.Instant = State
State.Period = Section
#
from .tools.builders import (
    from_constructs,
    extrapolate_state, 
    from_csv, 
    from_flight, 
    stack
)

Section.from_constructs = staticmethod(from_constructs)
Section.extrapolate_state = staticmethod(extrapolate_state)
Section.from_csv = staticmethod(from_csv)
Section.from_flight = staticmethod(from_flight)
Section.stack = staticmethod(stack)

from .tools.transformers import (
    superimpose_angles, 
    superimpose_rotation, 
    superimpose_roll, 
    smooth_rotation, 
    make_index, 
    transform
)

Section.transform = transform
Section.make_index = staticmethod(make_index)
Section.superimpose_angles = superimpose_angles
Section.superimpose_rotation = superimpose_rotation
Section.superimpose_roll = superimpose_roll
Section.smooth_rotation = smooth_rotation

from .tools.alignment import align, copy_labels

Section.align = staticmethod(align)
Section.copy_labels = staticmethod(copy_labels)

from .tools.conversions import to_judging, body_to_wind, judging_to_wind, wind_to_body

Section.to_judging = to_judging
Section.body_to_wind = body_to_wind
Section.judging_to_wind = judging_to_wind
Section.wind_to_body = wind_to_body

from .tools.measurements import measure_aoa, measure_airspeed, measure_coefficients

Section.measure_aoa = measure_aoa
Section.measure_airspeed = measure_airspeed
Section.measure_coefficients = measure_coefficients