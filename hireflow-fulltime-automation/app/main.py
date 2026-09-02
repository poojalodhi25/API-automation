"""HireFlow FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config.settings import APP_DIR, settings
from app.database.database import init_db
from app.routes.analytics import router as analytics_router
from app.routes.candidates import router as candidates_router
from app.routes.gmail_auth import router as gmail_router
from app.routes.health import router as health_router
from app.routes.jobs import router as jobs_router
from app.routes.outreach_routes import router as outreach_router
from app.routes.pages import router as pages_router
from app.routes.recruiters import router as recruiters_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        init_db()
    except Exception as exc:
        print(f"MySQL is not ready yet: {exc}")
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")

app.include_router(pages_router)
app.include_router(health_router)
app.include_router(candidates_router)
app.include_router(jobs_router)
app.include_router(recruiters_router)
app.include_router(outreach_router)
app.include_router(analytics_router)
app.include_router(gmail_router)
