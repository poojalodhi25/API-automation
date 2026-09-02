"""Gemini API helpers for resume alignment and email wording."""

from __future__ import annotations

import logging

import httpx

from app.config.settings import settings

logger = logging.getLogger(__name__)


def _generate(prompt: str) -> str:
    if not settings.gemini_ready:
        return ""
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        with httpx.Client(timeout=45.0) as client:
            response = client.post(url, params={"key": settings.gemini_api_key}, json=payload)
            response.raise_for_status()
            data = response.json()
        return (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
            .strip()
        )
    except Exception as exc:
        logger.warning("Gemini request failed: %s", exc)
        return ""


def align_resume(resume_text: str, role: str, job_description: str, candidate_name: str) -> str:
    """Rewrite resume positioning for a full-time W2 / Direct Hire role."""
    prompt = (
        "You are helping a candidate apply for a USA Full-Time W2 or Direct Hire role.\n"
        f"Candidate name: {candidate_name}\n"
        f"Target role: {role}\n"
        f"Job description:\n{job_description[:4000]}\n\n"
        f"Current resume:\n{resume_text[:8000]}\n\n"
        "Rewrite a concise aligned resume. Keep facts truthful. "
        "Do not invent employers or degrees. Use plain text."
    )
    return _generate(prompt)


def draft_outreach_email(
    candidate_name: str,
    role: str,
    recruiter_name: str,
    company: str,
    job_description: str,
) -> tuple[str, str]:
    """Return (subject, body) for a professional recruiter email."""
    prompt = (
        "Write a short professional outreach email from a job seeker to a recruiter.\n"
        f"Candidate: {candidate_name}\n"
        f"Recruiter: {recruiter_name or 'Hiring Team'}\n"
        f"Company: {company or 'the company'}\n"
        f"Role: {role}\n"
        f"Job notes:\n{job_description[:2500]}\n\n"
        "USA Full-Time W2 / Direct Hire only. No C2C/bench language. "
        "Return exactly:\nSUBJECT: ...\nBODY:\n..."
    )
    generated = _generate(prompt)
    subject = f"Interest in {role} – {candidate_name}"
    body = (
        f"Hello {recruiter_name or 'there'},\n\n"
        f"I am {candidate_name}, and I am interested in the {role} opportunity"
        f"{' at ' + company if company else ''}. "
        "I am targeting USA Full-Time W2 / Direct Hire roles and would welcome a conversation.\n\n"
        "I have attached my resume.\n\n"
        "Thank you,\n"
        f"{candidate_name}\n"
    )
    if generated:
        lines = generated.splitlines()
        body_lines: list[str] = []
        capture_body = False
        for line in lines:
            if line.upper().startswith("SUBJECT:"):
                subject = line.split(":", 1)[1].strip() or subject
            elif line.upper().startswith("BODY:"):
                capture_body = True
            elif capture_body:
                body_lines.append(line)
        if body_lines:
            body = "\n".join(body_lines).strip() + "\n"
    return subject, body
