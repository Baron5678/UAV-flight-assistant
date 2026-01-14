import pandas as pd
from uav_assistant.services.feature_builder import FeatureBuilder
from uav_assistant.dtos.ForecastRequest import UAVState

def test_add_is_flying_when_not_flying_should_encode_0():
    df = pd.DataFrame([{"speed_h_ms": 0.0, "alt": 0.0}])
    out = FeatureBuilder.add_is_flying(df)
    assert out["is_flying"].iloc[0] == 0


def test_add_is_flying_when_is_flying_should_encode_1():
    df = pd.DataFrame([{"speed_h_ms": 10.0, "alt": 25.0}])
    out = FeatureBuilder.add_is_flying(df)
    assert out["is_flying"].iloc[0] == 1

def test_insert_uav_state_should_contain_all_features():
    df = pd.DataFrame([{"wind_speed": 0.0, "payload": 567}])
    uav = UAVState(
        soc_percentage=80,
        wind_speed=5.0,
        payload=1.2,
        battery_capacity_mAh=5000,
    )

    out = FeatureBuilder.insert_uav_state(
        df,
        uav,
        training_features=["wind_speed", "payload", "missing"]
    )

    assert out.iloc[0]["wind_speed"] == 5.0
    assert out.iloc[0]["payload"] == 1.2
    assert out.iloc[0]["missing"] == 0.0
