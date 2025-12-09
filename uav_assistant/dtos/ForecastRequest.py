from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class UAVState(BaseModel):
    soc_percentage: float
    wind_speed: float
    payload: float
    battery_capacity_mAh: int

class ForecastRequest(BaseModel):
    uav_state: UAVState
    model_id: str
    horizon_seconds: int = Field(..., ge=10, le=3600)
