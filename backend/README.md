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

This repo is being built sprint-by-sprint per the project spec. **Sprints 1
(Authentication), 2 (Dashboard), and 3 (Income) are complete.** Later
sprints (Expenses, Budgets, Savings Goals, Subscriptions, Reports,
Notifications, Settings, Profile) will each add their own `models/`,
`schemas/`, `repositories/`, `services/`, and `api/v1/endpoints/` files
without changing this structure.

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

## Sprint 2 — Dashboard

### Endpoints

| Method | Path | Auth required | Description |
|---|---|---|---|
| GET | `/api/v1/dashboard/summary` | Yes (Bearer access token) | Monthly overview: totals, net profit/loss, savings, recent transactions |

Query params: `month` (1-12, default: current month), `year` (default: current year).

### Response shape

```json
{
  "month": 7,
  "year": 2026,
  "currency": "$",
  "total_income": "0",
  "total_expenses": "0",
  "net_profit_loss": "0",
  "total_savings": "0",
  "recent_transactions": [],
  "pending_features": ["income", "expenses", "savings_goals", "subscriptions"]
}
```

### Database changes

**None.** The Dashboard doesn't own any data - it aggregates across other
domains. No migration was added for this sprint.

### Architectural decisions made in this sprint

- **The Dashboard was built out of dependency order on purpose.** Income,
  Expenses, Savings Goals, and Subscriptions (the sprints Dashboard needs
  real numbers from) don't exist yet. Rather than skip Sprint 2 or invent
  those domains early, `DashboardService.get_summary()` returns a
  correctly-shaped response with zeroed totals and an empty transaction
  list, plus a `pending_features` array naming exactly which data sources
  aren't wired up yet.
- **The API contract is locked in now and won't change.** Each future
  sprint (Income, Expenses, Savings Goals, Subscriptions) will inject its
  repository into `DashboardService` and replace one hardcoded value with
  a real aggregation query, removing that feature from `pending_features`
  as it goes. No schema or route change is required when that happens.
- **Money fields use `Decimal`, not `float`,** in `DashboardSummary`
  (per the "avoid floating-point precision errors" requirement) - this
  convention should carry through to every future sprint that handles
  amounts.
- `router.py` from Sprint 1 was touched **only** to add one
  `include_router` line for the new dashboard routes - no other Sprint 1
  code changed.

### Integration Notes for Frontend

- Build the dashboard UI against the shape above **today** - it's stable.
- Check `pending_features` to decide whether to show a real number or a
  "coming soon" placeholder for each widget (e.g. hide/gray out the
  income/expense cards until `"income"`/`"expenses"` disappear from that
  array).
- `recent_transactions` will start being populated once Income (Sprint 3)
  and Expenses (Sprint 4) exist; its item shape (`id`, `type`, `category`,
  `amount`, `description`, `date`) is already final.
- Same auth header convention as Sprint 1: `Authorization: Bearer <access_token>`.

### Testing

`tests/test_dashboard_service.py` (unit) and `tests/test_dashboard_api.py`
(API-level, including the 401-without-auth and 422-invalid-month cases).
Run with `uv run pytest` - all 27 tests (19 from Sprint 1 + 8 new) pass.

### Git

- **Branch:** `feature/dashboard`
- **Suggested commit:** `feat(dashboard): add dashboard summary endpoint with placeholder aggregation`

## Sprint 3 — Income

### Endpoints

| Method | Path | Auth required | Description |
|---|---|---|---|
| POST | `/api/v1/income` | Yes | Create an income entry |
| GET | `/api/v1/income` | Yes | List income entries (paginated, filterable, sortable) |
| GET | `/api/v1/income/{income_id}` | Yes | Get one income entry |
| PATCH | `/api/v1/income/{income_id}` | Yes | Partially update an income entry |
| DELETE | `/api/v1/income/{income_id}` | Yes | Delete an income entry |

**Categories:** `salary`, `business`, `freelance`, `other`.

**List filters (query params):** `category`, `start_date`/`end_date`
(inclusive), `min_amount`/`max_amount`, `search` (matches `description`).
**Sorting:** `sort_by` (`date` | `amount` | `category` | `created_at`,
default `date`), `sort_order` (`asc` | `desc`, default `desc`).
**Pagination:** `page` (default 1), `page_size` (default 20, max 100).

