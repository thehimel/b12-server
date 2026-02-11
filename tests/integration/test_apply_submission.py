import json

from urls import URL_APPLY_SUBMISSION


def test_apply_submission_success(client, valid_submission_payload, build_signed_body):
    raw_body, signature = build_signed_body(valid_submission_payload)
    response = client.post(
        URL_APPLY_SUBMISSION,
        content=raw_body,
        headers={"Content-Type": "application/json", "X-Signature-256": signature},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "receipt" in data
    assert data["receipt"].startswith("sub_")
    assert len(data["receipt"]) == 4 + 32  # "sub_" + 32 hex chars


def test_apply_submission_missing_signature(client, valid_submission_payload):
    body = json.dumps(valid_submission_payload, separators=(",", ":")).encode("utf-8")
    response = client.post(
        URL_APPLY_SUBMISSION,
        content=body,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 401


def test_apply_submission_invalid_signature(client, valid_submission_payload, build_signed_body):
    raw_body, _ = build_signed_body(valid_submission_payload)
    response = client.post(
        URL_APPLY_SUBMISSION,
        content=raw_body,
        headers={"Content-Type": "application/json", "X-Signature-256": "sha256" + "0" * 64},
    )
    assert response.status_code == 401


def test_apply_submission_invalid_payload(client, build_signed_body):
    invalid_payload = {"wrong": "shape"}
    raw_body, signature = build_signed_body(invalid_payload)
    response = client.post(
        URL_APPLY_SUBMISSION,
        content=raw_body,
        headers={"Content-Type": "application/json", "X-Signature-256": signature},
    )
    assert response.status_code in (400, 422)


def test_apply_submission_invalid_json(client, sign_raw):
    raw_body = b"not valid json"
    signature = sign_raw(raw_body)
    response = client.post(
        URL_APPLY_SUBMISSION,
        content=raw_body,
        headers={"Content-Type": "application/json", "X-Signature-256": signature},
    )
    assert response.status_code in (400, 422)
