#!/bin/sh
# wait-for-postgres.sh

set -e
  
host="$1"
shift
  
until PGPASSWORD=$DATABASE_PASSWORD psql -h "$host" -U $DATABASE_USER $DATABASE_NAME  -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
  
>&2 echo "Postgres is up - executing command"

python manage.py migrate --no-input

exec "$@"