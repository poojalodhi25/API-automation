"""HTML pages."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config.settings import APP_DIR, settings
from app.database.database import db_is_ready, get_db
from app.models.candidate import Candidate
from app.models.email_history import EmailHistory
from app.models.job import JobOpportunity
from app.models.recruiter import Recruiter
from app.services.analytics import build_analytics
from app.services.gmail_client import gmail_connected

templates = Jinja2Templates(directory=str(APP_DIR / "templates"))
router = APIRouter()


def _ctx(request: Request, extra: dict | None = None) -> dict:
    data = {
        "request": request,
        "app_name": settings.app_name,
        "gmail_ready": gmail_connected(),
        "gemini_ready": settings.gemini_ready,
        "mysql_ready": db_is_ready(),
    }
    if extra:
        data.update(extra)
    return data


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    stats = {
        "usa_jobs": 0,
        "total_recruiters": 0,
        "emails_sent": 0,
        "reply_rate": 0,
        "interested": 0,
        "due_followups": 0,
    }
    if db_is_ready():
        stats = build_analytics(db)
    return templates.TemplateResponse("index.html", _ctx(request, {"stats": stats}))


@router.get("/candidates", response_class=HTMLResponse)
def candidates_page(request: Request, db: Session = Depends(get_db)):
    rows = db.query(Candidate).order_by(Candidate.id.desc()).all() if db_is_ready() else []
    return templates.TemplateResponse("candidates.html", _ctx(request, {"candidates": rows}))


@router.get("/search", response_class=HTMLResponse)
def search_page(request: Request):
    return templates.TemplateResponse("search.html", _ctx(request))


@router.get("/recruiters", response_class=HTMLResponse)
def recruiters_page(request: Request, db: Session = Depends(get_db)):
    rows = db.query(Recruiter).order_by(Recruiter.id.desc()).all() if db_is_ready() else []
    return templates.TemplateResponse("recruiters.html", _ctx(request, {"recruiters": rows}))


@router.get("/outreach", response_class=HTMLResponse)
def outreach_page(request: Request, db: Session = Depends(get_db)):
    extra = {"candidates": [], "recruiters": []}
    if db_is_ready():
        extra["candidates"] = db.query(Candidate).order_by(Candidate.id.desc()).all()
        extra["recruiters"] = db.query(Recruiter).order_by(Recruiter.id.desc()).all()
    return templates.TemplateResponse("outreach.html", _ctx(request, extra))


@router.get("/history", response_class=HTMLResponse)
def history_page(request: Request, db: Session = Depends(get_db)):
    rows = (
        db.query(EmailHistory).order_by(EmailHistory.sent_at.desc()).all()
        if db_is_ready()
        else []
    )
    return templates.TemplateResponse("history.html", _ctx(request, {"history": rows}))


@router.get("/analytics", response_class=HTMLResponse)
def analytics_page(request: Request, db: Session = Depends(get_db)):
    stats = {}
    if db_is_ready():
        stats = build_analytics(db)
    return templates.TemplateResponse("analytics.html", _ctx(request, {"stats": stats}))


@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request):
    return templates.TemplateResponse(
        "settings.html",
        _ctx(
            request,
            {
                "usajobs_ready": bool(settings.usajobs_api_key.strip()),
                "adzuna_ready": bool(
                    settings.adzuna_app_id.strip() and settings.adzuna_app_key.strip()
                ),
            },
        ),
    )
