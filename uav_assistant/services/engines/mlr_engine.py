import joblib
import pandas as pd
from datetime import datetime, timedelta
from typing import List

from uav_assistant.dtos.ForecastRequest import UAVState
from uav_assistant.dtos.ForecastResponse import ForecastPoint
from uav_assistant.services.telemetry_repository import TelemetryRepository


class MlrEngine:
    """
    Predicts battery current for each forecast step,
    then converts it to SoC using Coulomb counting.
    """

    def __init__(
        self,
        model_path,
        telemetry_repo: TelemetryRepository,
        horizon_step_sec: int = 5,
    ):
        self.model = joblib.load(model_path)
        self.repo = telemetry_repo
        self.horizon_step_sec = horizon_step_sec
        self.training_features = list(self.model.feature_names_in_)

    def predict(self, uav: UAVState, horizon_seconds: int) -> List[ForecastPoint]:
        # Load a random flight just to get base row structure
        base_df = self.repo.get_random_test_flight()
        last_row = base_df.tail(1)  # use last frame as template

        # Convert initial SoC (%) to mAh
        capacity_mAh = float(uav.battery_capacity_mAh)
        soc_mAh = capacity_mAh * (uav.soc_percentage / 100.0)

        results: List[ForecastPoint] = []
        now = datetime.utcnow()

        # forecast loop: one ML prediction per horizon step
        dt = self.horizon_step_sec

        for t in range(dt, horizon_seconds + 1, dt):
            X = self.repo.prepare_features(last_row, uav, self.training_features)

            pred_current_A = float(self.model.predict(X)[0])
            mAh_used = (dt / 3600.0) * (pred_current_A * 1000.0)

            soc_mAh -= mAh_used
            if soc_mAh < 0:
                soc_mAh = 0.0

            soc_percent = (soc_mAh / capacity_mAh) * 100.0

            # append forecast point
            ts = now + timedelta(seconds=t)
            results.append(ForecastPoint(timestamp=ts, value=soc_percent))

        return results
