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
                version="1.0",
                description="Multiple Linear Regression",
                path=base / "mlr_battery_current.pkl",
                engine="mlr",
            ),
            "arimax_soc": ModelInfo(
                id="arimax_soc",
                name="ARIMAX",
                version="1.0",
                description="ARIMAX for SoC forecasting",
                path=base / "arimax_soc.pkl",
                engine="arimax",
            ),
        }

    def list(self) -> List[ModelInfo]:
        return list(self.models.values())

    def get(self, model_id: str) -> ModelInfo:
        return self.models[model_id]
