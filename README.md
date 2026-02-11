# B12 Server

A small FastAPI service that accepts signed application submissions. Clients POST a JSON payload with applicant details
and an HMAC-SHA256 signature; the server validates the signature and payload and returns a unique receipt for
confirmation.

## What this is

- **Apply submission API** - `POST /apply/submission` accepts a canonical JSON body (timestamp, name, email, resume
  link, repository link, CI run link) and requires a valid `X-Signature-256` header (HMAC-SHA256 of the raw body using a
  shared secret). On success it returns a receipt you can use to confirm the submission.
- **Health check** - `GET /health` returns service status for load balancers or monitoring.

Validation includes: ISO 8601 timestamp, non-empty name (min 2 chars), valid email, and HTTP/HTTPS URLs for resume,
repository, and action-run links.

## Prerequisites

- Python 3.12+
- A signing secret (stored in `.env`)

## Getting started

### 1. Clone and enter the project

```bash
git clone https://github.com/thehimel/b12-server
cd <b12-server>
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

Copy the template and set your signing secret:

```bash
cp .env.template .env
```

Edit `.env` and set `SIGNING_SECRET` to the same value your clients use to sign requests (e.g. the value provided by B12
for the apply flow).

### 4. Run the server

```bash
uvicorn main:app --reload
```

Or use the included script:

```bash
./runserver.sh
```

The API will be available at `http://127.0.0.1:8000`. Interactive docs: `http://127.0.0.1:8000/docs`.

---

## API

### Health check

```http
GET /health
```

**Response (200)**

```json
{"status": "ok"}
```

---

### Apply submission

```http
POST /apply/submission
Content-Type: application/json
X-Signature-256: sha256=<hex-digest>
```

The body must be **UTF-8 JSON** with **keys in alphabetical order** and **no extra whitespace** (compact separators).
The header `X-Signature-256` must be `sha256=<hex-digest>`, where the digest is the **HMAC-SHA256** of the **raw request
body** using `SIGNING_SECRET` as the key.

**Example request body (canonical form)**

```json
{"action_run_link":"https://github.com/you/repo/actions/runs/123","email":"you@example.com","name":"Your Name","repository_link":"https://github.com/you/repo","resume_link":"https://example.com/resume","timestamp":"2026-01-06T16:59:37.571Z"}
```

**Example: computing the signature (Python)**

```python
import hmac
import hashlib
import json

payload = {
    "action_run_link": "https://github.com/you/repo/actions/runs/123",
    "email": "you@example.com",
    "name": "Your Name",
    "repository_link": "https://github.com/you/repo",
    "resume_link": "https://example.com/resume",
    "timestamp": "2026-01-06T16:59:37.571Z",
}
body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
digest = hmac.new(b"your-signing-secret", body, hashlib.sha256).hexdigest().lower()
# Header: X-Signature-256: sha256={digest}
```

**Success response (200)**

```json
{"success": true, "receipt": "sub_a1b2c3d4e5f6789012345678abcdef01"}
```

Save the `receipt` value to confirm your submission.

**Error responses**

| Status | Meaning                                                                 |
|--------|-------------------------------------------------------------------------|
| 400    | Invalid JSON or validation error (e.g. bad timestamp, invalid URL).     |
| 401    | Missing or invalid `X-Signature-256`, or signature verification failed. |
| 422    | Request body does not match the required schema.                        |

---

## Testing

Run the test suite from the project root:

```bash
pytest
```

Or with verbose output:

```bash
pytest -v
```

Tests include unit (schemas, signature verification), integration (API with TestClient), and a full submission flow. The
test suite uses a separate signing secret (see `tests/conftest.py`).

---

## Code style and pre-commit

The project uses **Black** (line length 120) and **isort** (profile `black`, line length 120). Config lives in
`pyproject.toml`.

**Pre-commit** runs formatting, generic checks, and tests before each commit. Setup once:

Hooks (see: [.pre-commit-config.yaml](.pre-commit-config.yaml))

- **pre-commit-hooks** - trailing whitespace, end-of-file fixer, check YAML/JSON/TOML, large files, merge conflicts, debug statements
- **Black** - format code
- **isort** - sort imports
- **pytest** - run the test suite

Run all hooks manually (e.g. before pushing):

```bash
pre-commit run --all-files
```

Format only (without running tests):

```bash
black .
isort .
```
