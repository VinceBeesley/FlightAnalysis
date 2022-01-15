import numpy as np
import pandas as pd
from flightanalysis.section import Section
from geometry import Point, Points, Quaternion, Quaternions, Transformation


def t_array(duration: float, freq: float = None):
    if freq==None:
        freq = Section._construct_freq
    return  np.linspace(0, duration, max(int(duration * freq), 3))


def transform(self: Section, transform: Transformation) -> Section:
    return Section.from_constructs(
        time=np.array(self.data.index),
        pos=transform.point(self.gpos),
        att=transform.quat(self.gatt),
        bvel=transform.rotate(self.gbvel),
        brvel=transform.rotate(self.gbrvel),
        bacc=transform.rotate(self.gbacc),
        bracc=transform.rotate(self.gbracc),
    )

def superimpose_angles(self: Section, angles: Points, reference:str="body"): 
    if reference=="world":
        new_att = self.gatt.rotate(angles)
    elif reference=="body":
        new_att = self.gatt.body_rotate(angles)
    else:
        raise ValueError("unknwon rotation reference")
       
    
    sec =  Section.from_constructs(
        time=np.array(self.data.index),
        pos=Points.from_pandas(self.pos.copy()),
        att=new_att
    )

    if "sub_element" in self.data.columns:
        sec = sec.append_columns(self.data["sub_element"])
    return sec


def superimpose_rotation(self: Section, axis: Point, angle: float, reference:str="body"):
    """Generate a new section, identical to self, but with a continous rotation integrated
    """
    t = np.array(self.data.index) - self.data.index[0]

    rate = angle / t[-1]
    superimposed_rotation = t * rate

    angles = Points.from_point(axis.unit(), len(t)) * superimposed_rotation

    return self.superimpose_angles(angles, reference)



def superimpose_roll(self: Section, proportion: float) -> Section:
    """Generate a new section, identical to self, but with a continous roll integrated

    Args:
        proportion (float): the amount of roll to integrate
    """
    return self.superimpose_rotation(Point(1,0,0), 2 * np.pi * proportion)



def smooth_rotation(self: Section, axis: Point, angle: float, reference:str="body", w: float=0.25, w2=0.1):
    """Accelerate for acc_prop * t, flat rate for middle, slow down for acc_prop * t.

    Args:
        axis (Point): Axis to rotate around.
        angle (float): angle to rotate.
        reference (str, optional): rotate about body or world. Defaults to "body".
        acc_prop (float, optional): proportion of total rotation to be accelerating for. Defaults to 0.1.
    """

    t = np.array(self.data.index) - self.data.index[0]

    T = t[-1]

    V = angle / (T*(1-0.5*w-0.5*w2))  # The maximum rate

    #between t=0 and t=wT
    x = t[t<=w*T]
    angles_0 = (V * x**2) / (2 * w * T)    

    #between t=wT and t=T(1-w)
    y=t[(t>w*T) & (t<=(T-w2*T))]
    angles_1 = V * y - V * w * T / 2
    
    #between t=T(1-w2) and t=T
    z = t[t>(T-w2*T)] - T + w2*T
    angles_2 = V*z - V * z **2 / (2*w2*T) + V*T - V * w2 * T  - 0.5*V*w*T

    angles = Points.from_point(axis.unit(), len(t)) * np.concatenate([angles_0, angles_1, angles_2])

    return self.superimpose_angles(angles, reference)


