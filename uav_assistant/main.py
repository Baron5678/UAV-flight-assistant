from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from uav_assistant.api.forecast_router import router as forecast_router
from uav_assistant.transport.routers import (waypoints, paths, mission, ws_paths)

from fastapi.middleware.cors import CORSMiddleware


BASE_DIR = Path(__file__).resolve().parent
TRANSPORT_DIR = BASE_DIR / "transport"
STATIC_DIR = TRANSPORT_DIR / "static"

ROUTING_UI = STATIC_DIR / "routing_ui"
FORECASTING_UI = STATIC_DIR / "forecasting_ui"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(waypoints.router)
app.include_router(paths.router)
app.include_router(mission.router)
app.include_router(ws_paths.router)
app.include_router(forecast_router)

# Mount static UI folders
app.mount("/routing", StaticFiles(directory=ROUTING_UI, html=True), name="routing-ui")
app.mount("/forecasting", StaticFiles(directory=FORECASTING_UI, html=True), name="forecasting-ui")


# Serve index.html for each app root
@app.get("/routing", include_in_schema=False)
async def routing_root():
    return FileResponse(ROUTING_UI / "index.html")


@app.get("/forecasting", include_in_schema=False)
async def forecasting_root():
    return FileResponse(FORECASTING_UI / "index.html")

@app.get("/", response_class=HTMLResponse)
async def root_redirect():
    return RedirectResponse(url="/routing")

# progress bar
# number of points per algo
#