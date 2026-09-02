"""USA market, W2/Direct Hire, and role/domain filters."""

from __future__ import annotations

import re

EMAIL_RE = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.I)

NON_USA_HINTS = (
    "india",
    "hyderabad",
    "bangalore",
    "bengaluru",
    "pune",
    "chennai",
    "noida",
    "gurgaon",
    "gurugram",
    "mumbai",
    "delhi",
    "pakistan",
    "bangladesh",
    "philippines",
    "canada only",
    "uk only",
    "united kingdom",
    "london",
    "toronto",
    "europe",
    "emea",
    "apac",
)

USA_HINTS = (
    "united states",
    "united states of america",
    "usa",
    "u.s.",
    "u.s.a",
    " us ",
    "remote - us",
    "remote, us",
    "us remote",
    "nationwide",
    "new york",
    "california",
    "texas",
    "florida",
    "washington",
    "illinois",
    "georgia",
    "north carolina",
    "new jersey",
    "virginia",
    "massachusetts",
    "pennsylvania",
    "arizona",
    "colorado",
    "ohio",
    "michigan",
    "seattle",
    "austin",
    "dallas",
    "atlanta",
    "chicago",
    "boston",
    "denver",
    "san francisco",
    "los angeles",
    "remote usa",
)

CONTRACT_HINTS = (
    "c2c",
    "corp to corp",
    "corp-to-corp",
    "bench",
    "on bench",
    "contract to hire only",
    "1099 only",
    "independent contractor only",
)

FULL_TIME_HINTS = (
    "full-time",
    "full time",
    "fulltime",
    "w2",
    "direct hire",
    "permanent",
    "salaried",
)


def extract_emails(text: str) -> list[str]:
    """Return unique email addresses found in free text."""
    if not text:
        return []
    found = [item.lower() for item in EMAIL_RE.findall(text)]
    unique: list[str] = []
    for email in found:
        if email not in unique:
            unique.append(email)
    return unique


def _blob(*parts: str) -> str:
    return " ".join(part or "" for part in parts).lower()


def is_usa_job(title: str, location: str, description: str) -> bool:
    """Keep USA / US-remote roles and drop obvious non-USA postings."""
    text = _blob(title, location, description)
    if any(hint in text for hint in NON_USA_HINTS) and not any(
        hint in f" {location.lower()} " for hint in ("usa", "united states", "us")
    ):
        if any(hint in _blob(location) for hint in NON_USA_HINTS):
            return False
    location_l = (location or "").lower()
    if any(hint in location_l for hint in USA_HINTS):
        return True
    if any(hint in text for hint in USA_HINTS):
        return True
    if location_l in {"remote", "united states", "us", "usa"}:
        return True
    return False


def is_full_time_w2_or_direct_hire(title: str, description: str, job_type: str = "") -> bool:
    """Prefer Full-Time / W2 / Direct Hire and skip C2C-bench contract posts."""
    text = _blob(title, description, job_type)
    if any(hint in text for hint in CONTRACT_HINTS) and not any(
        hint in text for hint in ("w2", "direct hire", "full-time", "full time")
    ):
        return False
    if any(hint in text for hint in FULL_TIME_HINTS):
        return True
    # Public job APIs often omit employment type; keep them if not clearly contract.
    return "contract" not in text


def matches_role(title: str, description: str, role: str, exclusion_keywords: str = "") -> bool:
    """Match a target role and drop excluded domain keywords."""
    text = _blob(title, description)
    role_l = (role or "").strip().lower()
    if role_l:
        tokens = [token for token in re.split(r"[,\|/]+", role_l) if token.strip()]
        if tokens and not any(token.strip() in text for token in tokens):
            # Allow partial token match on title
            title_l = (title or "").lower()
            if not any(token.strip() in title_l for token in tokens):
                return False
    exclusions = [item.strip().lower() for item in (exclusion_keywords or "").split(",") if item.strip()]
    if any(item in text for item in exclusions):
        return False
    return True
