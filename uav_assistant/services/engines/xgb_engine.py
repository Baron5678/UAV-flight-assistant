from typing import List
from datetime import datetime, timedelta

from uav_assistant.services.engines.base_engine import BaseEngine
from uav_assistant.dtos.ForecastRequest import UAVState
from uav_assistant.dtos.ForecastResponse import ForecastPoint
from uav_assistant.services.feature_builder import FeatureBuilder
from uav_assistant.services.telemetry_repository import TelemetryRepository


class XgbEngine(BaseEngine):
    """
    XGBoost-based battery current predictor
    """

    def __init__(
        self,
        model_path,
        telemetry_repo: TelemetryRepository,
        horizon_step_sec: int = 5,
    ):
        super().__init__(model_path, telemetry_repo, horizon_step_sec)

    def predict(self, uav: UAVState, horizon_seconds: int):
        capacity_mAh = float(uav.battery_capacity_mAh)
        soc_mAh = capacity_mAh * (uav.soc_percentage / 100.0)

        results: List[ForecastPoint] = []
        now = datetime.utcnow()
        dt = self.horizon_step_sec

        for t in range(dt, horizon_seconds + 1, dt):
            Xraw = self.repo.step(dt)
            X = FeatureBuilder.add_is_flying(Xraw)
            X = FeatureBuilder.insert_uav_state(
                X, uav, self.training_features
            )

            # Inference
            pred_current_A = self._predict_current(X)

            # Coulomb counting
            mAh_used = (dt / 3600.0) * (pred_current_A * 1000.0)
            soc_mAh = max(0.0, soc_mAh - mAh_used)

            soc_percent = (soc_mAh / capacity_mAh) * 100.0

            results.append(
                ForecastPoint(
                    timestamp=now + timedelta(seconds=t),
                    value=soc_percent
                )
            )

        return results
