# Import template library
from django import template
from django.utils.translation import gettext as _

# Set register
register = template.Library()


# Register filter
@register.filter
def price(course):
    if course.price == 0:
        return _('Sin costo')
    else:
        return f'{course.price} {course.get_price_currency_display()}'
