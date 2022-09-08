from flightanalysis import State
from flightanalysis.schedule.elements import El
from pathlib import Path
from flightplotting import plotsec


class AnalysisSummary:
    def __init__(self, element, flown, template):
        self.el = element
        self.fl=flown
        self.tp = template
    
    @staticmethod
    def parse(folder: Path, id: str):
        folder = Path(folder)
        return AnalysisSummary(
            El.from_json(folder / f"element_{id}.json"),
            State.from_csv(folder / f"flown_{id}.csv"),
            State.from_csv(folder / f"template_{id}.csv"),
        )

    def plot(self, **kwargs):
        if "color" in kwargs:
            kwargs.pop("color")
        fig=plotsec(self.fl, color="red", **kwargs)
        if "fig" in kwargs:
            kwargs.pop("fig")
        return plotsec(self.tp, color="blue", fig=fig, **kwargs)