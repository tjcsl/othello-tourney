from django.conf import settings
from django.core.exceptions import ValidationError


def validate_game_time_limit(value):
    if not 1 <= value <= settings.MAX_TIME_LIMIT:
        raise ValidationError(
            f"Time Limit has to be between 1 and {settings.MAX_TIME_LIMIT} seconds"
        )
