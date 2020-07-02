from django.conf import settings
from django.core.exceptions import ValidationError


def validate_tournament_rounds(value):
    if not (15 <= value <= settings.MAX_ROUND_NUM):
        raise ValidationError(
            f"Tournament has to have at least 15 rounds and at most {settings.MAX_ROUND_NUM} rounds"
        )
