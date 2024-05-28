DEBUG = True
SECRET_KEY = "y_xy)s%b_0h=#=y#3le5wfk!iy_+w#3#2j_&g@k^u-^qbrhxl2"

AUTHENTICATION_BACKENDS = ("othello.apps.auth.oauth.IonOauth2",)

if DEBUG:
    AUTH_PASSWORD_VALIDATORS = []
    AUTHENTICATION_BACKENDS += ("django.contrib.auth.backends.ModelBackend",)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "othello",
        "USER": "othello",
        "PASSWORD": "pwd",
        "HOST": "localhost",
        "PORT": "5432",
    }
}


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
            "capacity": 1500,
            "expiry": 2,
        },
    },
}
CELERY_BROKER_URL = "redis://localhost/1"

SOCIAL_AUTH_REDIRECT_IS_HTTPS = False
SOCIAL_AUTH_ION_KEY = ""
SOCIAL_AUTH_ION_SECRET = ""

# Message to display on the front page. HTML not escaped, be careful.
FRONT_PAGE_MESSAGE = ""

# Message to display on every page. HTML not escaped, be careful.
GLOBAL_MESSAGE = ""