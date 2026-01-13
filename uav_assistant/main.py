from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from uav_assistant.transport.routers.http import (waypoint, path, mission, path_summary, export_summeary)
from uav_assistant.transport.routers.ws import path as ws_path

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


BASE_DIR = Path(__file__).resolve().parent
TRANSPORT_DIR = BASE_DIR / "transport"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory=TRANSPORT_DIR / "templates")

app.mount(
    "/static",
    StaticFiles(directory=TRANSPORT_DIR / "static"),
    name="static",
)
app.include_router(waypoint.router)
app.include_router(path.router)
app.include_router(mission.router)
app.include_router(ws_path.router)
app.include_router(path_summary.router)
app.include_router(export_summeary.router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