### Response envelope for list endpoints

Every paginated list in this API (starting now, reused by every future
sprint) returns:
```json
{
  "items": [ ... ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

### Validation

- `amount` must be greater than 0 (enforced in the schema and as a DB
  `CHECK` constraint - defense in depth).
- `category` must be one of the four valid values (enforced in the
  schema and as a DB `CHECK` constraint).
- `description` optional, max 500 characters.
- Money is stored as `NUMERIC(12,2)`, never `FLOAT` - no floating-point
  rounding errors on financial data.

### Database changes

New `income` table - see migration below. Ownership is enforced at the
query level (every read/update/delete filters by `user_id`); a mismatched
or nonexistent id returns `404`, not `403`, so the API never confirms
whether a given id exists for another user.

### Migration

`alembic/versions/0002_create_income_table.py` (depends on `0001`). Run:
```bash
uv run alembic upgrade head
```

### Architectural decisions made in this sprint

- **Dashboard now reflects real income data** - `DashboardService` gained
  a required `IncomeRepository` dependency; `total_income` and
  `net_profit_loss` are computed from real rows, and `"income"` was
  removed from `pending_features`. This was the planned Sprint-2-to-3
  hookup, not scope creep.
- **`recent_transactions` is a "latest activity" feed, not scoped to the
  dashboard's selected month/year** - a conscious design decision (see
  the docstring on `DashboardService.get_summary`) since totals and
  "what did I just do" are different questions a dashboard answers.
- **PATCH uses `exclude_unset=True`**, not "skip if None": a field the
  client omits is left untouched, but a field explicitly sent as `null`
  (e.g. clearing `description`) is actually cleared. This distinction
  matters and is covered by a test.
- **Two real Python gotchas were caught by the test suite while building
  this sprint** and are worth knowing about for future sprints:
  1. A Pydantic field named `date` with the annotation `date | None = None`
     raises `TypeError: unsupported operand type(s) for |: 'NoneType' and 'NoneType'`.
     Cause: for an annotated assignment `x: T = v`, Python binds the
     *value* to the class namespace before evaluating the *annotation*,
     so if `x` and `T` are the same name, the annotation sees the
     already-assigned value instead of the type. Fixed by importing the
     type under an alias (`from datetime import date as date_type`) in
     `app/schemas/income.py`. Any future schema with a field literally
     named `date` (or `id`, `list`, etc. shadowing a needed name) should
     use the same alias pattern.
  2. A service method named `list` breaks return-type annotations
     (`-> list[Income]`) on every method defined *after* it in the same
     class, because the class body's local namespace now shadows the
     builtin `list`. Renamed to `list_for_user`. **Avoid naming any
     repository/service method `list`, `dict`, `type`, or other builtins**
     for this reason.
- **Rate limiting** was not added to Income endpoints - unlike auth,
  these aren't credential-guessing targets, so the existing per-endpoint
  opt-in (`app/utils/rate_limit.py`) wasn't necessary here.

### Integration Notes for Frontend

- Auth header convention unchanged: `Authorization: Bearer <access_token>`.
- Build income list/filter/sort UI against the query params and envelope
  documented above - this same pagination shape will be used by Expenses,
  Budgets, and every other list endpoint, so it's worth a shared frontend
  helper now.
- `PATCH` truly is partial - only send fields you want changed. To clear
  `description`, send `"description": null` explicitly.
- `404` (not `403`) is returned for another user's income id or an id
  that doesn't exist - don't rely on the distinction between those two
  cases; treat any `404` on these routes as "not accessible to you."
- The Dashboard's `total_income` and `recent_transactions` will now
  reflect real data - no frontend change needed there, it was already
  built against this contract in Sprint 2.

### Testing

`tests/test_income_service.py` (unit) and `tests/test_income_api.py`
(API-level: CRUD, validation, ownership, filtering, sorting, pagination).
`tests/test_dashboard_service.py` and `tests/test_dashboard_api.py` were
updated to reflect income now being wired in. Run with `uv run pytest` -
all 58 tests (27 from Sprints 1-2 + 31 new/updated) pass.

### Git

- **Branch:** `feature/income`
- **Suggested commit:** `feat(income): add income CRUD with pagination, filtering, and sorting`
