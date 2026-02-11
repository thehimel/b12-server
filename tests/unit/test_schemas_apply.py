import pytest
from pydantic import ValidationError

from schemas.apply import ApplySubmissionBody


def test_valid_submission():
    payload = {
        "timestamp": "2026-01-06T16:59:37.571Z",
        "name": "Jane Doe",
        "email": "jane@example.com",
        "resume_link": "https://example.com/resume",
        "repository_link": "https://github.com/jane/repo",
        "action_run_link": "https://github.com/jane/repo/actions/runs/1",
    }
    body = ApplySubmissionBody.model_validate(payload)
    assert body.name == "Jane Doe"
    assert body.email == "jane@example.com"


def test_timestamp_invalid_not_iso8601():
    payload = {
        "timestamp": "not-a-date",
        "name": "Jane",
        "email": "jane@example.com",
        "resume_link": "https://example.com/r",
        "repository_link": "https://github.com/jane/repo",
        "action_run_link": "https://github.com/jane/repo/actions/runs/1",
    }
    with pytest.raises(ValidationError) as exc_info:
        ApplySubmissionBody.model_validate(payload)
    assert "timestamp" in str(exc_info.value).lower() or "ISO" in str(exc_info.value)


def test_name_too_short():
    payload = {
        "timestamp": "2026-01-06T16:59:37.571Z",
        "name": "J",
        "email": "jane@example.com",
        "resume_link": "https://example.com/r",
        "repository_link": "https://github.com/jane/repo",
        "action_run_link": "https://github.com/jane/repo/actions/runs/1",
    }
    with pytest.raises(ValidationError):
        ApplySubmissionBody.model_validate(payload)


def test_name_must_be_string():
    payload = {
        "timestamp": "2026-01-06T16:59:37.571Z",
        "name": 123,
        "email": "jane@example.com",
        "resume_link": "https://example.com/r",
        "repository_link": "https://github.com/jane/repo",
        "action_run_link": "https://github.com/jane/repo/actions/runs/1",
    }
    with pytest.raises(ValidationError):
        ApplySubmissionBody.model_validate(payload)


def test_email_invalid():
    payload = {
        "timestamp": "2026-01-06T16:59:37.571Z",
        "name": "Jane",
        "email": "not-an-email",
        "resume_link": "https://example.com/r",
        "repository_link": "https://github.com/jane/repo",
        "action_run_link": "https://github.com/jane/repo/actions/runs/1",
    }
    with pytest.raises(ValidationError):
        ApplySubmissionBody.model_validate(payload)


def test_resume_link_not_http_url():
    payload = {
        "timestamp": "2026-01-06T16:59:37.571Z",
        "name": "Jane",
        "email": "jane@example.com",
        "resume_link": "ftp://example.com/resume",
        "repository_link": "https://github.com/jane/repo",
        "action_run_link": "https://github.com/jane/repo/actions/runs/1",
    }
    with pytest.raises(ValidationError):
        ApplySubmissionBody.model_validate(payload)


def test_repository_link_no_netloc():
    payload = {
        "timestamp": "2026-01-06T16:59:37.571Z",
        "name": "Jane",
        "email": "jane@example.com",
        "resume_link": "https://example.com/r",
        "repository_link": "https://",
        "action_run_link": "https://github.com/jane/repo/actions/runs/1",
    }
    with pytest.raises(ValidationError):
        ApplySubmissionBody.model_validate(payload)
