import json

from typing import Any, Dict
from django.template import Library
from django.utils.safestring import mark_safe, SafeString

register = Library()


@register.filter(is_safe=True)
def safe_json(obj: Dict[str, Any]) -> SafeString:
    return mark_safe(json.dumps(obj))
