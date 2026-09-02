"""Pydantic request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class CandidateCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str = ""
    linkedin: str = ""
    location: str = ""
    relocation: str = ""
    work_auth: str = ""
    availability: str = ""
    experience: str = ""
    primary_role: str
    search_roles: str = ""
    exclusion_keywords: str = ""


class CandidateOut(CandidateCreate):
    id: int
    resume_path: str = ""
    created_at: datetime

    model_config = {"from_attributes": True}


class RecruiterCreate(BaseModel):
    recruiter_name: str = ""
    recruiter_email: EmailStr
    role: str = ""
    post_url: str = ""
    job_description: str = ""
    company: str = ""
    location: str = ""
    source: str = "manual"


class RecruiterOut(RecruiterCreate):
    id: int
    email_sent_status: str
    timestamp: datetime

    model_config = {"from_attributes": True}


class JobSearchRequest(BaseModel):
    keyword: str = Field(min_length=2)
    location: str = "United States"
    role: str = ""
    max_results: int = Field(default=20, ge=1, le=50)


class OutreachRequest(BaseModel):
    candidate_id: int
    recruiter_ids: list[int]
    customize_resume: bool = True
