# Backend Workspace

This directory stores the StepMap backend service.

Planned stack:
- FastAPI
- PostgreSQL
- SQLAlchemy

Entity naming conventions:
- Trip
- Footprint
- MovieJob (reserved for V1.1)

## Step 2: Environment Configuration

1. Create `backend/.env` from `backend/.env.example`.
2. Fill all required values.
3. Install dependencies from `backend/requirements.txt`.
4. Start service with:
   - `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`

Startup behavior:
- If required settings are missing or invalid, startup fails immediately with
  a clear configuration error listing offending fields.

## Step 3: Logging and Error Handling Baseline

Implemented baseline:
- Structured request logging with fields:
  - `method`
  - `path`
  - `status_code`
  - `duration_ms`
- Unified error response shape:
  - `error_code`
  - `message`
- Error code classes:
  - `auth_error`
  - `validation_error`
  - `resource_error`
  - `system_error`

Verification hints:
- Successful request logs should contain all request fields above.
- Validation and handled errors should return consistent error payloads.

## Step 4: User Model and Migration Baseline

Implemented baseline:
- SQLAlchemy base and session setup
- `User` model with fields:
  - `id`
  - `email` (unique)
  - `password_hash`
  - `created_at`
- Alembic configuration and initial revision:
  - `alembic/versions/20260425_0001_create_users.py`

Migration command:
- `alembic upgrade head`

Verification hints:
- After migration, database must contain `users` table.
- Unique index on `email` must exist.
- Duplicate email insert should fail at database constraint level.

## Step 5: Registration Capability Baseline

Implemented baseline:
- Registration endpoint: `POST /auth/register`
- Input validation:
  - email format check
  - password length constraints
- Duplicate email handling:
  - returns consistent error payload with `error_code` and `message`
- Sensitive data protection:
  - response excludes `password_hash`
  - password stored as irreversible hash

Manual verification hints:
- Valid input returns `201` and user public fields only.
- Duplicate email returns `409` with readable error message.
- Invalid payload returns `422` validation error payload.
