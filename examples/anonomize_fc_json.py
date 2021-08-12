from flightanalysis.fc_json import FCJson
from io import open
from json import dump

with open("examples/UK_England_Bristol_AMARC2002_F3A_P21_21_08_12_00000026.json") as f:
    fcj = FCJson.parse_fc_json(f)

anonymous = fcj.create_fc_json()

with open("new_json.json", "w") as f:
    dump(anonymous, f)
