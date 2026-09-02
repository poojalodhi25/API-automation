"""Search full-time USA jobs from public APIs (not LinkedIn)."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config.settings import settings
from app.services.filters import (
    extract_emails,
    is_full_time_w2_or_direct_hire,
    is_usa_job,
    matches_role,
)

logger = logging.getLogger(__name__)

ARBEITNOW_URL = "https://www.arbeitnow.com/api/job-board-api"
USAJOBS_URL = "https://data.usajobs.gov/api/search"
ADZUNA_URL = "https://api.adzuna.com/v1/api/jobs/us/search/1"


def _normalize(
    title: str,
    company: str,
    location: str,
    description: str,
    url: str,
    source: str,
    job_type: str = "",
) -> dict[str, Any]:
    emails = extract_emails(description)
    return {
        "title": title.strip(),
        "company": company.strip(),
        "location": location.strip() or "United States",
        "description": description.strip(),
        "url": url.strip(),
        "source": source,
        "employment_type": job_type or "Full-Time",
        "is_usa": is_usa_job(title, location, description),
        "is_w2_or_direct_hire": is_full_time_w2_or_direct_hire(title, description, job_type),
        "emails": emails,
    }


def _search_arbeitnow(keyword: str, max_results: int) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    tokens = [token for token in keyword.lower().split() if token]
    try:
        with httpx.Client(timeout=20.0) as client:
            for page in range(1, 4):
                response = client.get(ARBEITNOW_URL, params={"page": page})
                response.raise_for_status()
                payload = response.json()
                for item in payload.get("data") or []:
                    title = str(item.get("title") or "")
                    company = str(item.get("company_name") or "")
                    location = str(item.get("location") or "")
                    description = str(item.get("description") or "")
                    url = str(item.get("url") or "")
                    job_types = ", ".join(item.get("job_types") or [])
                    blob = f"{title} {company} {description}".lower()
                    if tokens and not any(token in blob for token in tokens):
                        continue
                    jobs.append(
                        _normalize(
                            title, company, location, description, url, "arbeitnow", job_types
                        )
                    )
                    if len(jobs) >= max_results:
                        return jobs
    except Exception as exc:
        logger.warning("Arbeitnow search failed: %s", exc)
        return jobs
    return jobs


def _search_usajobs(keyword: str, location: str, max_results: int) -> list[dict[str, Any]]:
    if not settings.usajobs_api_key.strip():
        return []
    headers = {
        "Host": "data.usajobs.gov",
        "User-Agent": settings.usajobs_user_agent,
        "Authorization-Key": settings.usajobs_api_key,
    }
    params = {
        "Keyword": keyword,
        "LocationName": location or "United States",
        "ResultsPerPage": str(min(max_results, 25)),
    }
    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.get(USAJOBS_URL, headers=headers, params=params)
            response.raise_for_status()
            payload = response.json()
    except Exception as exc:
        logger.warning("USAJobs search failed: %s", exc)
        return []

    items = (
        payload.get("SearchResult", {}).get("SearchResultItems")
        or []
    )
    jobs: list[dict[str, Any]] = []
    for item in items:
        descriptor = item.get("MatchedObjectDescriptor") or {}
        locations = descriptor.get("PositionLocation") or []
        location_name = ", ".join(
            loc.get("LocationName", "") for loc in locations if loc.get("LocationName")
        )
        details = (descriptor.get("UserArea") or {}).get("Details") or {}
        description = str(details.get("JobSummary") or descriptor.get("QualificationSummary") or "")
        jobs.append(
            _normalize(
                str(descriptor.get("PositionTitle") or ""),
                str(descriptor.get("OrganizationName") or ""),
                location_name or "United States",
                description,
                str(descriptor.get("PositionURI") or ""),
                "usajobs",
                "Full-Time",
            )
        )
    return jobs


def _search_adzuna(keyword: str, location: str, max_results: int) -> list[dict[str, Any]]:
    if not (settings.adzuna_app_id.strip() and settings.adzuna_app_key.strip()):
        return []
    params = {
        "app_id": settings.adzuna_app_id,
        "app_key": settings.adzuna_app_key,
        "results_per_page": min(max_results, 20),
        "what": keyword,
        "where": location or "United States",
        "content-type": "application/json",
    }
    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.get(ADZUNA_URL, params=params)
            response.raise_for_status()
            payload = response.json()
    except Exception as exc:
        logger.warning("Adzuna search failed: %s", exc)
        return []

    jobs: list[dict[str, Any]] = []
    for item in payload.get("results") or []:
        location_obj = item.get("location") or {}
        location_name = str(location_obj.get("display_name") or location)
        jobs.append(
            _normalize(
                str(item.get("title") or ""),
                str((item.get("company") or {}).get("display_name") or ""),
                location_name,
                str(item.get("description") or ""),
                str(item.get("redirect_url") or ""),
                "adzuna",
                str(item.get("contract_time") or "full_time"),
            )
        )
    return jobs


def search_full_time_jobs(
    keyword: str,
    location: str = "United States",
    role: str = "",
    exclusion_keywords: str = "",
    max_results: int = 20,
) -> dict[str, Any]:
    """Query public job APIs, then apply USA / full-time / role filters."""
    collected: list[dict[str, Any]] = []
    sources_used: list[str] = []

    arbeitnow = _search_arbeitnow(keyword, max_results)
    if arbeitnow:
        sources_used.append("arbeitnow")
        collected.extend(arbeitnow)

    usajobs = _search_usajobs(keyword, location, max_results)
    if usajobs:
        sources_used.append("usajobs")
        collected.extend(usajobs)

    adzuna = _search_adzuna(keyword, location, max_results)
    if adzuna:
        sources_used.append("adzuna")
        collected.extend(adzuna)

    filtered: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for job in collected:
        url = job.get("url") or ""
        if url and url in seen_urls:
            continue
        if not job["is_usa"]:
            continue
        if not job["is_w2_or_direct_hire"]:
            continue
        if not matches_role(job["title"], job["description"], role or keyword, exclusion_keywords):
            continue
        if url:
            seen_urls.add(url)
        filtered.append(job)
        if len(filtered) >= max_results:
            break

    return {
        "status": "success",
        "sources": sources_used or ["none"],
        "count": len(filtered),
        "jobs": filtered,
        "note": (
            "Arbeitnow works without an API key. "
            "Add USAJOBS_API_KEY and optional Adzuna keys in .env for more results. "
            "This is not a LinkedIn integration."
        ),
    }
