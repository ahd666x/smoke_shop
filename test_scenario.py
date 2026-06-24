# test_scenario.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smoke_shop.settings')
django.setup()

from django.contrib.auth.models import User
from inventory.models import Category, Product, Supplier
from sales.models import Order, OrderItem, Payment, Customer
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum, F, DecimalField
import json

def print_separator(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def main():
    # 1. ایجاد کاربر تست
    user, created = User.objects.get_or_create(username='admin')
    if created:
        user.set_password('admin123')
        user.save()
        print("کاربر admin ساخته شد.")
    else:
        print("کاربر admin از قبل وجود دارد.")

    # 2. ایجاد دسته‌بندی‌ها
    cat_sigar, _ = Category.objects.get_or_create(name='سیگار')
    cat_winston = Category.objects.get_or_create(name='وینستون', parent=cat_sigar)[0]
    cat_pad, _ = Category.objects.get_or_create(name='پاد')

    # 3. ایجاد / بازنشانی محصولات (همه مقادیر پولی Decimal)
    product1, _ = Product.objects.get_or_create(barcode='111', defaults={'name': 'وینستون آبی'})
    product1.category = cat_winston
    product1.unit = 'pack'
    product1.purchase_price = Decimal('50000')
    product1.selling_price = Decimal('70000')
    product1.stock_quantity = 50
    product1.inventory_cost = Decimal('2500000')   # 50 * 50000
    product1.is_active = True
    product1.save()

    product2, _ = Product.objects.get_or_create(barcode='222', defaults={'name': 'پاد انبه'})
    product2.category = cat_pad
    product2.unit = 'piece'
    product2.purchase_price = Decimal('80000')
    product2.selling_price = Decimal('120000')
    product2.stock_quantity = 30
    product2.inventory_cost = Decimal('2400000')   # 30 * 80000
    product2.is_active = True
    product2.save()

    print("محصولات تست ایجاد / بازنشانی شدند.")
    print(f"وینستون: موجودی={product1.stock_quantity}, ارزش={product1.inventory_cost}")
    print(f"پاد: موجودی={product2.stock_quantity}, ارزش={product2.inventory_cost}")

    # 4. تأمین‌کننده
    supplier, _ = Supplier.objects.get_or_create(name='تأمین‌کننده اصلی')

    # 5. شبیه‌سازی خرید جدید (افزایش موجودی با قیمت متفاوت)
    print_separator("خرید جدید: 20 عدد وینستون با قیمت 55000")
    product1.stock_quantity += 20
    product1.inventory_cost += Decimal(20 * 55000)   # Decimal
    product1.purchase_price = Decimal('55000')
    product1.save()
    avg1 = product1.inventory_cost / product1.stock_quantity
    print(f"موجودی وینستون: {product1.stock_quantity}, ارزش: {product1.inventory_cost}, میانگین: {avg1:.2f}")

    # 6. فروش 5 عدد وینستون
    print_separator("فروش 5 عدد وینستون (بدون تخفیف)")
    order1 = Order.objects.create(
        user=user, is_paid=True,
        subtotal=Decimal(5*70000), total_tax=Decimal('0'), grand_total=Decimal(5*70000)
    )
    avg_before = (product1.inventory_cost / product1.stock_quantity).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    item1 = OrderItem.objects.create(
        order=order1, product=product1,
        quantity=5, unit_price=Decimal('70000'),
        purchase_cost=avg_before
    )
    product1.inventory_cost -= avg_before * 5
    product1.stock_quantity -= 5
    product1.save()
    Payment.objects.create(order=order1, amount=Decimal('350000'), method='cash')
    print(f"سفارش #{order1.id} ثبت شد. موجودی جدید: {product1.stock_quantity}, میانگین جدید: {product1.inventory_cost/product1.stock_quantity:.2f}")

    # 7. فروش 2 عدد پاد با تخفیف 10 درصدی
    print_separator("فروش 2 عدد پاد با تخفیف 10%")
    price_pad = product2.selling_price
    subtotal_pad = 2 * price_pad
    discount_pad = subtotal_pad * Decimal('0.1')
    grand_pad = subtotal_pad - discount_pad
    order2 = Order.objects.create(
        user=user, is_paid=True,
        subtotal=subtotal_pad, total_tax=Decimal('0'), grand_total=grand_pad,
        discount_type='percent', discount_value=10, discount_amount=discount_pad
    )
    avg_before2 = (product2.inventory_cost / product2.stock_quantity).quantize(Decimal('1'))
    item2 = OrderItem.objects.create(
        order=order2, product=product2,
        quantity=2, unit_price=price_pad,
        purchase_cost=avg_before2
    )
    product2.inventory_cost -= avg_before2 * 2
    product2.stock_quantity -= 2
    product2.save()
    Payment.objects.create(order=order2, amount=grand_pad, method='card')
    print(f"سفارش #{order2.id} ثبت شد. قابل پرداخت: {grand_pad}")

    # 8. برگشت کامل سفارش #order1
    print_separator("برگشت کامل سفارش #order1")
    if not Order.objects.filter(original_order=order1, is_return=True).exists():
        return_order_obj = Order.objects.create(
            user=user,
            customer=None,
            subtotal=order1.subtotal,
            total_tax=order1.total_tax,
            discount_amount=order1.discount_amount,
            grand_total=order1.grand_total,
            is_paid=True,
            is_return=True,
            original_order=order1
        )
        for item in order1.items.all():
            product = item.product
            qty = item.quantity
            pc = item.purchase_cost
            product.stock_quantity += qty
            product.inventory_cost += pc * qty
            product.save()
            OrderItem.objects.create(
                order=return_order_obj, product=product,
                quantity=qty, unit_price=item.unit_price,
                tax_amount=item.tax_amount, purchase_cost=pc
            )
        for pay in order1.payment_set.all():
            Payment.objects.create(order=return_order_obj, amount=-pay.amount, method=pay.method)
        print(f"برگشت سفارش #{order1.id} ایجاد شد. موجودی وینستون: {product1.stock_quantity}, میانگین: {product1.inventory_cost/product1.stock_quantity:.2f}")

    # 9. اصلاحیه سفارش #order2 (برگشت 1 عدد پاد و افزودن 3 عدد وینستون)
    print_separator("اصلاحیه سفارش #order2")
    original_order = order2
    return_qty = 1
    item_to_return = original_order.items.first()
    product = item_to_return.product
    avg_before_return = item_to_return.purchase_cost
    product.stock_quantity += return_qty
    product.inventory_cost += avg_before_return * return_qty
    product.save()
    item_to_return.returned_quantity = Decimal('1')
    item_to_return.is_returned = True
    item_to_return.save()
    winston = product1
    qty_new = 3
    price_new = winston.selling_price
    avg_new = (winston.inventory_cost / winston.stock_quantity).quantize(Decimal('1'))
    winston.stock_quantity -= qty_new
    winston.inventory_cost -= avg_new * qty_new
    winston.save()
    new_item = OrderItem.objects.create(
        order=original_order, product=winston,
        quantity=qty_new, unit_price=price_new,
        purchase_cost=avg_new
    )
    return_value = (item_to_return.unit_price * return_qty)
    new_value = price_new * qty_new
    diff = new_value - (return_value - (return_value * Decimal('0.1')))
    if diff > 0:
        Payment.objects.create(order=original_order, amount=diff, method='cash')
    original_order.subtotal = original_order.subtotal - return_value + new_value
    original_order.total_tax = Decimal('0')
    original_order.discount_amount = original_order.discount_amount - (return_value * Decimal('0.1'))
    original_order.grand_total = original_order.subtotal - original_order.discount_amount
    original_order.save()
    print(f"اصلاحیه انجام شد. مبلغ جدید سفارش: {original_order.grand_total}")
    print(f"موجودی پاد: {product2.stock_quantity}, وینستون: {product1.stock_quantity}")

    # 10. محاسبه سود و فروش امروز
    print_separator("گزارش نهایی امروز")
    today = timezone.localdate()
    gross = Order.objects.filter(created_at__date=today, is_paid=True, is_return=False)\
              .aggregate(total=Sum(F('subtotal') - F('discount_amount')))['total'] or Decimal('0')
    returns = Order.objects.filter(created_at__date=today, is_paid=True, is_return=True)\
              .aggregate(total=Sum(F('subtotal') - F('discount_amount')))['total'] or Decimal('0')
    sales = gross - returns
    print(f"فروش خالص امروز: {sales}")

    cost_normal = OrderItem.objects.filter(
        order__created_at__date=today, order__is_paid=True, order__is_return=False
    ).aggregate(
        total=Sum(F('purchase_cost') * (F('quantity') - F('returned_quantity')), output_field=DecimalField())
    )['total'] or Decimal('0')
    cost_return = OrderItem.objects.filter(
        order__created_at__date=today, order__is_paid=True, order__is_return=True
    ).aggregate(
        total=Sum(F('purchase_cost') * F('quantity'), output_field=DecimalField())
    )['total'] or Decimal('0')
    net_cost = cost_normal - cost_return
    profit = sales - net_cost
    print(f"بهای تمام‌شده خالص: {net_cost}")
    print(f"سود خالص امروز: {profit}")

    # 11. جمع‌بندی
    print_separator("خلاصه وضعیت محصولات")
    for p in Product.objects.filter(is_active=True):
        if p.stock_quantity > 0:
            avg = p.inventory_cost / p.stock_quantity
        else:
            avg = 0
        print(f"{p}: موجودی={p.stock_quantity}, ارزش={p.inventory_cost}, میانگین={avg:.0f}")

    print("\n✅ تست به پایان رسید. لطفاً خروجی بالا را برای تحلیل ارسال کنید.")

if __name__ == '__main__':
    main()