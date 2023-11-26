from django.template import Library

from utils import utils

register = Library()


@register.filter
def format_price(val):
    return utils.format_price(val)


@register.filter
def cart_total_amount(cart):
    return utils.cart_total_amount(cart)


@register.filter
def cart_total_price(cart):
    return utils.cart_total_price(cart)
