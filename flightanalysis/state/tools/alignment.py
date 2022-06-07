from geometry import Point
from fastdtw import fastdtw
import warnings
from scipy.spatial.distance import euclidean
from flightanalysis.state import State
import numpy as np
import pandas as pd


def align(flown, template, radius=5, white=False, weights = Point(1,1,1)) -> State:
    """Perform a temporal alignment between two sections. return the flown section with labels 
    copied from the template along the warped path

    Args:
        flown (Section): An un-labelled Section
        template (Section): A labelled Section
        radius (int, optional): The DTW search radius. Defaults to 5.
        whiten (bool, optional): Whether to whiten the data before performing the alignment. Defaults to False.

    """
    if white:
        warnings.filterwarnings("ignore", message="Some columns have standard deviation zero. ")

    def get_brv(brv):
        brv.data[:,0] = abs(brv.data[:,0])
        brv.data[:,2] = abs(brv.data[:,2])

        if white:
            brv = brv.whiten()

        return brv * weights

    fl = get_brv(flown.rvel)

    tp = get_brv(template.rvel)

    distance, path = fastdtw(
        tp.data,
        fl.data,
        radius=radius,
        dist=euclidean
    )

    return distance, copy_labels(template, flown, path)


def copy_labels(template, flown, path) -> State:
    """Copy the labels from a template section to a flown section along the index warping path

    Args:
        template (Section): A labelled section
        flown (Section): An unlabelled section
        path (List): A list of lists containing index pairs from template to flown

    Returns:
        Section: a labelled section
    """
    mans = pd.DataFrame(path, columns=["template", "flight"]).set_index("template").join(
            template.data.reset_index(drop=True).loc[:, ["manoeuvre", "element"]]
        ).groupby(['flight']).last().reset_index().set_index("flight")

    return State(flown.data.reset_index(drop=True).join(mans).set_index("t", drop=False))


