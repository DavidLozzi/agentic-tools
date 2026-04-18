# Python Coding Guidelines

## Core stack
- **FastAPI:** Modular `APIRouter`s, `Depends` / `Security` for auth and request context, lifespan for startup/shutdown and long-lived clients.
- **Settings:** `pydantic_settings.BaseSettings` (or a thin `Settings` subclass) plus a single cached accessor (e.g. `get_settings()`) so env overrides are consistent; fail fast on missing required env vars.
- **Data:** Pydantic `BaseModel` for request/response bodies; prefer explicit schemas over untyped dicts.
- **HTTP client:** `httpx.AsyncClient` with `async with`, explicit timeouts, and `raise_for_status()` when failures should propagate; do not use `requests` in async services.
- **Tests:** `pytest` and `pytest-asyncio`; mock I/O with `AsyncMock`. Format with Black (120) and lint with Flake8.

## Layout and responsibilities
- Typical layout: `app/routes`, `app/services`, `app/models`, `app/utils`; add `app/orchestration` (or similar) only when multi-step workflows justify it.
- Handlers stay thin: validate, call services, return responses. Put integrations in dedicated clients/services; avoid duplicating helpers.
- Prefer plain functions and small modules until multiple implementations exist; introduce ABCs and orchestrators only when they remove real duplication (YAGNI).

## API, validation, and errors
- Version or prefix routes from settings; respect an application root / sub-path if the app is mounted behind a proxy.
- Document routes with summaries/descriptions; use `response_model` for structured JSON bodies.
- Use sensible HTTP verbs and status codes; map domain and downstream errors to consistent `HTTPException`s and optional global handlers—clear messages for clients, full detail in logs only.
- On startup, validate critical config and dependencies; exit or fail loudly if the service cannot run safely.

## Configuration and secrets
- No secrets in source; load from env (or `.env` consumed only by settings). Use flags or env toggles for environment-specific behavior with safe defaults.

## Async, outbound HTTP, and background work
- Use `async def` for I/O-bound work; keep the event loop free of blocking calls.
- Stream or iterate large responses with `async for` when appropriate; use `BackgroundTasks` for idempotent post-response work.
- Use `asyncio.create_task` only for fire-and-forget work that is safe and bounded; coordinate shared mutable state with clear ownership (locks, queues, or a single writer).
- Tie client lifetimes to lifespan or scoped factories so connections are closed cleanly.

## Logging
- Structured logs (JSON or stable key/value fields); carry a request or correlation id via middleware and `contextvars`.
- Redact secrets from logs; use levels deliberately (info for normal flow, debug behind toggles, warning/error for failures). Log durations for important operations when useful.

## Testing
- Mirror `app/` layout under `tests/`; share fixtures for common setup.
- Use `TestClient` for route-level tests; for async services hitting `httpx`, use `AsyncMock` or fixtures instead of the network. Add regression tests for fixed bugs; keep critical paths covered in CI.

## Security
- Protected routes must fail closed without valid auth. Never log or persist credentials.
- Parameterize or validate any user-controlled data used in shells, SQL, or paths. Use HTTPS outward; configure CORS and trusted hosts in middleware. Enforce authorization when data is tenant- or user-specific.

## Style
- Imports: stdlib, third party, local. Naming: `snake_case`, `CamelCase` classes, `UPPER_SNAKE_CASE` constants. Prefer readable code and short docstrings on public APIs over comments that restate the obvious.
- Update README or module docs when public behavior or setup changes.
