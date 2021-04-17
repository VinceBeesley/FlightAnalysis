"""These are the variables handled by the State and Section classes.
    The variables are defined in the values of the svars dict, in the order in which they first appear.
    The keys just provide some handy tags to access sets of values with. 

    pos = position (Cartesian)
    att = attitude (Quaternion)
    bvel = velocity in (body frame)
    brvel = rotational velocity (body axis rates)

    """

svars = {
    "pos": ["x", "y", "z"],
    "att": ["rw", "rx", "ry", "rz"],
    "bvel": ["bvx", "bvy", "bvz"],
    "brvel": ["brvr", "brvp", "brvy"],
    "bacc": ["bax", "bay", "baz"],
    "wp": ["x", "y", "z", "rw", "rx", "ry", "rz"],
    "bv": ["bvx", "bvy", "bvz", "brvr", "brvp", "brvy"]
}
