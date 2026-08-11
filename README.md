# FastAPI Modular Monolith

A production-oriented Python 3.14 and FastAPI service organized as a modular monolith. The
reference `users` module includes domain rules, application use cases, SQLAlchemy persistence, and
FastAPI endpoints without coupling the inner layers to a framework.

## Stack

- Python 3.14.6 and uv 0.12.1
- FastAPI, Pydantic Settings, SQLAlchemy async, Alembic, and PostgreSQL
- Structlog JSON logging, request correlation, Prometheus metrics, and health probes
- Ruff, strict mypy, pytest with branch coverage, pip-audit, and architecture tests
- Non-root Docker image, migration-gated Compose stack, and immutable-action CI

Runtime and development dependencies are reproducibly pinned in `uv.lock`.

## Local development

Install Python 3.14.6 and uv, then run:

```powershell
Copy-Item .env.example .env
uv sync --all-groups
uv run alembic upgrade head
uv run serve
```

The API listens on `http://127.0.0.1:8000`; OpenAPI UI is at
`http://127.0.0.1:8000/docs`.

To use PostgreSQL and the production image locally:

```powershell
docker compose up --build
```

## API surface

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/users` | Register a user |
| `GET` | `/api/v1/users/{id}` | Retrieve a user |
| `GET` | `/health/live` | Process liveness |
| `GET` | `/health/ready` | Database readiness |
| `GET` | `/metrics` | Prometheus metrics |

## Quality gates

```powershell
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv run pip-audit
```

The test suite enforces at least 80% branch coverage and checks module import direction.

## Design

```text
HTTP / database adapters -> application use cases -> domain
             composition root wires dependencies
```

Business modules do not import another module's API or infrastructure. Cross-module collaboration
uses explicit `contracts` or durable integration events. See [Architecture](docs/architecture.md)
for module rules and the planned RAG boundary, and [Operations](docs/operations.md) for deployment
and production guidance.