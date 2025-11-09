#!/usr/bin/env bash
set -euo pipefail

SKIP_MIGRATIONS=${SKIP_MIGRATIONS:-0}
WAIT_DB_ATTEMPTS=${WAIT_DB_ATTEMPTS:-10}
WAIT_DB_SLEEP=${WAIT_DB_SLEEP:-3}

echo "Starting entrypoint script..."

# Wait for database to be ready (only for PostgreSQL)
if [ -n "${DATABASE_URL:-}" ] && [[ "$DATABASE_URL" == postgres* ]]; then
  echo "Waiting for PostgreSQL database..."
  for i in $(seq 1 $WAIT_DB_ATTEMPTS); do
    python -c 'import sys, psycopg2, urllib.parse;\ntry:\n d=urllib.parse.urlparse("'$DATABASE_URL'");\n conn=psycopg2.connect(dbname=d.path[1:], user=d.username, password=d.password, host=d.hostname, port=d.port or 5432); conn.close();\n print("DB ready")\n sys.exit(0)\nexcept Exception as e: print(e); sys.exit(1)' && break
    echo "DB not ready yet ($i/$WAIT_DB_ATTEMPTS)... sleeping $WAIT_DB_SLEEP seconds"
    sleep $WAIT_DB_SLEEP
    if [ "$i" -eq "$WAIT_DB_ATTEMPTS" ]; then
      echo "Database not available after $WAIT_DB_ATTEMPTS attempts, exiting."
      exit 1
    fi
  done
else
  echo "Using SQLite or DATABASE_URL not set, skipping PostgreSQL connection check"
fi

if [ "$SKIP_MIGRATIONS" != "1" ]; then
  echo "Running database migrations..."
  python manage.py migrate --noinput || { echo 'Migration failed'; exit 1; }
else
  echo "SKIPPING migrations as SKIP_MIGRATIONS=${SKIP_MIGRATIONS}"
fi

echo "Setting up admin permissions..."
python manage.py setup_admin_permissions || echo "setup_admin_permissions failed, continuing..."

# Only load fixture in non-prod or via explicit flag
if [ "${LOAD_FIXTURES:-0}" = "1" ]; then
  echo "Loading Lagos locations fixture..."
  python manage.py loaddata fixtures/lagos_locations.json || echo "Fixture load failed or already loaded."
else
  echo "Skipping fixture loading (set LOAD_FIXTURES=1 to enable)"
fi

# Create superuser if env vars are set
if [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  echo "Creating superuser..."
  python manage.py createsuperuser --noinput --email "$DJANGO_SUPERUSER_EMAIL" --username admin || echo "Superuser already exists"
fi

if [ -n "${STATIC_ROOT:-}" ]; then
  echo "Collecting static files to ${STATIC_ROOT}"
  python manage.py collectstatic --noinput
else
  echo "STATIC_ROOT not set, skipping collectstatic"
fi

echo "Starting Gunicorn..."
exec "$@"