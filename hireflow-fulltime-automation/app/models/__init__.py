"""SQLAlchemy models for candidates, jobs, recruiters, and email history."""

from app.models.candidate import Candidate
from app.models.email_history import EmailHistory
from app.models.job import JobOpportunity
from app.models.recruiter import Recruiter

__all__ = ["Candidate", "EmailHistory", "JobOpportunity", "Recruiter"]
