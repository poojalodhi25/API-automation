"""Prepare and send personalized recruiter outreach with duplicate checks."""

from __future__ import annotations

import time
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.settings import BASE_DIR, settings
from app.models.candidate import Candidate
from app.models.email_history import EmailHistory
from app.models.recruiter import Recruiter
from app.services import gemini_client, gmail_client
from app.services.resume_processor import extract_resume_text, write_aligned_resume


def already_emailed(db: Session, candidate_id: int, recruiter_email: str) -> bool:
    """Duplicate prevention: one outreach thread per candidate + recruiter email."""
    existing = db.scalar(
        select(EmailHistory).where(
            EmailHistory.candidate_id == candidate_id,
            EmailHistory.recruiter_email == recruiter_email.lower(),
            EmailHistory.email_type == "outreach",
        )
    )
    return existing is not None


def send_outreach(
    db: Session,
    candidate_id: int,
    recruiter_ids: list[int],
    customize_resume: bool = True,
) -> dict:
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        return {"status": "error", "message": "Candidate not found"}
    if not gmail_client.gmail_connected():
        return {"status": "error", "message": "Connect Gmail in Settings first"}

    sent: list[dict] = []
    skipped: list[dict] = []
    resume_text = extract_resume_text(candidate.resume_path) if candidate.resume_path else ""

    for recruiter_id in recruiter_ids:
        recruiter = db.get(Recruiter, recruiter_id)
        if not recruiter:
            skipped.append({"id": recruiter_id, "reason": "Recruiter not found"})
            continue
        email = recruiter.recruiter_email.lower()
        if already_emailed(db, candidate.id, email):
            skipped.append({"email": email, "reason": "Duplicate: already emailed"})
            continue

        attachment = candidate.resume_path or None
        if customize_resume and resume_text:
            aligned = gemini_client.align_resume(
                resume_text,
                recruiter.role or candidate.primary_role,
                recruiter.job_description,
                candidate.name,
            )
            if aligned:
                out_path = (
                    BASE_DIR
                    / "generated_resumes"
                    / f"{candidate.id}_{recruiter.id}_aligned.docx"
                )
                write_aligned_resume(candidate.resume_path, aligned, str(out_path))
                attachment = str(out_path)

        subject, body = gemini_client.draft_outreach_email(
            candidate.name,
            recruiter.role or candidate.primary_role,
            recruiter.recruiter_name,
            recruiter.company,
            recruiter.job_description,
        )
        message_id = gmail_client.send_email(email, subject, body, attachment)
        due = datetime.utcnow() + timedelta(days=settings.followup_after_days)
        history = EmailHistory(
            candidate_id=candidate.id,
            recruiter_id=recruiter.id,
            recruiter_email=email,
            subject=subject,
            body=body,
            gmail_message_id=message_id,
            status="sent",
            email_type="outreach",
            follow_up_due_at=due,
        )
        recruiter.email_sent_status = "sent"
        db.add(history)
        db.commit()
        sent.append({"email": email, "subject": subject, "message_id": message_id})
        time.sleep(max(settings.email_send_delay_seconds, 0))

    return {"status": "success", "sent": sent, "skipped": skipped}


def send_due_followups(db: Session) -> dict:
    """Send follow-up emails that are due and have no reply yet."""
    if not gmail_client.gmail_connected():
        return {"status": "error", "message": "Connect Gmail in Settings first"}
    now = datetime.utcnow()
    due_rows = db.scalars(
        select(EmailHistory).where(
            EmailHistory.email_type == "outreach",
            EmailHistory.follow_up_sent.is_(False),
            EmailHistory.reply_detected.is_(False),
            EmailHistory.follow_up_due_at.is_not(None),
            EmailHistory.follow_up_due_at <= now,
        )
    ).all()
    sent = 0
    for row in due_rows:
        candidate = db.get(Candidate, row.candidate_id)
        recruiter = db.get(Recruiter, row.recruiter_id)
        if not candidate or not recruiter:
            continue
        subject = f"Follow-up: {row.subject}"
        body = (
            f"Hello {recruiter.recruiter_name or 'there'},\n\n"
            f"I wanted to follow up on my note about the {recruiter.role or candidate.primary_role} role. "
            "I remain interested in a USA Full-Time W2 / Direct Hire conversation.\n\n"
            f"Thank you,\n{candidate.name}\n"
        )
        message_id = gmail_client.send_email(recruiter.recruiter_email, subject, body, None)
        follow = EmailHistory(
            candidate_id=candidate.id,
            recruiter_id=recruiter.id,
            recruiter_email=recruiter.recruiter_email.lower(),
            subject=subject,
            body=body,
            gmail_message_id=message_id,
            status="sent",
            email_type="follow_up",
        )
        row.follow_up_sent = True
        db.add(follow)
        sent += 1
        time.sleep(max(settings.email_send_delay_seconds, 0))
    db.commit()
    return {"status": "success", "followups_sent": sent}
