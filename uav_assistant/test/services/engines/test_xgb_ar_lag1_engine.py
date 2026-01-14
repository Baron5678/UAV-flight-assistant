from pathlib import Path
from uav_assistant.services.engines.xgb_ar_lag1_engine import XgbArEngine
from uav_assistant.services.telemetry_repository import TelemetryRepository
from uav_assistant.dtos.ForecastRequest import UAVState

def test_xgb_ar_updates_lag():
    repo = TelemetryRepository(Path("data/test_dataset.csv"))
    engine = XgbArEngine(Path("uav_assistant/models/xgb_ar_lag1.pkl"), repo)

    uav = UAVState(
        soc_percentage=100,
        wind_speed=2.0,
        payload=0.5,
        battery_capacity_mAh=4000,
    )

    points = engine.predict(uav, horizon_seconds=20)

    assert engine.last_current != 0
    assert len(points) > 0


def test_xgb_autoregressive_engine_should_updates_lag_feature():
    repo = TelemetryRepository(Path("data/test_dataset.csv"))
    engine = XgbArEngine(Path("uav_assistant/models/xgb_ar_lag1.pkl"), repo)
    
    uav = UAVState(soc_percentage=50, wind_speed=0, payload=0, battery_capacity_mAh=5000)
    
    engine.predict(uav, horizon_seconds=10)

    assert engine.last_current != 0.0