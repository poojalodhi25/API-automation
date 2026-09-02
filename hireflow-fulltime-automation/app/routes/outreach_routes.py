"""Outreach, follow-up, and reply-sync APIs."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import db_is_ready, get_db
from app.schemas import OutreachRequest
from app.services.outreach import send_due_followups, send_outreach
from app.services.replies import sync_replies

router = APIRouter(prefix="/api/outreach", tags=["outreach"])


def _require_db() -> None:
    if not db_is_ready():
        raise HTTPException(status_code=503, detail="MySQL is not connected")


@router.post("/send")
def send(payload: OutreachRequest, db: Session = Depends(get_db)):
    _require_db()
    return send_outreach(
        db,
        payload.candidate_id,
        payload.recruiter_ids,
        payload.customize_resume,
    )


@router.post("/followups")
def followups(db: Session = Depends(get_db)):
    _require_db()
    return send_due_followups(db)


@router.post("/sync-replies")
def replies(db: Session = Depends(get_db)):
    _require_db()
    return sync_replies(db)
