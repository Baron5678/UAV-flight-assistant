from fastapi import APIRouter, Depends, HTTPException, Response
from uav_assistant.dtos.ForecastRequest import ForecastRequest
from uav_assistant.services.forecast_service import ForecastService

router = APIRouter(prefix="/forecast", tags=["forecast"])

def get_service():
    return ForecastService()

@router.get("/models")
def get_models(service: ForecastService = Depends(get_service)):
    return [
        {
            "id": m.id,
            "name": m.name,
            "version": m.version,
            "description": m.description,
        }
        for m in service.registry.list()
    ]

@router.post("/run")
def run_forecast(req: ForecastRequest, service: ForecastService = Depends(get_service)):
    return service.run(req)
