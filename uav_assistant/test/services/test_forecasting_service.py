import pytest
from uav_assistant.services.forecast_service import ForecastService
from uav_assistant.dtos.ForecastRequest import ForecastRequest, UAVState

def test_forecast_service_run_integration():
    service = ForecastService()

    req = ForecastRequest(
        model_id="mlr_battery_current",
        horizon_seconds=30,
        uav_state=UAVState(
            soc_percentage=75,
            wind_speed=4.0,
            payload=1.2,
            battery_capacity_mAh=6000,
        ),
    )

    resp = service.run(req)

    assert resp.model_id == "mlr_battery_current"
    assert len(resp.points) > 0
    assert resp.points[0].value <= 75


@pytest.mark.parametrize("model_id", ["mlr_battery_current", "xgb", "xgb_ar_lag1"])
def test_forecast_service_supports_all_forecasting_engines(model_id):
    service = ForecastService()
    req = ForecastRequest(
        model_id=model_id,
        horizon_seconds=10,
        uav_state=UAVState(soc_percentage=100, wind_speed=0, payload=0, battery_capacity_mAh=5000)
    )
    
    resp = service.run(req)
    assert resp.model_id == model_id
    assert len(resp.points) > 0


@pytest.mark.parametrize("model_id", ["mlr_battery_current", "xgb", "xgb_ar_lag1"])
def test_forecast_predicted_battery_soc_is_non_increasing(model_id):
    service = ForecastService()
    req = ForecastRequest(
        model_id=model_id,
        horizon_seconds=60,
        uav_state=UAVState(soc_percentage=80, wind_speed=10, payload=2.0, battery_capacity_mAh=5000)
    )
    
    resp = service.run(req)
    values = [p.value for p in resp.points]
    
    for i in range(1, len(values)):
        assert values[i] <= values[i-1], f"SoC increased at point {i}"