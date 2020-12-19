from geometry import Point, Coord
from flightdata import CIDTypes


def rotate_data(bin, angle):
    # get a vector pointing in the desired x axis by rotating the default x axis vector by the angle requested.
    box_normal_vector = Point(1, 0, 0).rotate(
        Point(0, 0, angle).to_rotation_matrix())

    # create a new Coord based on the origin (unchanged), the z axis (up), and the new x axis vector.
    box_cid = Coord.from_zx(Point(0, 0, 0), Point(0, 0, -1), box_normal_vector)

    def point_to_box(x, y, z):
        box_point = Point(x, y, z).rotate(box_cid.rotation_matrix)
        return box_point.x, box_point.y, box_point.z

    def euler_to_box(x, y, z):
        seupoint = Point(x, y - pi, - z - angle)
        return seupoint.x, seupoint.y, seupoint.z

    transforms = {i: lambda *args: args for i in range(0, 7)}
    transforms[CIDTypes.CARTESIAN] = point_to_box
    transforms[CIDTypes.EULER] = euler_to_box
    transforms[CIDTypes.ZONLY] = lambda *args: tuple(-arg for arg in args)
    transforms[CIDTypes.XY]: lambda *args: point_to_box(*args, z=0)

    return bin.transform(transforms)
