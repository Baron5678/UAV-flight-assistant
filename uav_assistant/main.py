from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from uav_assistant.transport.routers import (waypoints, paths, mission)



BASE_DIR = Path(__file__).resolve().parent
TRANSPORT_DIR = BASE_DIR / "transport"

app = FastAPI()

templates = Jinja2Templates(directory=TRANSPORT_DIR / "templates")

app.mount(
    "/static",
    StaticFiles(directory=TRANSPORT_DIR / "static"),
    name="static",
)
app.include_router(waypoints.router)
app.include_router(paths.router)
app.include_router(mission.router)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

# progress bar
# number of points per algo
#