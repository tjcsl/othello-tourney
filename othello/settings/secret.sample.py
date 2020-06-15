DEBUG = True
SECRET_KEY = 'y_xy)s%b_0h=#=y#3le5wfk!iy_+w#3#2j_&g@k^u-^qbrhxl2'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": 'othello',
        "USER": 'othello',
        "PASSWORD": 'pwd',
        "HOST": 'localhost',
        "PORT": '5432',
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [("127.0.0.1", 6379)], "capacity": 1500, "expiry": 2, },
    },
}
CELERY_BROKER_URL = "redis://localhost/1"

SOCIAL_AUTH_ION_KEY = ""
SOCIAL_AUTH_ION_SECRET = ""
