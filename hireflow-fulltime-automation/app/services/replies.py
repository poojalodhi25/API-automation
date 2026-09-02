"""Detect recruiter replies and mark interested contacts."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.email_history import EmailHistory
from app.models.recruiter import Recruiter
from app.services import gmail_client

INTEREST_HINTS = (
    "interested",
    "available for a call",
    "let's talk",
    "lets talk",
    "please share",
    "send your",
    "interview",
    "next steps",
    "good fit",
)


def sync_replies(db: Session) -> dict:
    """Scan Gmail inbox and match messages to recruiters we already emailed."""
    if not gmail_client.gmail_connected():
        return {"status": "error", "message": "Connect Gmail in Settings first"}

    inbox = gmail_client.list_inbox_snippets()
    matched = 0
    interested = 0
    for message in inbox:
        from_header = (message.get("from") or "").lower()
        snippet = (message.get("snippet") or "").lower()
        subject = (message.get("subject") or "").lower()
        rows = db.scalars(select(EmailHistory).where(EmailHistory.status == "sent")).all()
        for row in rows:
            email = row.recruiter_email.lower()
            if email not in from_header:
                continue
            if not row.reply_detected:
                row.reply_detected = True
                row.replied_at = datetime.utcnow()
                matched += 1
            recruiter = db.get(Recruiter, row.recruiter_id)
            if recruiter:
                recruiter.email_sent_status = "replied"
                blob = f"{snippet} {subject}"
                if any(hint in blob for hint in INTEREST_HINTS):
                    recruiter.interested = "yes"
                    interested += 1
                elif recruiter.interested != "yes":
                    recruiter.interested = "replied"
    db.commit()
    return {
        "status": "success",
        "inbox_scanned": len(inbox),
        "replies_matched": matched,
        "interested_flagged": interested,
    }
