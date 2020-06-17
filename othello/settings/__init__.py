import os

import sentry_sdk
from celery.schedules import crontab
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

DEBUG = True
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = "y_xy)s%b_0h=#=y#3le5wfk!iy_+w#3#2j_&g@k^u-^qbrhxl2"

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "othello.csl.tjhsst.edu",
    "othello.tjhsst.edu",
]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [("localhost", 6379)], "capacity": 1500, "expiry": 2, },
    },
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "channels",
    "social_django",
    "django_celery_results",
    "othello.apps",
    "othello.apps.auth.apps.AuthConfig",
    "othello.apps.games.apps.GamesConfig",
    "othello.apps.tournaments.apps.TournamentsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
]

ROOT_URLCONF = "othello.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ]
        },
    }
]

ASGI_APPLICATION = "othello.routing.application"
WSGI_APPLICATION = "othello.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Authentication
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
AUTH_USER_MODEL = "authentication.User"

AUTHENTICATION_BACKENDS = ("othello.apps.auth.oauth.IonOauth2",)

SOCIAL_AUTH_USER_FIELDS = ["username", "first_name", "last_name", "email", "id"]
SOCIAL_AUTH_URL_NAMESPACE = "social"
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "othello.apps.auth.oauth.get_username",
    "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
)
SOCIAL_AUTH_ALWAYS_ASSOCIATE = True
SOCIAL_AUTH_LOGIN_ERROR_URL = "auth:error"
SOCIAL_AUTH_RAISE_EXCEPTIONS = False


LOGIN_URL = "auth:login"
LOGIN_REDIRECT_URL = "games:upload"
LOGOUT_REDIRECT_URL = "auth:index"

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/New_York"
USE_I18N = True
USE_L10N = True
USE_TZ = True
DATE_INPUT_FORMATS = [
    "%Y-%m-%dT%H:%M",
]

SESSION_SAVE_EVERY_REQUEST = True

# Celery
CELERY_RESULT_BACKEND = "django-db"
CELERY_BROKER_URL = "redis://localhost:6379/1"
CELERY_TIMEZONE = "America/New_York"
CELERY_BEAT_SCHEDULE = {
    "delete-old-games": {
        "task": "othello.apps.games.tasks.delete_old_games",
        "schedule": crontab(hour=2, minute=30, day_of_week="*/2"),
        "args": (),
    }
}

# Static
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "serve")
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
MEDIA_ROOT = os.path.join(BASE_DIR, "submissions")

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {"format": "{asctime}:{module}:{levelname} {message}", "style": "{"},
        "simple": {"format": "{levelname} {message}", "style": "{"},
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "logs/info.log"),
            "formatter": "verbose",
        },
        "console": {"class": "logging.StreamHandler", "formatter": "simple", },
    },
    "loggers": {
        "django": {"handlers": ["console", "file"], "level": "INFO", "propagate": True, },
        "othello": {"handlers": ["console", "file"], "level": "INFO", "propagate": True, },
    },
}


# Mail
MAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "mail.tjhsst.edu"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_SUBJECT_PREFIX = "[Othello]"
EMAIL_FROM = "othello-noreply@tjhsst.edu"
FORCE_EMAIL_SEND = True

# Othello Settings
SANDBOXING_ROOT = os.path.join(BASE_DIR, "sandboxing")
MODERATOR_ROOT = os.path.join(BASE_DIR, "moderator")
IMPORT_DRIVER = os.path.join(SANDBOXING_ROOT, "import_wrapper.py")
FIREJAIL_PROFILE = os.path.join(SANDBOXING_ROOT, "sandbox.profile")
JAILEDRUNNER_DRIVER = os.path.abspath(os.path.join(os.path.dirname(BASE_DIR), "run_ai_jailed.py"))

# Game settings
STALE_GAME = 6  # hours
YOURSELF_TIMEOUT = 300  # seconds
MAX_TIME_LIMIT = 15  # seconds

# Tournament settings
MAX_ROUND_NUM = 75  # amount of rounds
CONCURRENT_GAME_LIMIT = 5  # max amount of games that can be played at any time

try:
    from .secret import *
except ImportError:
    DEBUG = True
    SENTRY_DSN = ""


if not DEBUG:
    sentry_sdk.init(
        SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        send_default_pii=True,
    )
