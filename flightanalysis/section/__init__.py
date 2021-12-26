from .state import State
from .section import Section

from .tools.builders import (
    from_constructs,
    extrapolate_state, 
    from_csv, 
    from_flight, 
    stack, 
    make_dt,
    make_bvel, 
    make_brvel, 
    make_bacc, 
    make_bracc
)

Section.from_constructs = staticmethod(from_constructs)
Section.extrapolate_state = staticmethod(extrapolate_state)
Section.from_csv = staticmethod(from_csv)
Section.from_flight = staticmethod(from_flight)
Section.stack = staticmethod(stack)

Section.construct_makers = dict(
    dt=make_dt,
    bvel=make_bvel,
    brvel=make_brvel,
    bacc=make_bacc,
    bracc=make_bracc,
)

from .tools.transformers import (
    superimpose_angles, 
    superimpose_rotation, 
    superimpose_roll, 
    smooth_rotation, 
    t_array, 
    transform
)

Section.transform = transform
Section.t_array = staticmethod(t_array)
Section.superimpose_angles = superimpose_angles
Section.superimpose_rotation = superimpose_rotation
Section.superimpose_roll = superimpose_roll
Section.smooth_rotation = smooth_rotation


from .tools.alignment import align, copy_labels


Section.align = staticmethod(align)
Section.copy_labels = staticmethod(copy_labels)


