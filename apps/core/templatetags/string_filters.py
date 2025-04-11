from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    old, new = arg.split(',', 1)  # Split on comma instead of space
    return value.replace(old, new)
