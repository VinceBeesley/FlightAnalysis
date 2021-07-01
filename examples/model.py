from flightplotting.model import OBJ
from geometry import Transformation, Point, Quaternion
import numpy as np

obj = OBJ.from_obj_file('data/models/ColdDraftF3APlane.obj').transform(Transformation(
    Point(0.75, 0, 0), Quaternion.from_euler(Point(np.pi, 0, -np.pi/2))
))
