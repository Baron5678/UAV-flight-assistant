from datetime import datetime
from typing import List
from pydantic import BaseModel

class ForecastPoint(BaseModel):
    timestamp: datetime
    value: float


class ForecastResponse(BaseModel):
    model_id: str
    generated_at: datetime
    points: List[ForecastPoint]
