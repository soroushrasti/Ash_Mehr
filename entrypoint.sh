#!/bin/bash
set -e
export PYTHONPATH="/app:$PYTHONPATH"
poetry run python src/main.py