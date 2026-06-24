import jdatetime
from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def jalali_date(value, format="%Y/%m/%d %H:%M"):
    """
    تبدیل datetime یا date میلادی به شمسی با تبدیل خودکار به وقت تهران
    """
    if value is None:
        return ""

    # اگر datetime باشد، ابتدا به وقت محلی (تهران) تبدیل کن
    if hasattr(value, 'hour'):
        value = timezone.localtime(value)

    # حالا به jdatetime تبدیل کن
    if hasattr(value, 'hour'):
        j_date = jdatetime.datetime.fromgregorian(datetime=value)
    else:
        j_date = jdatetime.date.fromgregorian(date=value)

    return j_date.strftime(format)