from django.db import models
from django.conf import settings
from inventory.models import Product
from decimal import Decimal


class Customer(models.Model):
    name = models.CharField(max_length=200, verbose_name="نام")
    phone = models.CharField(max_length=15, unique=True, verbose_name="تلفن")
    credit = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="اعتبار (تومان)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "مشتری"
        verbose_name_plural = "مشتریان"

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="کاربر")
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="مشتری")
    customer_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="نام مشتری")
    customer_phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="تلفن مشتری")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    is_paid = models.BooleanField(default=False, verbose_name="پرداخت شده")
    subtotal = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="جمع کل")
    total_tax = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="جمع مالیات")
    discount_type = models.CharField(max_length=10, default='none', verbose_name="نوع تخفیف")
    discount_value = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="مقدار تخفیف")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="مبلغ تخفیف")
    grand_total = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="قابل پرداخت")
    is_held = models.BooleanField(default=False, verbose_name="نگهداری شده")
    held_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ نگهداری")
    is_return = models.BooleanField(default=False, verbose_name="فاکتور برگشتی")
    original_order = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='return_orders', verbose_name="فاکتور اصلی"
    )

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"

    def __str__(self):
        return f"سفارش #{self.id} - {self.created_at.strftime('%Y/%m/%d %H:%M')}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="سفارش")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="کالا")
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1, verbose_name="تعداد")
    unit_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="قیمت فروش واحد (تومان)")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="مالیات (تومان)")
    purchase_cost = models.DecimalField(
        max_digits=12, decimal_places=0, default=0,
        verbose_name="بهای تمام‌شده واحد (تومان)"
    )
    is_returned = models.BooleanField(default=False, verbose_name="برگشت خورده")
    returned_quantity = models.DecimalField(
        max_digits=10, decimal_places=3, default=0, verbose_name="تعداد برگشتی"
    )

    class Meta:
        verbose_name = "اقلام فروش"
        verbose_name_plural = "اقلام فروش"

    def __str__(self):
        return f"{self.product} × {self.quantity}"


class Payment(models.Model):
    METHOD_CHOICES = [('cash', 'نقد'), ('card', 'کارت'), ('credit', 'اعتباری')]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="سفارش")
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="مبلغ (تومان)")
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, verbose_name="روش پرداخت")
    paid_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان پرداخت")

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"

    def __str__(self):
        return f"{self.get_method_display()} - {self.amount}"