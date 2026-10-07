import os

from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.utilities.flash import get_flashed_messages
from jinja2 import Environment, FileSystemLoader
from app.config import get_settings


template_env = Environment(loader = FileSystemLoader("app/templates",), autoescape=True)
template_env.globals['get_flashed_messages'] = get_flashed_messages
# Changes whenever the stylesheet does, so a browser never keeps showing an old cached copy.
template_env.globals['css_version'] = lambda: int(os.path.getmtime("app/static/css/app.css"))
templates = Jinja2Templates(env=template_env)
static_files = StaticFiles(directory="app/static")

router = APIRouter(tags=["Jinja Based Endpoints"], include_in_schema=get_settings().env.lower() in ["dev","development"])
api_router = APIRouter(tags=["API Endpoints"], prefix="/api")

# Route name each role lands on after login. Other roles have no page.
ROLE_HOME = {"student": "plan_view", "advisor": "submissions_view"}

from . import (index, login, plan, progress, submissions, logout, server_config)