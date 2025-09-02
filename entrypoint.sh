#!/bin/bash
set -e
export PYTHONPATH="/app:$PYTHONPATH"

# Run Alembic migrations to create/update database tables
echo "Running database migrations..."
poetry run alembic upgrade head

# Start the application (binds to HOST/PORT from env inside src/main.py)
echo "Starting the application..."
exec poetry run python src/main.py
