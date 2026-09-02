"""Job search and save APIs using public job boards."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import db_is_ready, get_db
from app.models.job import JobOpportunity
from app.models.recruiter import Recruiter
from app.schemas import JobSearchRequest
from app.services.filters import extract_emails
from app.services.job_search import search_full_time_jobs

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/search")
def search_jobs(payload: JobSearchRequest):
    result = search_full_time_jobs(
        keyword=payload.keyword,
        location=payload.location,
        role=payload.role,
        max_results=payload.max_results,
    )
    return result


@router.post("/save")
def save_jobs(jobs: list[dict], db: Session = Depends(get_db)):
    if not db_is_ready():
        raise HTTPException(status_code=503, detail="MySQL is not connected")
    saved_jobs = 0
    saved_contacts = 0
    for item in jobs:
        row = JobOpportunity(
            title=item.get("title") or "",
            company=item.get("company") or "",
            location=item.get("location") or "",
            description=item.get("description") or "",
            url=item.get("url") or "",
            source=item.get("source") or "",
            employment_type=item.get("employment_type") or "Full-Time",
            is_usa=bool(item.get("is_usa", True)),
            is_w2_or_direct_hire=bool(item.get("is_w2_or_direct_hire", True)),
        )
        db.add(row)
        saved_jobs += 1
        emails = item.get("emails") or extract_emails(item.get("description") or "")
        for email in emails:
            exists = (
                db.query(Recruiter)
                .filter(Recruiter.recruiter_email == email.lower())
                .first()
            )
            if exists:
                continue
            db.add(
                Recruiter(
                    recruiter_name="",
                    recruiter_email=email.lower(),
                    role=item.get("title") or "",
                    post_url=item.get("url") or "",
                    job_description=item.get("description") or "",
                    company=item.get("company") or "",
                    location=item.get("location") or "",
                    source=item.get("source") or "job_api",
                )
            )
            saved_contacts += 1
    db.commit()
    return {"status": "success", "saved_jobs": saved_jobs, "saved_contacts": saved_contacts}
