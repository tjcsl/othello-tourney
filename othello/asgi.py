import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "othello.settings")

django.setup()

from .routing import application  # noqa: E402,F401
