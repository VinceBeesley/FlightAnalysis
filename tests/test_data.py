from flightanalysis.data import get_json_resource


def test_jsons():
    assert "p23" in jsons


def test_load_json_resurce():
    p23def = get_json_resource("p23_schedule")

    assert p23def[0]['info']['name'] == "Top Hat"