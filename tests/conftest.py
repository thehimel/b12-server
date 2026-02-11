import hmac
import hashlib
import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure project root is on path when running pytest (e.g. from repo root or tests/)
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from main import app

TEST_SIGNING_SECRET = "test-signing-secret"


@pytest.fixture(autouse=True)
def env_signing_secret(monkeypatch):
    monkeypatch.setenv("SIGNING_SECRET", TEST_SIGNING_SECRET)


@pytest.fixture
def build_signed_body():
    """Fixture that returns (raw_body, signature) for a given payload."""

    def _build(payload: dict, secret: str = TEST_SIGNING_SECRET) -> tuple[bytes, str]:
        raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        digest = hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).hexdigest().lower()
        return raw, f"sha256={digest}"

    return _build


@pytest.fixture
def sign_raw():
    """Fixture that returns a function (raw_body: bytes) -> X-Signature-256 header value."""

    def _sign(raw_body: bytes, secret: str = TEST_SIGNING_SECRET) -> str:
        digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest().lower()
        return f"sha256={digest}"

    return _sign


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def valid_submission_payload():
    return {
        "action_run_link": "https://github.com/you/repo/actions/runs/123",
        "email": "you@example.com",
        "name": "Your Name",
        "repository_link": "https://github.com/you/repo",
        "resume_link": "https://example.com/resume",
        "timestamp": "2026-01-06T16:59:37.571Z",
    }
