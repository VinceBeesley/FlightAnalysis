from .state import State
from .section import Section


from .tools.builders import extrapolate_state, from_csv, from_flight, stack

Section.extrapolate_state = staticmethod(extrapolate_state)
Section.from_csv = staticmethod(from_csv)
Section.from_flight = staticmethod(from_flight)
Section.stack = staticmethod(stack)

from .tools.transformers import superimpose_angles, superimpose_rotation, superimpose_roll, smooth_rotation, t_array, transform

Section.transform = transform
Section.t_array = staticmethod(t_array)
Section.superimpose_angles = superimpose_angles
Section.superimpose_rotation = superimpose_rotation
Section.superimpose_roll = superimpose_roll
Section.smooth_rotation = smooth_rotation

from .tools.alignment import align, copy_labels

Section.align = staticmethod(align)
Section.copy_labels = staticmethod(copy_labels)


from .tools.wind import calculate_wind, append_wind

Section.calculate_wind = calculate_wind
Section.append_wind = append_wind

from .tools.flow import calculate_flow, append_flow

Section.calculate_flow = calculate_flow
Section.append_flow = append_flow 

def append_derived_values(self: Section) -> Section:
    return self.append_wind().append_flow()

Section.append_derived_values = append_derived_values

