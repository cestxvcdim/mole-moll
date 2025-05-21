from django import template

register = template.Library()


@register.filter()
def media_path(val):
    if val:
        return f'/media/{val}'
    return '#'
