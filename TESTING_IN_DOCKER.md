# Running tests in Docker (Compose)

## Prerequisites

Ensure the following environment files exist:
- `.env` file in the project root (required for Docker Compose variable interpolation)
- `envs/dev.env` - Development environment variables for the application and Postgres
- `envs/testing.env` - Testing environment variables for the test-runner service

## Running Tests

To run the test suite:

```bash
docker compose run --rm --build test-runner
```

This command will:
- Build the Docker image if needed
- Automatically start the Postgres service (via `depends_on` with health check)
- Wait for Postgres to be ready and healthy
- Install test dependencies at runtime
- Run database migrations (`alembic upgrade head`)
- Execute the test suite with `pytest -q`

## Configuration

The `test-runner` service uses `envs/testing.env` which provides:
- `DATABASE_URL` set to a plain `postgresql://...` connection string (without `+asyncpg`)
- `MOCK_DATABASE=true` for test configuration

Edit `envs/testing.env` if you need to change the test database connection or other test-specific settings.

## Alternative: Running Tests Without Database

If your tests don't need a real database, you can also run:

```bash
docker compose run --rm --build fastapi-app pytest -q
```

This runs pytest directly in the fastapi-app container without the full test-runner setup.
