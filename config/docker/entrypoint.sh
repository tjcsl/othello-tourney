#!/bin/sh
set -e

until (PGPASSWORD=pwd psql -h "othello_postgres" -U "othello" -c '\q') 2> /dev/null; do
  >&2 echo "waiting for postgres"
  sleep 1
done

# Run migrations
python3 manage.py migrate

# Start the Django development server
python3 manage.py runserver 0.0.0.0:8000
