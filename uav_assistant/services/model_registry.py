from dataclasses import dataclass
from typing import Dict, List
from pathlib import Path

@dataclass
class ModelInfo:
    id: str
    name: str
    version: str
    description: str
    path: Path
    engine: str

class ModelRegistry:
    def __init__(self):
        base = Path(__file__).resolve().parents[1] / "models"
        self.models: Dict[str, ModelInfo] = {
            "mlr_battery_current": ModelInfo(
                id="mlr_battery_current",
                name="MLR",
                version="2.0",
                description="Multiple Linear Regression",
                path=base / "mlr.pkl",
                engine="mlr",
            ),
            "xgb": ModelInfo(
                id="xgb",
                name="XGB",
                version="1.0",
                description="XGBoost",
                path=base / "xgb.pkl",
                engine="xgb",
            ),
            "xgb_ar_lag1": ModelInfo(
                id="xgb_ar_lag1",
                name="XGB_AR",
                version="2.0",
                description="XGBoost with AutoRegression",
                path=base / "xgb_ar_lag1.pkl",
                engine="xgb_ar_lag1",
            ),
        }

    def list(self) -> List[ModelInfo]:
        return list(self.models.values())

    def get(self, model_id: str) -> ModelInfo:
        return self.models[model_id]
