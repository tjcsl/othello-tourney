#!/bin/sh
set -e

# Run migrations
python3 manage.py migrate

# Start the Django development server
python3 manage.py runserver 0.0.0.0:8000
