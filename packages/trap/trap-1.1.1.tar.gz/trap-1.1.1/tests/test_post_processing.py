import numpy as np
import pandas as pd

from trap.io import open_db
from trap.post_processing import construct_lightcurves, construct_varmetric


def test_construct_lightcurves():
    db_engine = open_db("sqlite", "tests/data/lofar1/default_export.db")
    reconstructed_lightcurves = construct_lightcurves(db_engine, attribute="peak_flux")

    expected_nr_lightcurves = 235
    assert len(reconstructed_lightcurves) == expected_nr_lightcurves
    assert np.all(reconstructed_lightcurves.columns == ["im_0", "im_1", "im_2"])
    expected_min = [0.02776169776916504, 0.01306371169859542, -0.0036572221340776256]
    np.testing.assert_allclose(reconstructed_lightcurves.min().values, expected_min)
    expected_max = [4.470382213592529, 4.453154563903809, 4.392852783203125]
    np.testing.assert_allclose(reconstructed_lightcurves.max().values, expected_max)
    expected_median = [0.09594719856977463, 0.09016537666320801, 0.0842289999127388]
    np.testing.assert_allclose(
        reconstructed_lightcurves.median().values, expected_median
    )


def test_construct_varmetric():
    db_engine = open_db("sqlite", "tests/data/lofar1/default_export.db")
    varmetric = construct_varmetric(db_engine)
    expected_median = {
        "newsource": 117.0,
        "v_int": 0.10600701080271989,
        "eta_int": 1.155251105515327,
        "sigma_rms_min": 42.12059388941379,
        "sigma_rms_max": 7.358573068100963,
        "lightcurve_max": 0.1202419325709343,
        "lightcurve_avg": 0.10827704519033432,
        "lightcurve_median": 0.10759570449590683,
        "nr_datapoints": 3.0,
        "wm_ra": 61.64806974620912,
        "av_ra_err": 0.0007610453378461557,
        "wm_dec": 65.05353379816607,
        "av_dec_err": 0.00032939548448496225,
    }
    # Columns for which we don't calculate mean but test in a different way leter in the function
    otherwise_expected_columns = ["first_detection_time", "first_image"]

    col_diff = set(expected_median.keys()).difference(varmetric.columns)
    assert not col_diff, f"Expected column not found in varmetric table: {col_diff}"
    col_diff_reverse = set(varmetric.columns).difference(expected_median.keys())
    for col in otherwise_expected_columns:
        col_diff_reverse.remove(col)
    assert (
        not col_diff_reverse
    ), f"Column found in varmetric table that is not in expected dict: {col_diff_reverse}"
    for key in varmetric.columns:
        if key in otherwise_expected_columns:
            continue
        np.testing.assert_allclose(varmetric[key].median(), expected_median[key])

    # In the current test dataset we can assume that once a source is detected it will not
    # turn NaN again. Given this assumption, verify that image of first detection correlates
    # correctly to the number of datapoints.
    nr_images = 3
    assert np.all(varmetric["first_image"] == nr_images - varmetric["nr_datapoints"])
    # Group by detection time and check that the detection times nicely align with the image id's when selecting the first_image of the groupby
    np.testing.assert_allclose(
        varmetric.groupby("first_detection_time")
        .mean("first_image")["first_image"]
        .values,
        np.arange(nr_images),
    )
