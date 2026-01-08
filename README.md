# Veefyed

My Skin Scanner - A FastAPI application for skin scanning and analysis.

## Prerequisites

- Docker
- Docker Compose

## Setup

### Environment Configuration

Before running the application, ensure you have a `.env` file in the project root with the following variables:

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=skins_db
```

This file is required for Docker Compose variable interpolation. The `.env` file is already listed in `.gitignore` and will not be committed to version control.

Additionally, ensure the following environment files exist(left sample in the repo):
- `envs/dev.env` - Development environment variables for the application and Postgres
- `envs/testing.env` - Testing environment variables for the test-runner service

## Development

To start the development environment with all services:

```bash
docker compose up --build
```

This command will:
- Build the Docker images
- Start the FastAPI application on port 8000 (accessible at http://localhost:8000)
- Start the PostgreSQL database on port 5432
- Run database migrations automatically via the prestart script

The services will continue running until you stop them with `Ctrl+C` or `docker compose down`.

## Testing

To run the test suite:

```bash
docker compose run --rm --build test-runner
```

This command will:
- Build the Docker image if needed
- Install test dependencies
- Wait for the Postgres service to be ready
- Run database migrations (`alembic upgrade head`)
- Execute the test suite with `pytest -q`

The `test-runner` service uses `envs/testing.env` which provides a `DATABASE_URL` set to a plain `postgresql://...` connection string (without `+asyncpg`). Edit `envs/testing.env` if you need to change the test database connection.

## Additional Notes

- The application uses PostgreSQL 18 as the database
- Database migrations are handled by Alembic
- Storage volumes are created automatically for database data and skin images
- For more detailed testing information, see [TESTING_IN_DOCKER.md](TESTING_IN_DOCKER.md)
