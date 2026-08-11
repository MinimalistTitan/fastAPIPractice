# Operations

## Configuration

All settings use the `APP_` prefix and can be supplied by environment variables or a local `.env`
file. Production mode rejects SQLite. Store database credentials in the deployment platform's
secret manager and URL-encode reserved characters in connection URLs.

## Deployment order

1. Build one immutable image from the committed `uv.lock`.
2. Back up the database and run `alembic upgrade head` as a one-off job.
3. Roll out API instances and wait for `/health/ready`.
4. Route traffic only after readiness succeeds.

Use backward-compatible expand/migrate/contract migrations for rolling deployments. Destructive
schema changes require a later release after old application instances are gone.

## Scaling and reliability

- Run one Uvicorn process per container and scale containers horizontally.
- Size SQLAlchemy pools so the aggregate across replicas stays below the database connection cap.
- Put TLS, request-size limits, timeouts, and edge rate limits at the ingress or API gateway.
- Scrape `/metrics`; collect JSON logs from stdout and propagate `x-request-id` at the edge.
- Alert on readiness failures, error ratio, latency, pool exhaustion, migration failures, and
  database saturation.
- Back up PostgreSQL, test restores, and define RPO/RTO targets before production launch.

The example users API is intentionally unauthenticated because identity and authorization policy
are business requirements, not generic middleware defaults. Add authentication and per-operation
authorization before exposing business endpoints publicly.