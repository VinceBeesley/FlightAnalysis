from flightanalysis.analysis.aircraft_analysis import Analysis, WindModelBuilder, WindModel, fit_wind


def test_fit_wind(st):
    wmodel = fit_wind(st, WindModelBuilder.power_law())

    assert isinstance(wmodel, WindModel)