from pathlib import Path
from starlette.templating import Jinja2Templates
from .routers import waypoints as wp
from .routers import paths as pp
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI()
templates = Jinja2Templates(directory=BASE_DIR / "templates")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(wp.router)
app.include_router(pp.router)

@app.get("/",response_class=HTMLResponse)
async def home(request:Request):
    return templates.TemplateResponse(request=request, name="base.html")


