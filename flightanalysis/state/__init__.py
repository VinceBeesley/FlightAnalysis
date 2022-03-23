



from .state import State

#
from .tools.builders import (
    extrapolate, 
    from_csv, 
    from_flight, 
    stack
)
#
State.extrapolate = extrapolate
State.from_csv = staticmethod(from_csv)
State.from_flight = staticmethod(from_flight)
State.stack = staticmethod(stack)
#
from .tools.transformers import (
    superimpose_angles, 
    superimpose_rotation, 
    superimpose_roll, 
    smooth_rotation, 
    transform
)
#
State.transform = transform
State.superimpose_angles = superimpose_angles
State.superimpose_rotation = superimpose_rotation
State.superimpose_roll = superimpose_roll
State.smooth_rotation = smooth_rotation
#
from .tools.alignment import align, copy_labels
#
State.align = staticmethod(align)
State.copy_labels = staticmethod(copy_labels)
#
from .tools.conversions import to_judging, body_to_wind, judging_to_wind, wind_to_body
#
State.to_judging = to_judging
State.body_to_wind = body_to_wind
State.judging_to_wind = judging_to_wind
State.wind_to_body = wind_to_body
#
from .tools.measurements import measure_aoa, measure_airspeed, measure_coefficients, direction
#
State.measure_aoa = measure_aoa
State.measure_airspeed = measure_airspeed
State.measure_coefficients = measure_coefficients
State.direction = direction