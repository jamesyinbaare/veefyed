#!/usr/bin/env bash

set -e
set -x

# Let the DB start (wait a bit for PostgreSQL to be ready)
sleep 2

# Run migrations
uv run alembic upgrade head
