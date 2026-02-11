from datetime import datetime
from urllib.parse import urlparse

from pydantic import BaseModel, EmailStr, Field, field_validator


class ApplySubmissionBody(BaseModel):
    timestamp: str
    name: str = Field(..., min_length=2)
    email: EmailStr

    resume_link: str
    repository_link: str
    action_run_link: str

    @field_validator("timestamp")
    @classmethod
    def timestamp_iso8601(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("The timestamp must be valid ISO 8601")
        return v

    @field_validator("name")
    @classmethod
    def name_must_be_string(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("Name must be a string")
        return v

    @field_validator("resume_link", "repository_link", "action_run_link")
    @classmethod
    def valid_http_url(cls, v: str) -> str:
        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("Must be a valid http or https URL")
        return v
