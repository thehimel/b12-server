import logging
import uuid

from fastapi import Body, FastAPI, Request

from config.logging_config import configure_app_logging
from middleware.body_cache import CacheRequestBodyMiddleware
from schemas.apply import ApplySubmissionBody
from security.signature import verify_signature
from urls import URL_APPLY_SUBMISSION, URL_HEALTH, URL_ROOT

configure_app_logging()
logger = logging.getLogger(__name__)


app = FastAPI()
app.add_middleware(CacheRequestBodyMiddleware)


@app.get(URL_ROOT)
def root():
    return {"service": "b12-server", "docs": "/docs"}


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
    logger.info("Apply submission body: %s", raw_body.decode("utf-8"))
    signature_header = request.headers.get("X-Signature-256")
    verify_signature(raw_body, signature_header)
    logger.info("Signature verification successful")

    receipt = f"sub_{uuid.uuid4().hex}"
    return {"success": True, "receipt": receipt}
