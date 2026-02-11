"""
E2E: full apply-submission flow with real app stack (middleware, signature, validation).
"""

from urls import URL_APPLY_SUBMISSION, URL_HEALTH


def test_full_submission_flow(client, valid_submission_payload, build_signed_body):
    raw_body, signature = build_signed_body(valid_submission_payload)
    response = client.post(
        URL_APPLY_SUBMISSION,
        content=raw_body,
        headers={"Content-Type": "application/json", "X-Signature-256": signature},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["receipt"].startswith("sub_")
    # Receipt is returned and can be used for confirmation
    receipt = data["receipt"]
    assert len(receipt) == 4 + 32
