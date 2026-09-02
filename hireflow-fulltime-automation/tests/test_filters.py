"""USA / full-time filter checks."""

from app.services.filters import extract_emails, is_full_time_w2_or_direct_hire, is_usa_job, matches_role


def test_extract_emails():
    text = "Contact jane.doe@acme.com or jobs@acme.com."
    assert extract_emails(text) == ["jane.doe@acme.com", "jobs@acme.com"]


def test_usa_job_keeps_us_remote():
    assert is_usa_job("Engineer", "Remote - US", "Full-time W2") is True


def test_usa_job_drops_india():
    assert is_usa_job("Engineer", "Hyderabad, India", "Office in Hyderabad") is False


def test_contract_only_is_rejected():
    assert is_full_time_w2_or_direct_hire("Dev", "C2C bench only") is False


def test_w2_is_kept():
    assert is_full_time_w2_or_direct_hire("Dev", "Full-Time W2 Direct Hire") is True


def test_exclusion_keywords():
    assert matches_role("Java Developer", "Spring Boot", "java", "mainframe") is True
    assert matches_role("COBOL Developer", "Mainframe", "java", "mainframe") is False
