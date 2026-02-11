from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from urls import URL_APPLY_SUBMISSION


class CacheRequestBodyMiddleware(BaseHTTPMiddleware):
    """Cache POST body for apply submission so it can be read for signature and parsing."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path == URL_APPLY_SUBMISSION and request.method == "POST":
            body = await request.body()

            async def receive():
                return {"type": "http.request", "body": body}

            request = Request(request.scope, receive)
        return await call_next(request)
