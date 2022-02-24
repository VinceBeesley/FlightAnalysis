from flightanalysis import FlightLine, Box
from typing import Union, Tuple
from flightdata import Flight
from flightanalysis.section.variables import secvars
from flightanalysis.section import Section, State
from geometry import Points
import numpy as np
from flightanalysis.base import Period, Instant

class Section(Period):
    def from_constructs(*args, **kwargs) -> Section: 
        """Construct a Section from a set of constructs

        Returns:
            Section: [description]
        """
        ...
        
    def copy(self, *args, **kwargs) -> Section: 
        """Copy the Section and replace the desired constructs

        Returns:
            Section: [description]
        """
        ...
    def from_csv(filename: str) -> Section: 
        """Read a Section from a csv file

        Args:
            filename (str): path to the csv file

        Returns:
            Section: [description]
        """
        ...
        
    def extrapolate_state(istate: State, duration: float, freq: float = None) -> Section: 
        """Extrapolate the state along its velocity and axis rate

        Args:
            istate (State): the first state
            duration (float): time (seconds) to extrapolate over
            freq (float, optional): frequency to extrapolate at. Defaults to Section.construct_freq.

        Returns:
            Section: [description]
        """
        ...
    def from_flight(flight: Union[Flight, str], box:Union[FlightLine, Box, str]) -> Section: 
        """Create a section from a Flight instance, rotated to the desired box.

        Args:
            flight (Union[Flight, str]): [description]
            box ([type], optional): [description]. Defaults to Union[FlightLine, Box, str].

        Returns:
            Section: [description]
        """
        ...

    def stack(sections: list) -> Section: 
        """stack two sections on top of each other, offset time indeces appropriately

        Args:
            sections (list): list of sections to stack

        Returns:
            Section: [description]
        """
        ...
    

    def to_judging(self: Section) -> Section: 
        """Converts a body or wind axis section to the Judging axis 
        (x axis aligned with velocity vector)

        Args:
            self (Section): [description]

        Returns:
            Section: [description]
        """
        ...

    def body_to_wind(self: Section, alpha: np.ndarray, beta: np.ndarray) -> Section: 
        """Converts a body frame Section to the Wind Axis for a given set of alphas and betas

        Args:
            self (Section): body frame section
            alpha (np.ndarray): alpha for every time instant
            beta (np.ndarray): alpha for every time instant

        Returns:
            Section: Secion in wind axis
        """
        ...

    def judging_to_wind(self: Section, wind: Points) -> Section:
        """converts a judging frame section to the wind axis given the wind at every time instant.

        Args:
            self (Section): Judging frame Section
            wind (Points): instantanious wind
        """
        ...

    
    def wind_to_body(self: Section, alpha: np.ndarray, beta: np.ndarray) -> Section:
        """convert a wind axis section to a body axis section

        Args:
            self (Section): Section in wind axis
            alpha (np.ndarray): alpha for each time instant
            beta (np.ndarray): beta for each time instant

        Returns:
            Section: body axis section
        """
        ...


    def measure_aoa(self: Section, other:Section=None) -> Tuple[np.ndarray, np.ndarray]: 
        """measure alpha and beta for two sections representing the same data in different axis systems.

        Args:
            self (Section): first section
            other (Section, optional): Second Section, None for judging.

        Returns:
            Tuple[np.ndarray, np.ndarray]: alpha and beta
        """
        ...

    def measure_airspeed(self: Section, wind_vectors: Points) -> np.ndarray:
        """given a section and a set of wind vectors for each time instant calculate the airspeed.

        Args:
            self (Section): input section
            wind_vectors (Points): wind vector at each time instant

        Returns:
            np.ndarray: airspeed for each instant
        """
        ...

    