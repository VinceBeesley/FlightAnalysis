
from flightanalysis.section import Section, State
from flightanalysis.environment import Environment, Environments
from flightanalysis.controls import Control, Controls
from flightanalysis.model.flow import Flow, Flows
from flightanalysis.model.coefficients import Coefficient, Coefficients

from flightanalysis.environment.wind import WindModel
from flightanalysis.model.constants import ACConstants
from flightanalysis.flightline import Box
from flightdata import Flight

contents = {
    "body": Section, 
    "wind": Section,
    "judge": Section,
    "control": Controls,
    "environment": Environments,
    "flow": Flows,
    "coeffs": Coefficients
}

class Analysis:
    def __init__(self, flight, data):
        self.flight= flight
        self.data = data

    def __getattr__(self, name):
        if name in self.data.keys():
            return self.data[name]
        for val in self.data.values():
            if hasattr(val, name):
                return getattr(val, name)
        
    @staticmethod
    def build(
        flight: Flight, 
        box: Box, 
        wmodel: WindModel, 
        consts: ACConstants,
        control_mapping: dict
    ):
        
        body = Section.from_flight(flight, box)
        judge = body.to_judging()
        controls = Controls.build(flight, control_mapping)
        environments = Environments.build(flight, body, wmodel)
        flows = Flows.build(body, environments)
        wind = judge.judging_to_wind(environments.gwind)
        coeffs = Coefficients.build(wind, flows, consts)

        return Analysis(
            flight,
            data = dict(
                body=body,
                wind=wind,
                judge=judge,
                control=controls,
                environment=environments,
                flow=flows,
                coeffs=coeffs
            )
        )

    def __getitem__(self, sli):
        return Analysis(
            self.flight[sli],
            {key: value[sli] for key, value in self.data.items()}    
        )

    

    