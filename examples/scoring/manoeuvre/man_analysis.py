from flightanalysis import ManoeuvreAnalysis
from json import load

with open("examples/scoring/manoeuvre/ma.json", "r") as f:
    data = load(f)


ma = ManoeuvreAnalysis.from_dict(data)

results = ma.intended.analyse(ma.aligned, ma.intended_template)

print(results.downgrade_df())

print(results.downgrade_df().sum())
