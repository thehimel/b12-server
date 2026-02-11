import uuid

from fastapi import Body, FastAPI, Request, HTTPException
from middleware.body_cache import CacheRequestBodyMiddleware
from schemas.apply import ApplySubmissionBody
from security.signature import verify_signature

from urls import URL_HEALTH, URL_APPLY_SUBMISSION

app = FastAPI()
app.add_middleware(CacheRequestBodyMiddleware)


@app.get(URL_HEALTH)
def health():
    return {"status": "ok"}


@app.post(URL_APPLY_SUBMISSION)
async def apply_submission(
    request: Request,
    _body: ApplySubmissionBody = Body(
        ...,
        description="Application submission payload",
        examples=[
            {
                "summary": "Default submission",
                "value": {
                    "action_run_link": "https://github.com/your/repo/actions/runs/123",
                    "email": "you@example.com",
                    "name": "Your Name",
                    "repository_link": "https://github.com/your/repo",
                    "resume_link": "https://example.com/resume",
                    "timestamp": "2026-01-06T16:59:37.571Z",
                },
            },
        ],
    ),
):
    raw_body = await request.body()
    signature_header = request.headers.get("X-Signature-256")
    verify_signature(raw_body, signature_header)

    receipt = f"sub_{uuid.uuid4().hex}"
    return {"success": True, "receipt": receipt}
