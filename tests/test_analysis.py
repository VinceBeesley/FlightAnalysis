from flightanalysis.analysis import WindModelBuilder, WindModel, fit_wind


def test_fit_wind(st):
    wmodel = fit_wind(st, WindModelBuilder.power_law())

    assert isinstance(wmodel, WindModel)