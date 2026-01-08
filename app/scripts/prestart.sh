#!/usr/bin/env bash

set -e
set -x

# Let the DB start (wait a bit for PostgreSQL to be ready)
sleep 2

# Ensure database exists (create if it doesn't)

export PGPASSWORD="${POSTGRES_PASSWORD:-postgres}"
DB_EXISTS=$(psql -h "${POSTGRES_HOST:-postgres}" -U "${POSTGRES_USER:-postgres}" -d postgres -tc \
  "SELECT 1 FROM pg_database WHERE datname = '${POSTGRES_DB:-skins_db}'" | xargs)

if [ -z "$DB_EXISTS" ]; then
  echo "Database ${POSTGRES_DB:-skins_db} does not exist. Creating it..."
  psql -h "${POSTGRES_HOST:-postgres}" -U "${POSTGRES_USER:-postgres}" -d postgres -c \
    "CREATE DATABASE \"${POSTGRES_DB:-skins_db}\""
else
  echo "Database ${POSTGRES_DB:-skins_db} already exists."
fi

# Run migrations
uv run alembic upgrade head
