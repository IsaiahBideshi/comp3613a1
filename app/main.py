import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse, RedirectResponse

from app.config import get_settings
from app.routers import api_router, router, static_files, templates
from app.services.plan_service import PlanError
from app.utilities.flash import flash

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import ensure_db_and_tables

    # First boot on Render often races the free Postgres instance.
    ensure_db_and_tables()
    yield


app = FastAPI(
    middleware=[
        Middleware(SessionMiddleware, secret_key=get_settings().secret_key)
    ],
    lifespan=lifespan,
)

app.include_router(router)
app.include_router(api_router)
app.mount("/static", static_files, name="static")


@app.middleware("http")
async def recover_uninitialized_db(request: Request, call_next):
    """If a request hits a missing schema, create tables once and retry."""
    from app.database import recover_if_uninitialized

    try:
        return await call_next(request)
    except Exception as exc:  # noqa: BLE001 — catch then re-raise if not DB init
        if not recover_if_uninitialized(exc):
            raise
        logger.info("Retrying %s after database init", request.url.path)
        try:
            return await call_next(request)
        except Exception:
            # Schema exists now but the prior response may still need a refresh.
            if request.method.upper() == "GET":
                return RedirectResponse(url=str(request.url), status_code=303)
            raise


@app.get("/health")
async def health():
    return {"ok": True}


@app.exception_handler(PlanError)
async def plan_error_handler(request: Request, exc: PlanError):
    # A page or form request shows the message on the user's own start page; an autosave fetch gets a 400.
    if "text/html" in request.headers.get("accept", ""):
        flash(request, str(exc), "danger")
        return RedirectResponse(url=request.url_for("login_view"), status_code=status.HTTP_303_SEE_OTHER)
    return JSONResponse({"detail": str(exc)}, status_code=status.HTTP_400_BAD_REQUEST)


@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_redirect_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        request=request,
        name="401.html",
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=get_settings().app_host,
        port=get_settings().app_port,
        reload=get_settings().env.lower() != "production",
    )
