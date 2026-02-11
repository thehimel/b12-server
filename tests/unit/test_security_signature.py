import hmac
import hashlib

import pytest
from fastapi import HTTPException

from security.signature import verify_signature

TEST_SECRET = b"test-signing-secret"


def test_verify_signature_valid():
    raw_body = b'{"action_run_link":"https://x.com/a","email":"a@b.com","name":"Ab","repository_link":"https://x.com/r","resume_link":"https://x.com/s","timestamp":"2026-01-06T16:59:37.571Z"}'
    digest = hmac.new(TEST_SECRET, raw_body, hashlib.sha256).hexdigest().lower()
    verify_signature(raw_body, f"sha256={digest}")  # no raise (env SIGNING_SECRET set in conftest)


def test_verify_signature_missing_header():
    with pytest.raises(HTTPException) as exc_info:
        verify_signature(b"{}", None)
    assert exc_info.value.status_code == 401


def test_verify_signature_wrong_prefix():
    with pytest.raises(HTTPException) as exc_info:
        verify_signature(b"{}", "hmac=abc" + "0" * 60)
    assert exc_info.value.status_code == 401


def test_verify_signature_wrong_digest():
    raw_body = b'{"name":"x"}'
    header = "sha256=" + "0" * 64
    with pytest.raises(HTTPException) as exc_info:
        verify_signature(raw_body, header)
    assert exc_info.value.status_code == 401
    assert "verification failed" in exc_info.value.detail.lower() or "signature" in exc_info.value.detail.lower()


def test_verify_signature_invalid_hex_length():
    with pytest.raises(HTTPException) as exc_info:
        verify_signature(b"{}", "sha256=abc")
    assert exc_info.value.status_code == 401
