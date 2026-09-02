"""Campaign analytics for outreach, replies, and follow-ups."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.email_history import EmailHistory
from app.models.job import JobOpportunity
from app.models.recruiter import Recruiter


def build_analytics(db: Session) -> dict:
    total_candidates = db.scalar(select(func.count(Candidate.id))) or 0
    total_recruiters = db.scalar(select(func.count(Recruiter.id))) or 0
    usa_jobs = db.scalar(
        select(func.count(JobOpportunity.id)).where(JobOpportunity.is_usa.is_(True))
    ) or 0
    emails_sent = db.scalar(
        select(func.count(EmailHistory.id)).where(EmailHistory.status == "sent")
    ) or 0
    replies = db.scalar(
        select(func.count(EmailHistory.id)).where(EmailHistory.reply_detected.is_(True))
    ) or 0
    followups = db.scalar(
        select(func.count(EmailHistory.id)).where(EmailHistory.email_type == "follow_up")
    ) or 0
    interested = db.scalar(
        select(func.count(Recruiter.id)).where(Recruiter.interested == "yes")
    ) or 0
    replied_recruiters = db.scalar(
        select(func.count(Recruiter.id)).where(Recruiter.email_sent_status == "replied")
    ) or 0
    reply_rate = round((replies / emails_sent) * 100, 1) if emails_sent else 0.0
    interest_rate = round((interested / total_recruiters) * 100, 1) if total_recruiters else 0.0

    recent = db.scalars(
        select(EmailHistory).order_by(EmailHistory.sent_at.desc()).limit(10)
    ).all()
    due_followups = db.scalar(
        select(func.count(EmailHistory.id)).where(
            EmailHistory.follow_up_sent.is_(False),
            EmailHistory.reply_detected.is_(False),
            EmailHistory.follow_up_due_at.is_not(None),
            EmailHistory.follow_up_due_at <= datetime.utcnow(),
        )
    ) or 0

    return {
        "total_candidates": total_candidates,
        "total_recruiters": total_recruiters,
        "usa_jobs": usa_jobs,
        "emails_sent": emails_sent,
        "replies": replies,
        "followups": followups,
        "interested": interested,
        "replied_recruiters": replied_recruiters,
        "reply_rate": reply_rate,
        "interest_rate": interest_rate,
        "due_followups": due_followups,
        "recent": recent,
    }
