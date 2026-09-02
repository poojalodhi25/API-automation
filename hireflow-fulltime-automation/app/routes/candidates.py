"""Candidate profile APIs."""

from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config.settings import BASE_DIR
from app.database.database import db_is_ready, get_db
from app.models.candidate import Candidate

router = APIRouter(prefix="/api/candidates", tags=["candidates"])


def _require_db() -> None:
    if not db_is_ready():
        raise HTTPException(status_code=503, detail="MySQL is not connected. Create the database and check .env.")


@router.get("")
def list_candidates(db: Session = Depends(get_db)):
    _require_db()
    rows = db.query(Candidate).order_by(Candidate.id.desc()).all()
    return {
        "status": "success",
        "candidates": [
            {
                "id": row.id,
                "name": row.name,
                "email": row.email,
                "primary_role": row.primary_role,
                "resume_path": row.resume_path,
            }
            for row in rows
        ],
    }


@router.post("")
async def create_candidate(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    linkedin: str = Form(""),
    location: str = Form(""),
    relocation: str = Form(""),
    work_auth: str = Form(""),
    availability: str = Form(""),
    experience: str = Form(""),
    primary_role: str = Form(...),
    search_roles: str = Form(""),
    exclusion_keywords: str = Form(""),
    resume: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    _require_db()
    resume_path = ""
    if resume and resume.filename:
        dest = BASE_DIR / "resumes" / resume.filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(await resume.read())
        resume_path = str(dest)
    row = Candidate(
        name=name,
        email=email,
        phone=phone,
        linkedin=linkedin,
        location=location,
        relocation=relocation,
        work_auth=work_auth,
        availability=availability,
        experience=experience,
        primary_role=primary_role,
        search_roles=search_roles,
        exclusion_keywords=exclusion_keywords,
        resume_path=resume_path,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"status": "success", "id": row.id}
