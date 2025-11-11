from functools import reduce

import ee
import numpy as np
import pandas as pd
from loguru import logger
from models.s2biophys import eePipelinePredictMap, load_model_ensemble
from models.sl2p import load_SL2P_model
from src.utils_predict import aggregate_imagecollection_simple


def test_sl2p():
    ee.Initialize(project="ee-speckerfelix")

    # generate test data: s
    test_data = {
        "B11": 0.1375,
        "B12": 0.0608,
        "B3": 0.0743,
        "B4": 0.0456,
        "B5": 0.0778,
        "B6": 0.2109,
        "B7": 0.2923,
        "B8A": 0.3207,
        "cosRAA": -0.6115806237535122,
        "cosSZA": 0.8929870643543202,
        "cosVZA": 0.9947046936998751,
    }

    band_order_sl2p = [
        "cosSZA",
        "cosVZA",
        "cosRAA",
        "B3",
        "B4",
        "B5",
        "B6",
        "B7",
        "B8A",
        "B11",
        "B12",
    ]

    test_x = np.array([test_data[band] for band in band_order_sl2p]).reshape(1, -1)

    # test array prediction
    sl2p_mean_model, sl2p_std_model = load_SL2P_model("lai")
    lai_mean_pred = sl2p_mean_model.predict(test_x)
    lai_std_pred = sl2p_std_model.predict(test_x)

    # test ee.Image prediction
    test_img = (
        ee.Image.constant(list(test_data.values()))
        .rename(list(test_data.keys()))
        .select(band_order_sl2p)
    )

    lai_mean_img = sl2p_mean_model.ee_predict(test_img)
    lai_std_img = sl2p_std_model.ee_predict(test_img)
    lai_mean_img_pred = lai_mean_img.sample(ee.Geometry.Point(0, 0)).getInfo()[
        "features"
    ][0]["properties"]["output"]
    lai_std_img_pred = lai_std_img.sample(ee.Geometry.Point(0, 0)).getInfo()[
        "features"
    ][0]["properties"]["output"]

    assert np.isclose(
        lai_mean_pred, lai_mean_img_pred, atol=1e-6
    ), f"Mean prediction mismatch: array {lai_mean_pred} vs ee.Image {lai_mean_img_pred}"
    assert np.isclose(
        lai_std_pred, lai_std_img_pred, atol=1e-6
    ), f"StdDev prediction mismatch: array {lai_std_pred} vs ee.Image {lai_std_img_pred}"

    logger.debug(f"SL2P Client versus Server Side test passed.")


def test_specker():
    ee.Initialize(project="ee-speckerfelix")

    # generate test data:
    test_data = {
        "B11": 0.14229999482631683,
        "B12": 0.0658000037074089,
        "B2": 0.08879999816417694,
        "B3": 0.07859999686479568,
        "B4": 0.05009999871253967,
        "B5": 0.08590000122785568,
        "B6": 0.23029999434947968,
        "B7": 0.2985000014305115,
        "B8": 0.2948000133037567,
        "B8A": 0.33090001344680786,
        "psi": 127.7038803100586,
        "tto": 5.898953914642334,
        "tts": 26.748966217041016,
    }

    band_order_specker = [
        "B2",
        "B3",
        "B4",
        "B5",
        "B6",
        "B7",
        "B8",
        "B8A",
        "B11",
        "B12",
        "tts",
        "tto",
        "psi",
    ]

    test_x = np.array([test_data[band] for band in band_order_specker]).reshape(1, -1)
    # convert to dataframe with correct column names
    test_x_df = pd.DataFrame(test_x, columns=band_order_specker)

    # pred with array
    specker_model_ensemble = load_model_ensemble("laie")

    preds = np.stack(
        [
            model["pipeline"].predict(test_x_df)
            for model in specker_model_ensemble.values()
        ]
    )
    lai_ensemble_mean = np.mean(preds, axis=0)
    lai_ensemble_std = np.std(preds, axis=0)

    # pred with ee.Image
    test_img = (
        ee.Image.constant(list(test_data.values()))
        .rename(list(test_data.keys()))
        .select(band_order_specker)
    )

    test_imgc = ee.ImageCollection([test_img])
    gee_preds = {}
    for i, (model_name, model) in enumerate(specker_model_ensemble.items()):
        gee_preds[model_name] = eePipelinePredictMap(
            pipeline=model["pipeline"],
            imgc=test_imgc,
            trait="laie",
            model_config=model["config"],
            min_max_bands=model["min_max_bands"],
            min_max_label=None,
        )

    specker_imgc_preds = reduce(
        lambda x, y: x.merge(y),
        gee_preds.values(),
    )

    # merge predictions by calculating mean and stddev
    aggregated_preds = aggregate_imagecollection_simple(
        specker_imgc_preds, "laie", replications=5
    )

    specker_ee_pred = aggregated_preds.sample(ee.Geometry.Point(0, 0)).getInfo()[
        "features"
    ][0]["properties"]

    mean_ee_pred = specker_ee_pred["laie_mean"]
    std_ee_pred = specker_ee_pred["laie_stdDev"]

    assert np.isclose(
        lai_ensemble_mean, mean_ee_pred, atol=1e-6
    ), f"Mean prediction mismatch: array {lai_ensemble_mean} vs ee.Image {mean_ee_pred}"
    assert np.isclose(
        lai_ensemble_std, std_ee_pred, atol=1e-6
    ), f"StdDev prediction mismatch: array {lai_ensemble_std} vs ee.Image {std_ee_pred}"

    logger.debug(f"Specker et al. Client versus Server Side test passed.")


if __name__ == "__main__":
    test_sl2p()
    test_specker()
