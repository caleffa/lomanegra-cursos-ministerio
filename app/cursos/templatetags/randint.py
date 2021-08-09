from random import randint
# Import template library
from django import template

# Set register
register = template.Library()


@register.simple_tag
def random_number(length=6):
    """
    Create a random integer with given length.
    For a length of 3 it will be between 100 and 999.
    For a length of 4 it will be between 1000 and 9999.
    """
    return randint(10**(length-1), (10**(length)-1))