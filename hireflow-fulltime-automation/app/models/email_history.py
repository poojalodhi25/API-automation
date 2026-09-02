"""Email send / reply history for duplicate prevention and follow-ups."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class EmailHistory(Base):
    __tablename__ = "email_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"))
    recruiter_id: Mapped[int] = mapped_column(ForeignKey("recruiters.id"))
    recruiter_email: Mapped[str] = mapped_column(String(255), index=True)
    subject: Mapped[str] = mapped_column(String(255), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    gmail_message_id: Mapped[str] = mapped_column(String(128), default="")
    status: Mapped[str] = mapped_column(String(40), default="sent")
    email_type: Mapped[str] = mapped_column(String(40), default="outreach")
    reply_detected: Mapped[bool] = mapped_column(default=False)
    replied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    follow_up_due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    follow_up_sent: Mapped[bool] = mapped_column(default=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    candidate: Mapped["Candidate"] = relationship(back_populates="emails")
    recruiter: Mapped["Recruiter"] = relationship(back_populates="emails")
