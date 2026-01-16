import json
from typing import Any

from django.template import Library
from django.utils.safestring import SafeString, mark_safe

register = Library()


@register.filter(is_safe=True)
def safe_json(obj: dict[str, Any]) -> SafeString:
    return mark_safe(json.dumps(obj))
