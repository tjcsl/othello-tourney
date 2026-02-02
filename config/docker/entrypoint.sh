#!/bin/bash
set -e

uv sync
uv run manage.py collectstatic --noinput

until (PGPASSWORD=pwd psql -h "othello_postgres" -U "othello" -c '\q') 2> /dev/null; do
  >&2 echo "waiting for postgres"
  sleep 1
done

uv run manage.py makemigrations --noinput
uv run manage.py migrate


while true
do
    uv run manage.py runserver 0.0.0.0:8000
    sleep 1
done