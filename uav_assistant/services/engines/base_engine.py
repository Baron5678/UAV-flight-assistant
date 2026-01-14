import joblib
from datetime import datetime, timedelta
from typing import List

from uav_assistant.dtos.ForecastRequest import UAVState
from uav_assistant.dtos.ForecastResponse import ForecastPoint
from uav_assistant.services.telemetry_repository import TelemetryRepository
from uav_assistant.services.feature_builder import FeatureBuilder


class BaseEngine:
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

    def _predict_current(self, X) -> float:
        if "is_flying" in X.columns and X["is_flying"].iloc[0] ==  0:
            return 0.0

        return float(self.model.predict(X)[0])
