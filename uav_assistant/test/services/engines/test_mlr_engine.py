from pathlib import Path
from uav_assistant.services.engines.mlr_engine import MlrEngine
from uav_assistant.services.telemetry_repository import TelemetryRepository
from uav_assistant.dtos.ForecastRequest import UAVState

def test_mlr_engine_runs():
    repo = TelemetryRepository(Path("data/test_dataset.csv"))
    engine = MlrEngine(Path("uav_assistant/models/mlr.pkl"), repo)

    uav = UAVState(
        soc_percentage=90,
        wind_speed=3.0,
        payload=1.0,
        battery_capacity_mAh=5000,
    )

    points = engine.predict(uav, horizon_seconds=30)

    assert len(points) > 0
    assert points[0].value <= 90
