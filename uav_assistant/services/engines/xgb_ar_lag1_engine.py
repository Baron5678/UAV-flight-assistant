from datetime import datetime, timedelta
from typing import List
from uav_assistant.dtos.ForecastRequest import UAVState
from uav_assistant.dtos.ForecastResponse import ForecastPoint
from uav_assistant.services.engines.xgb_engine import XgbEngine
from uav_assistant.services.feature_builder import FeatureBuilder


class XgbArEngine(XgbEngine):
    def __init__(self, model_path, telemetry_repo, horizon_step_sec=5):
        super().__init__(model_path, telemetry_repo, horizon_step_sec)
        self.last_current = 0.0

    def predict(self, uav: UAVState, horizon_seconds):
        self.last_current = 0.0
        capacity_mAh = float(uav.battery_capacity_mAh)
        soc_mAh = capacity_mAh * (uav.soc_percentage / 100.0)

        results: List[ForecastPoint] = []
        now = datetime.utcnow()
        dt = self.horizon_step_sec

        for t in range(dt, horizon_seconds + 1, dt):
            Xraw = self.repo.step(dt)
            X = FeatureBuilder.add_is_flying(Xraw)
            X = FeatureBuilder.insert_uav_state(X, uav, self.training_features)
            if "battery_current_lag1" in X.columns:
                X["battery_current_lag1"] = self.last_current

            pred_current_A = self._predict_current(X)

            self.last_current = pred_current_A

            mAh_used = (dt / 3600.0) * (pred_current_A * 1000.0)
            soc_mAh = max(0.0, soc_mAh - mAh_used)

            soc_percent = (soc_mAh / capacity_mAh) * 100.0
            ts = now + timedelta(seconds=t)

            results.append(ForecastPoint(timestamp=ts, value=soc_percent))

        return results
