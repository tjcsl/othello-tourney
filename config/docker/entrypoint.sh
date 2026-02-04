#!/bin/bash
set -e

uv sync
uv run manage.py collectstatic --noinput
uv run manage.py makemigrations --noinput
uv run manage.py migrate
uv run manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@admin.com',
        password='123'
    )
"


exec uv run manage.py runserver 0.0.0.0:8000