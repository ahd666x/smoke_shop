from decimal import Decimal
from .models import ProductTaxProfile

def calculate_taxes(item_subtotal, product):
    """
    ورودی: جمع مبلغ یک قلم کالا (قیمت واحد * تعداد) و شیء محصول
    خروجی: دیکشنری شامل جزئیات هر قانون و جمع کل مالیات
    """
    breakdown = {}
    cumulative = item_subtotal  # شروع با قیمت پایه
    total_tax = Decimal('0')
    try:
        profile = ProductTaxProfile.objects.get(product=product)
        rules = profile.tax_rules.all()
    except ProductTaxProfile.DoesNotExist:
        rules = []

    for rule in rules:
        if rule.applies_on == 'base_price':
            base = item_subtotal
        else:  # cumulative
            base = cumulative

        if rule.calculation_type == 'fixed_per_unit':
            # برای کالاهایی مثل سیگار که واحد بسته دارند، fixed_per_unit باید در quantity ضرب شود
            # در اینجا item_subtotal = unit_price * quantity, بنابراین مبلغ ثابت باید در تعداد ضرب شود
            # لذا پارامتر quantity را هم نیاز داریم. تابع اصلاح شود.
            pass




def calculate_item_tax(unit_price, quantity, product):
    item_subtotal = unit_price * quantity
    cumulative = item_subtotal
    total_tax = Decimal('0')
    tax_lines = []

    try:
        profile = ProductTaxProfile.objects.get(product=product)
        rules = profile.tax_rules.all()
    except ProductTaxProfile.DoesNotExist:
        return total_tax, tax_lines

    for rule in rules:
        if rule.applies_on == 'base_price':
            base = item_subtotal
        else:
            base = cumulative

        if rule.calculation_type == 'fixed_per_unit':
            tax_amount = rule.value * quantity  # value به ازای یک واحد
        else:  # percentage
            tax_amount = (base * rule.value) / Decimal('100')

        tax_lines.append({
            'rule_name': rule.name,
            'amount': tax_amount
        })
        total_tax += tax_amount
        cumulative += tax_amount  # برای مالیات‌های بعدی

    return total_tax, tax_lines