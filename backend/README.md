# Spending Tracker — Backend

FastAPI backend for the Spending Tracker application.

## Stack

- **Framework:** FastAPI
- **Language:** Python 3.13+
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Auth:** JWT access tokens + rotating refresh tokens
- **Dependency management:** [uv](https://docs.astral.sh/uv/)
- **Testing:** Pytest

## Architecture

Feature-based, clean-architecture layout with a strict one-way dependency
flow: **routes → services → repositories → models**. Nothing skips a layer.

```
app/
├── api/v1/endpoints/   # HTTP routes only: parse request, call a service, shape response
├── core/               # Framework-agnostic: security (hashing/JWT), domain exceptions
├── config/             # Pydantic Settings (env-driven configuration)
├── db/                 # SQLAlchemy engine, session, declarative Base
├── dependencies/        # FastAPI DI providers (get_db, get_current_user, service wiring)
├── middleware/         # Cross-cutting HTTP concerns (logging, security headers)
├── models/             # SQLAlchemy ORM models
├── repositories/       # All raw DB queries live here, nowhere else
├── schemas/            # Pydantic request/response DTOs (input + output validation)
├── services/           # Business logic - the only layer with actual "rules"
└── utils/              # Small framework-agnostic helpers (rate limiting, etc.)
```

**Why this split:** a route never imports a repository or the ORM directly,
and a service never imports `Session`/FastAPI. That means:
- Business logic (`services/`) is unit-testable with zero HTTP or real DB involved.
- Swapping the DB layer or adding a second delivery mechanism (a CLI, a
  background worker) never requires touching business rules.

## Sprint status

This repo is being built sprint-by-sprint per the project spec. **Sprint 1
(Authentication) is complete.** Later sprints (Dashboard, Income, Expenses,
Budgets, Savings Goals, Subscriptions, Reports, Notifications, Settings,
Profile) will each add their own `models/`, `schemas/`, `repositories/`,
`services/`, and `api/v1/endpoints/` files without changing this structure.

## Setup

```bash
cd backend
uv sync                      # installs dependencies from pyproject.toml
cp .env.example .env         # then fill in real secrets
```

Start Postgres (from the repo root, where docker-compose.yml lives):

```bash
docker compose up -d db
```

Run migrations:

```bash
uv run alembic upgrade head
```

Run the API:

```bash
uv run uvicorn app.main:app --reload
```

Interactive docs: `http://localhost:8000/docs` (Swagger) or `/redoc`.

## Running tests

```bash
uv run pytest
```

Tests run against an in-memory SQLite database for speed, not Postgres —
see `tests/conftest.py` for the reasoning and the tradeoff this implies
(Postgres-only column types in later sprints should get Postgres-backed
test coverage instead).

## Environment variables

See `.env.example` at the repo root. Required for Sprint 1:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLAlchemy connection string for Postgres |
| `JWT_SECRET_KEY` | Signing secret for access + refresh tokens — **must** be a long random value in any real deployment |
| `JWT_ALGORITHM` | Defaults to `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime (default 30) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime (default 7) |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend origins |
| `LOG_LEVEL` | Python logging level (default `INFO`) |

## Sprint 1 — Authentication

### Endpoints

| Method | Path | Auth required | Description |
|---|---|---|---|
| POST | `/api/v1/auth/register` | No | Create an account, returns tokens + user profile |
| POST | `/api/v1/auth/login` | No | Exchange credentials for a token pair |
| POST | `/api/v1/auth/refresh` | No (refresh token in body) | Rotates a refresh token for a new pair |
| POST | `/api/v1/auth/logout` | No (refresh token in body) | Revokes a refresh token |
| GET | `/api/v1/auth/me` | Yes (Bearer access token) | Returns the authenticated user's profile |
| GET | `/health` | No | Liveness/readiness check |

Full request/response schemas are in the auto-generated OpenAPI docs at `/docs`.

### Authentication flow (for frontend integration)

1. `POST /api/v1/auth/register` or `/login` → returns `{ access_token, refresh_token, token_type, user }`.
2. Send `Authorization: Bearer <access_token>` on every subsequent request.
3. When a request gets `401`, call `POST /api/v1/auth/refresh` with
   `{ "refresh_token": "..." }` to get a new pair. **Replace both tokens on
   the client** — the old refresh token is revoked as soon as it's used
   (rotation), so reusing it will fail.
4. On logout, call `POST /api/v1/auth/logout` with the current refresh
   token and discard both tokens client-side.

### Error response shape

Every handled error returns:
```json
{ "error_code": "unauthorized", "detail": "Incorrect email or password." }
```
`error_code` is stable and safe to branch on in the frontend; `detail` is
a human-readable message safe to display directly.

### Architectural decisions made in this sprint

- **Refresh tokens are persisted (hashed) in Postgres**, not just trusted
  as self-contained JWTs. This is what makes logout and rotation-reuse
  detection possible — a bare JWT can't be revoked before it expires.
- **Rotation on every refresh**: each `/refresh` call revokes the token it
  was given and issues a new one. Reuse of an already-rotated token is
  rejected, which is a standard signal of token theft.
- **Generic error messages for login** ("Incorrect email or password")
  regardless of whether the email exists or the password was wrong, to
  avoid account enumeration. Registration *does* reveal whether an email
  is taken — that's normal for registration flows and lower-risk.
- **Passwords capped/validated at 8+ chars, 1 letter, 1 digit** — a
  pragmatic baseline; tightening this (e.g. requiring a symbol) is a
  one-line change in `app/schemas/auth.py`.
- **Rate limiting** on `/register`, `/login`, `/refresh` uses a simple
  in-memory fixed-window counter (`app/utils/rate_limit.py`). This is
  explicitly *not* sufficient for a multi-instance deployment — it's a
  seam left ready to swap for a Redis-backed limiter without touching any
  calling code.
- **`bcrypt` is pinned to `4.0.1`** in `pyproject.toml`. Newer `bcrypt`
  releases (4.1+) have a breaking incompatibility with `passlib` 1.7.4
  that surfaces as a cryptic `ValueError` during password hashing — this
  was caught by the test suite while building this sprint.
- **Categories, budgets, and money-value handling** are out of scope for
  this sprint and will be addressed starting with the Income sprint.

## Git

- **Branch:** `feature/auth`
- **Suggested commit:** `feat(auth): implement JWT authentication with refresh token rotation`
