from django import template

register = template.Library()


@register.filter
def has_management_permissions(user) -> bool:
    return user.is_authenticated and user.has_management_permission
