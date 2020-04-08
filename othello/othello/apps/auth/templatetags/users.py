from django import template

register = template.Library()


@register.filter
def has_management_permissions(user):
    return not user.is_anonymous and user.has_management_permission
