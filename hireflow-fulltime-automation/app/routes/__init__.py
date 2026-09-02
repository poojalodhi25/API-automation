"""API routers."""

from app.routes.analytics import router as analytics_router
from app.routes.candidates import router as candidates_router
from app.routes.gmail_auth import router as gmail_router
from app.routes.health import router as health_router
from app.routes.jobs import router as jobs_router
from app.routes.outreach_routes import router as outreach_router
from app.routes.pages import router as pages_router
from app.routes.recruiters import router as recruiters_router

__all__ = [
    "analytics_router",
    "candidates_router",
    "gmail_router",
    "health_router",
    "jobs_router",
    "outreach_router",
    "pages_router",
    "recruiters_router",
]
