from django.db import models
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام")
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name="والد"
    )

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = [
        ('pack', 'بسته'),
        ('carton', 'کارتن'),
        ('piece', 'عدد'),
        ('kg', 'کیلوگرم'),
    ]
    name = models.CharField(max_length=200, verbose_name="نام کالا")
    barcode = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="بارکد")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="دسته‌بندی")
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pack', verbose_name="واحد")
    purchase_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="قیمت خرید (تومان)")
    selling_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="قیمت فروش (تومان)")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    stock_quantity = models.DecimalField(
        max_digits=12, decimal_places=3, default=0,
        validators=[MinValueValidator(0)], verbose_name="موجودی"
    )
    inventory_cost = models.DecimalField(
        max_digits=14, decimal_places=0, default=0,
        verbose_name="ارزش موجودی (تومان)"
    )
    is_featured = models.BooleanField(default=False, verbose_name="نمایش در دسترسی سریع")

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

    def __str__(self):
        if self.category:
            return f"{self.category.name} - {self.name}"
        return self.name


class StockMovement(models.Model):
    MOVEMENT_TYPES = [('in', 'ورود'), ('out', 'خروج')]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="کالا")
    quantity = models.DecimalField(max_digits=12, decimal_places=3, verbose_name="تعداد")
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES, verbose_name="نوع")
    reference = models.CharField(max_length=100, blank=True, verbose_name="مرجع")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ")

    class Meta:
        verbose_name = "گردش موجودی"
        verbose_name_plural = "گردش‌های موجودی"

    def save(self, *args, **kwargs):
        # BUG FIX: فقط رکورد StockMovement را ذخیره کن.
        # تغییر stock_quantity باید به صورت صریح در ویو انجام شود
        # تا از تداخل با product.save() در همان تراکنش جلوگیری شود.
        super().save(*args, **kwargs)

    def apply_to_product(self):
        """اعمال تغییر موجودی روی محصول - باید به صورت صریح در ویو صدا زده شود"""
        if self.movement_type == 'in':
            self.product.stock_quantity += self.quantity
        else:
            self.product.stock_quantity -= self.quantity
        self.product.save()

    def __str__(self):
        return f"{self.product} - {self.get_movement_type_display()}"


class Supplier(models.Model):
    name = models.CharField(max_length=200, verbose_name="نام")
    phone = models.CharField(max_length=15, blank=True, verbose_name="تلفن")
    address = models.TextField(blank=True, verbose_name="آدرس")

    class Meta:
        verbose_name = "تأمین‌کننده"
        verbose_name_plural = "تأمین‌کنندگان"

    def __str__(self):
        return self.name


class Purchase(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name="تأمین‌کننده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ")
    total_amount = models.DecimalField(max_digits=14, decimal_places=0, verbose_name="مبلغ کل (تومان)")
    is_paid = models.BooleanField(default=False, verbose_name="پرداخت شده")

    class Meta:
        verbose_name = "خرید"
        verbose_name_plural = "خریدها"

    def __str__(self):
        return f"خرید از {self.supplier.name} - {self.created_at.date()}"


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, related_name='items', on_delete=models.CASCADE, verbose_name="فاکتور خرید")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="کالا")
    quantity = models.PositiveIntegerField(verbose_name="تعداد")
    unit_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="قیمت واحد (تومان)")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="مالیات (تومان)")

    class Meta:
        verbose_name = "اقلام خرید"
        verbose_name_plural = "اقلام خرید"

    def __str__(self):
        return f"{self.product} × {self.quantity}"