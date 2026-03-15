from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    return value.split(delimiter)

@register.filter
def replace(value, args):
    old, new = args.split(',')
    return value.replace(old, new)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
