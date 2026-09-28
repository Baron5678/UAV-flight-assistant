from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from uav_assistant.settings import DATABASES
from uav_assistant.transport.routers.http import (waypoint, path, mission, path_summary, export_summeary,
                                                  undo_last_path)
from uav_assistant.transport.routers.ws import path as ws_path
from uav_assistant.api import forecast_router

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


BASE_DIR = Path(__file__).resolve().parent
TRANSPORT_DIR = BASE_DIR / "transport"
ROUTING_UI = TRANSPORT_DIR / "static/routing_ui"
FORECASTING_UI = TRANSPORT_DIR / "static/forecasting_ui"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        for database in DATABASES:
            await database.connect()
        yield
    finally:
        for database in reversed(DATABASES):
            await database.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory=TRANSPORT_DIR / "templates")


app.mount("/routing", StaticFiles(directory=ROUTING_UI, html=True), name="routing-ui")
app.mount("/forecasting", StaticFiles(directory=FORECASTING_UI, html=True), name="forecasting-ui")

app.include_router(waypoint.router)
app.include_router(path.router)
app.include_router(mission.router)
app.include_router(ws_path.router)
app.include_router(path_summary.router)
app.include_router(export_summeary.router)
app.include_router(undo_last_path.router)
app.include_router(forecast_router.router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return RedirectResponse("/routing")

