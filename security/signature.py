import hmac
import hashlib

from decouple import config
from fastapi import HTTPException


def verify_signature(raw_body: bytes, signature_header: str | None) -> None:
    signing_secret = config("SIGNING_SECRET").encode("utf-8")
    if not signature_header or not signature_header.startswith("sha256="):
        raise HTTPException(status_code=401, detail="Missing or invalid X-Signature-256")

    expected_hex = signature_header.removeprefix("sha256=").strip().lower()
    if len(expected_hex) != 64 or not all(c in "0123456789abcdef" for c in expected_hex):
        raise HTTPException(status_code=401, detail="Invalid X-Signature-256 hex digest")

    digest = hmac.new(signing_secret, raw_body, hashlib.sha256).hexdigest().lower()
    if not hmac.compare_digest(digest, expected_hex):
        raise HTTPException(status_code=401, detail="Signature verification failed")
