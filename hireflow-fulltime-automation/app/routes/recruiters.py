"""Recruiter record APIs."""

from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session

from app.database.database import db_is_ready, get_db
from app.models.recruiter import Recruiter

router = APIRouter(prefix="/api/recruiters", tags=["recruiters"])


def _require_db() -> None:
    if not db_is_ready():
        raise HTTPException(status_code=503, detail="MySQL is not connected")


@router.post("")
def create_recruiter(
    recruiter_name: str = Form(""),
    recruiter_email: str = Form(...),
    role: str = Form(""),
    post_url: str = Form(""),
    job_description: str = Form(""),
    company: str = Form(""),
    location: str = Form("United States"),
    source: str = Form("manual"),
    db: Session = Depends(get_db),
):
    _require_db()
    row = Recruiter(
        recruiter_name=recruiter_name,
        recruiter_email=recruiter_email.lower().strip(),
        role=role,
        post_url=post_url,
        job_description=job_description,
        company=company,
        location=location,
        source=source,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"status": "success", "id": row.id}
