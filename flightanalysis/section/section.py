from geometry import Point, Points, Quaternions
from .state import State, constructs, assert_vars, assert_constructs, all_vars, construct_list
from flightanalysis.fd_model.atmosphere import Atmosphere, Atmospheres
import numpy as np
import pandas as pd
from typing import Union
from numbers import Number
import warnings


def atmosphere_check(data):
    constrs = construct_list(data.columns)
    if not "atm" in constrs:
        warnings.warn("No Atmosphere Data Available, assuming SL Standard pressure and temperature. \n This is for temporary back compatibility with old section csvs.")
        data = pd.concat([
            data, 
            Atmospheres(np.full((len(data["t"]), 2), [101325, 288.15])).to_pandas(index=data.index)
        ], axis=1)

    return data

class Section():
    _construct_freq = 30

    def __init__(self, data: pd.DataFrame):
        if len(data) == 0:
            raise Exception("Section created with empty dataframe")

        data = atmosphere_check(data)
        
        assert_vars(data.columns)

        self.data = data
        self.data.index = self.data.index - self.data.index[0]

    def __getattr__(self, name) -> Union[pd.DataFrame, Points, Quaternions]:
        if name in self.data.columns:
            return self.data[name]
        elif name in constructs.keys():
            return self.data[constructs[name].keys]
        elif name == "gtime":     
            return self.time.to_numpy()[:,0]
        elif name in ["g" + name for name in constructs.keys()]:
            return constructs[name[1:]].fromdf(self.data)

    def segment(self, partitions):
        parts = np.linspace(self.data.index[0], self.data.index[-1], partitions)

        return [
            self.subset(p0, p1) 
            for p0, p1 in 
            zip(parts[:-2], parts[1:])
        ]

    def subset(self, start: Number, end: Number):
        if start == -1 and not end == -1:
            return Section(self.data.loc[:end])
        elif end == -1 and not start == -1:
            return Section(self.data.loc[start:])
        elif start == -1 and end == -1:
            return Section(self.data)
        else:
            return Section(self.data[start:end])

    @staticmethod
    def from_constructs(*args,**kwargs):
        kwargs = dict(kwargs, **{list(constructs.keys())[i]: arg for i, arg in enumerate(args)})

        assert_constructs(list(kwargs.keys()))

        df = pd.concat(
            [constructs[key].todf(x, kwargs["time"]) for key, x in kwargs.items()],
            axis=1
        )

        df = atmosphere_check(df)       

        return Section(df)

    def existing_constructs(self):
        """returns the variable construct names that exist in this section"""
        return [key for key, const in constructs.items() if all([val in self.data.columns for val in const.keys])]

    def misc_cols(self):
        return [col for col in self.data.columns if not col in all_vars]

    def copy(self, *args, **kwargs):
        kwargs = dict(kwargs, **{list(constructs.keys())[i]: arg for i, arg in enumerate(args)})
        
        old_constructs = {key: self.__getattr__("g" + key) for key in self.existing_constructs() if not key in kwargs.keys()}

        new_constructs = {key: value for key, value in list(kwargs.items()) + list(old_constructs.items())}

        return Section.from_constructs(**new_constructs).append_columns(self.data[self.misc_cols()])
        

    def append_columns(self, data):
        if isinstance(data, list):
            return Section(pd.concat([self.data] + data, axis=1, join="inner"))
        elif isinstance(data,pd.DataFrame):
            return Section(pd.concat([self.data, data], axis=1, join="inner"))
        elif isinstance(data, pd.Series):
            return Section(pd.concat([self.data, data], axis=1, join="inner"))
            
    def to_csv(self, filename):
        self.data.to_csv(filename)
        return filename


    def __len__(self):
        return len(self.data)

    @property
    def duration(self):
        return self.data.index[-1] - self.data.index[0]

    def __getitem__(self, key):
        return self.get_state_from_index(key)

    def get_state_from_index(self, index):
        return State(self.data.iloc[index])

    def get_state_from_time(self, time):
        return self.get_state_from_index(
            self.data.index.get_loc(time, method='nearest')
        )

    def body_to_world(self, pin: Union[Point, Points]) -> pd.DataFrame:
        """generate world frame trace of a body frame point

        Args:
            pin (Point): point in the body frame
            pin (Points): points in the body frame

        Returns:
            Points: trace of points
        """

        if isinstance(pin, Points) or isinstance(pin, Point):
            return self.gatt.transform_point(pin) + self.gpos
        else:
            return NotImplemented

    def label(self, **kwargs):
        return Section(self.data.assign(**kwargs))

    def remove_labels(self):
        return Section(self.data.drop(["manoeuvre", "element"], 1, errors="ignore"))
    
    def flying_only(self):
        above_ground = self.data.loc[self.data.z >= 5.0]
        return self.subset(above_ground.index[0], above_ground.index[-1])

