# management/templatetags/custom_filters.py
from django import template
from decimal import Decimal
register = template.Library()

@register.filter
def getattr(obj, attr_name):
    return getattr(obj, attr_name, '')




@register.filter
def get_field(obj, attr_name):
    """بازگرداندن مقدار یک فیلد از آبجکت"""
    return getattr(obj, attr_name, '')


@register.filter
def format_quantity(value):
    """نمایش مقدار به صورت صحیح اگر اعشار صفر باشد"""
    if value is None:
        return '0'
    try:
        decimal_value = Decimal(str(value))
        if decimal_value == decimal_value.to_integral_value():
            return str(int(decimal_value))
        return str(decimal_value).rstrip('0').rstrip('.') if '.' in str(decimal_value) else str(decimal_value)
    except (ValueError, TypeError):
        return str(value)