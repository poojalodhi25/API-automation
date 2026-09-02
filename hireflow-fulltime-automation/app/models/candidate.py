"""Candidate profile stored for outreach campaigns."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(50), default="")
    linkedin: Mapped[str] = mapped_column(String(255), default="")
    location: Mapped[str] = mapped_column(String(120), default="")
    relocation: Mapped[str] = mapped_column(String(120), default="")
    work_auth: Mapped[str] = mapped_column(String(120), default="")
    availability: Mapped[str] = mapped_column(String(120), default="")
    experience: Mapped[str] = mapped_column(String(120), default="")
    primary_role: Mapped[str] = mapped_column(String(120))
    search_roles: Mapped[str] = mapped_column(Text, default="")
    exclusion_keywords: Mapped[str] = mapped_column(Text, default="")
    resume_path: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    emails: Mapped[list["EmailHistory"]] = relationship(back_populates="candidate")
