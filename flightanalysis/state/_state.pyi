from flightanalysis.flightline import FlightLine, Box
from typing import Union, Tuple
from flightdata import Flight
from flightanalysis.state.variables import secvars
from flightanalysis.base.table import Table
from geometry import Points
import numpy as np


class State(Base):
    ...
    @staticmethod
    def from_csv(filename: str) -> State: 
        """Read a State from a csv file

        Args:
            filename (str): path to the csv file

        Returns:
            State: [description]
        """
        ...
    @staticmethod
    def extrapolate_state(istate: State, duration: float, freq: float = None) -> State: 
        """Extrapolate the state along its velocity and axis rate

        Args:
            istate (State): the first state
            duration (float): time (seconds) to extrapolate over
            freq (float, optional): frequency to extrapolate at. Defaults to State.construct_freq.

        Returns:
            State: [description]
        """
        ...
    @staticmethod
    def from_flight(flight: Union[Flight, str], box:Union[FlightLine, Box, str]) -> State: 
        """Create a State from a Flight instance, rotated to the desired box.

        Args:
            flight (Union[Flight, str]): [description]
            box ([type], optional): [description]. Defaults to Union[FlightLine, Box, str].

        Returns:
            State: [description]
        """
        ...
    @staticmethod
    def stack(States: list) -> State: 
        """stack two States on top of each other, offset time indeces appropriately

        Args:
            States (list): list of States to stack

        Returns:
            State: [description]
        """
        ...
    
    
    def to_judging(self: State) -> State: 
        """Converts a body or wind axis State to the Judging axis 
        (x axis aligned with velocity vector)

        Args:
            self (State): [description]

        Returns:
            State: [description]
        """
        ...

    def body_to_wind(self: State, alpha: np.ndarray, beta: np.ndarray) -> State: 
        """Converts a body frame State to the Wind Axis for a given set of alphas and betas

        Args:
            self (State): body frame State
            alpha (np.ndarray): alpha for every time instant
            beta (np.ndarray): alpha for every time instant

        Returns:
            State: Secion in wind axis
        """
        ...

    def judging_to_wind(self: State, wind: Points) -> State:
        """converts a judging frame State to the wind axis given the wind at every time instant.

        Args:
            self (State): Judging frame State
            wind (Points): instantanious wind
        """
        ...

    
    def wind_to_body(self: State, alpha: np.ndarray, beta: np.ndarray) -> State:
        """convert a wind axis State to a body axis State

        Args:
            self (State): State in wind axis
            alpha (np.ndarray): alpha for each time instant
            beta (np.ndarray): beta for each time instant

        Returns:
            State: body axis State
        """
        ...


    def measure_aoa(self: State, other:State=None) -> Tuple[np.ndarray, np.ndarray]: 
        """measure alpha and beta for two States representing the same data in different axis systems.

        Args:
            self (State): first State
            other (State, optional): Second State, None for judging.

        Returns:
            Tuple[np.ndarray, np.ndarray]: alpha and beta
        """
        ...

    def measure_airspeed(self: State, wind_vectors: Points) -> np.ndarray:
        """given a State and a set of wind vectors for each time instant calculate the airspeed.

        Args:
            self (State): input State
            wind_vectors (Points): wind vector at each time instant

        Returns:
            np.ndarray: airspeed for each instant
        """
        ...

    def fling_only(self: State) -> State:
        """return a subset of self with the ground data removed

        Args:
            self (State): _description_

        Returns:
            State: _description_
        """
        ...