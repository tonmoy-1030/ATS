from django import template

register = template.Library()

@register.filter
def endswith(value, arg):
    """Check if the value ends with the argument"""
    return str(value).lower().endswith(str(arg).lower())
