"""Recruiter / hiring contact records."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Recruiter(Base):
    __tablename__ = "recruiters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recruiter_name: Mapped[str] = mapped_column(String(120), default="")
    recruiter_email: Mapped[str] = mapped_column(String(255), index=True)
    role: Mapped[str] = mapped_column(String(255), default="")
    post_url: Mapped[str] = mapped_column(String(500), default="")
    job_description: Mapped[str] = mapped_column(Text, default="")
    company: Mapped[str] = mapped_column(String(255), default="")
    location: Mapped[str] = mapped_column(String(255), default="")
    source: Mapped[str] = mapped_column(String(80), default="manual")
    email_sent_status: Mapped[str] = mapped_column(String(40), default="not_sent")
    interested: Mapped[str] = mapped_column(String(20), default="")
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    emails: Mapped[list["EmailHistory"]] = relationship(back_populates="recruiter")
