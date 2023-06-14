from geometry import Point
from fastdtw import fastdtw
import warnings
from scipy.spatial.distance import euclidean
from flightanalysis.state import State
import numpy as np
import pandas as pd
from typing import List, Union
from pandas.api.types import is_list_like


def align(flown, template, radius=5, mirror=True, white=False, weights = Point(1,1,1)) -> State:
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
        if mirror:
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


def copy_labels(template, flown, path=None) -> State:
    """Copy the labels from a template section to a flown section along the index warping path

    Args:
        template (Section): A labelled section
        flown (Section): An unlabelled section
        path (List): A list of lists containing index pairs from template to flown

    Returns:
        Section: a labelled section
    """

    flown = flown.remove_labels()

    keys = [k for k in ["manoeuvre", "element", "sub_element"] if k in template.data.columns]
    if path is None:
        return State(
            pd.concat(
                [flown.data.reset_index(drop=True), template.data.loc[:,keys].reset_index(drop=True)], 
                axis=1
            ).set_index("t", drop=False)
        )
    else:
        mans = pd.DataFrame(path, columns=["template", "flight"]).set_index("template").join(
                template.data.reset_index(drop=True).loc[:, keys]
            ).groupby(['flight']).last().reset_index().set_index("flight")

        return State(flown.data.reset_index(drop=True).join(mans).set_index("t", drop=False))


def splitter_labels(self: State, mans: List[dict]) -> State:
        """label the manoeuvres in a State based on the flight coach splitter information

        TODO this assumes the state only contains the dataset contained in the json

        Args:
            mans (list): the mans field of a flight coach json

        Returns:
            State: State with labelled manoeuvres
        """

        takeoff = self.data.iloc[0:int(mans[0]["stop"])+1]

        labels = [mans[0]["name"]]
        labelled = [State(takeoff).label(manoeuvre=labels[0])]
        
        for split_man in mans[1:]:
            
            while split_man["name"] in labels:
                split_man["name"] = split_man["name"] + "2"

            labelled.append(
                State(
                    self.data.iloc[int(split_man["start"]):int(split_man["stop"])+1]
                ).label(manoeuvre=split_man["name"])
            )
            labels.append(split_man["name"])

        return State.stack(labelled)



def get_subset(self: State, mans: Union[list, slice], col="manoeuvre"):
    selectors = self.data.loc[:,col].unique()
    if isinstance(mans, slice):
        mans = selectors[mans]

    if not is_list_like(mans):
        mans = [mans]
    
    if not all(isinstance(m, str) for m in mans):
        mans = [m.uid if m.__class__.__name__ == "Manoeuvre" else m for m in mans]
        mans = [m.uid if m.__class__.__bases__[0].__name__ == "El" else m for m in mans]    
        mans = [selectors[m] if isinstance(m, int) else m for m in mans]
        
    assert all(isinstance(m, str) for m in mans)

    return State(self.data.loc[self.data.loc[:, col].isin(mans)])

def get_manoeuvre(self: State, manoeuvre: Union[str, list, int]):
    return get_subset(self, manoeuvre, "manoeuvre")

def get_element(self: State, element: Union[str, list, int]):
    return get_subset(self, element, "element") 

def get_meid(self: State, manid: int, elid: int=None):
    st = self.get_manoeuvre(manid)
    if not elid is None:
        return st.get_element(elid)
    else:
        return st
