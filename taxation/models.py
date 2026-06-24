from django.db import models


class TaxRule(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    CALCULATION_CHOICES = [
        ('fixed_per_unit', 'مبلغ ثابت به ازای هر واحد'),
        ('percentage', 'درصدی'),
    ]
    calculation_type = models.CharField(max_length=20, choices=CALCULATION_CHOICES, verbose_name="نوع محاسبه")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="مقدار")
    BASE_CHOICES = [
        ('base_price', 'قیمت پایه (قبل از مالیات)'),
        ('cumulative', 'جمع قیمت پایه + مالیات‌های قبلی'),
    ]
    applies_on = models.CharField(max_length=20, choices=BASE_CHOICES, default='base_price', verbose_name="مبنای محاسبه")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب اجرا")

    class Meta:
        ordering = ['order']
        verbose_name = "قانون مالیاتی"
        verbose_name_plural = "قوانین مالیاتی"

    def __str__(self):
        return f"{self.name} ({self.get_calculation_type_display()})"


class ProductTaxProfile(models.Model):
    product = models.OneToOneField('inventory.Product', on_delete=models.CASCADE, verbose_name="محصول")
    tax_rules = models.ManyToManyField(TaxRule, blank=True, verbose_name="قوانین مالیاتی")

    class Meta:
        verbose_name = "پروفایل مالیاتی"
        verbose_name_plural = "پروفایل‌های مالیاتی"

    def __str__(self):
        return f"Tax Profile: {self.product}"


class TaxLine(models.Model):
    order_item = models.ForeignKey('sales.OrderItem', related_name='tax_lines', on_delete=models.CASCADE, verbose_name="آیتم فروش")
    rule_name = models.CharField(max_length=100, verbose_name="نام قانون")
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="مبلغ (تومان)")

    class Meta:
        verbose_name = "خط مالیاتی"
        verbose_name_plural = "خطوط مالیاتی"

    def __str__(self):
        return f"{self.rule_name}: {self.amount}"