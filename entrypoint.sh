#!/bin/bash
set -e
export PYTHONPATH="/app:$PYTHONPATH"

# Run Alembic migrations to create/update database tables
echo "Running database migrations..."
poetry run alembic upgrade head

# Start the application
echo "Starting the application..."
poetry run python src/main.py