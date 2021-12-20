from typing import Iterator
from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    return value - arg

@register.filter
def the_range(value, arg):
    return range(value+arg)
    
@register.filter
def select(value, arg):
    return value[arg]