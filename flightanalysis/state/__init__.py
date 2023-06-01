



from .state import State

#
from .tools.builders import (
    fill,
    extrapolate, 
    from_csv, 
    from_flight, 
    stack
)
#
State.fill = fill
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
    move, 
    move_back,
    relocate
)
#
State.move = move
State.move_back = move_back
State.relocate = relocate
State.superimpose_angles = superimpose_angles
State.superimpose_rotation = superimpose_rotation
State.superimpose_roll = superimpose_roll
State.smooth_rotation = smooth_rotation
#
from .tools.alignment import (
    align, 
    copy_labels, 
    splitter_labels, 
    get_manoeuvre, 
    get_element, 
    get_subelement, 
    get_element_from_manoeuvre,
    remove_labels
)
#
State.align = staticmethod(align)
State.copy_labels = staticmethod(copy_labels)
State.splitter_labels = splitter_labels
State.get_manoeuvre = get_manoeuvre
State.get_element = get_element
State.get_subelement = get_subelement
State.get_element_from_manoeuvre = get_element_from_manoeuvre
State.remove_labels = remove_labels
#
from .tools.conversions import convert_state, to_judging, body_to_wind, judging_to_wind, wind_to_body
#
State.body_rotate = convert_state
State.to_judging = to_judging
State.body_to_wind = body_to_wind
State.judging_to_wind = judging_to_wind
State.wind_to_body = wind_to_body
#
from .tools.measurements import direction, inverted, upright, judging_itrans
#
State.direction = direction
State.inverted = inverted
State.upright = upright
State.judging_itrans = judging_itrans


from .tools.dumpers import create_fc_json
State.create_fc_json = create_fc_json