#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
until nc -z postgres 5432; do
  sleep 1
done

echo "PostgreSQL is up"

echo "Running Alembic migrations..."
alembic -c /app/docker/alembic.ini upgrade head

echo "Starting Uvicorn..."
exec uvicorn uav_assistant.main:app --host 0.0.0.0 --port 8000
