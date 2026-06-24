# management/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Q, Sum, F
from django import forms
from decimal import Decimal

from inventory.models import Category, Product, StockMovement, Supplier, Purchase, PurchaseItem
from taxation.models import TaxRule, ProductTaxProfile, TaxLine
from sales.models import Order, Payment, OrderItem

import jdatetime
from django.utils import timezone
from datetime import datetime, date
# ==================== کلاس‌های پایه ====================

class BaseManagementView(LoginRequiredMixin):
    login_url = '/accounts/login/'


# class BaseListView(BaseManagementView, ListView):
#     paginate_by = 20
#     template_name = 'management/generic_list.html'
#     search_fields = []
#     ordering = ['id']

#     def get_update_url_pattern(self):
#         app_label = self.model._meta.app_label
#         model_name = self.model._meta.model_name
#         return f'management:{model_name}_update'

#     def get_delete_url_pattern(self):
#         app_label = self.model._meta.app_label
#         model_name = self.model._meta.model_name
#         return f'management:{model_name}_delete'

#     def get_detail_url_pattern(self):
#         """بازگرداندن نام الگوی URL جزئیات (در صورت وجود). پیش‌فرض None."""
#         return None

#     def get_queryset(self):
#         qs = super().get_queryset()
#         search = self.request.GET.get('q', '')
#         if search and self.search_fields:
#             query = Q()
#             for field in self.search_fields:
#                 query |= Q(**{f"{field}__icontains": search})
#             qs = qs.filter(query)
#         return qs

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['search'] = self.request.GET.get('q', '')
#         context['model_verbose_name'] = self.model._meta.verbose_name

#         columns = self.get_list_columns()
#         context['list_columns'] = columns
#         context['create_url'] = self.get_create_url()
#         context['update_url_pattern'] = self.get_update_url_pattern()
#         context['delete_url_pattern'] = self.get_delete_url_pattern()
#         context['detail_url_pattern'] = self.get_detail_url_pattern()

#         # ساخت ردیف‌ها با فرمت اعداد و تاریخ
#         rows = []
#         for obj in context['object_list']:
#             row_values = []
#             for col_name, col_label in columns:
#                 value = getattr(obj, col_name, '')
#                 if isinstance(value, (int, float, Decimal)):
#                     value = f'{value:,.0f}'
#                 elif hasattr(value, 'strftime'):
#                     if hasattr(value, 'hour'):
#                         value = value.strftime('%Y/%m/%d %H:%M')
#                     else:
#                         value = value.strftime('%Y/%m/%d')
#                 row_values.append(value)
#             # برای OrderListView می‌توانیم detail_url شخصی را هم اضافه کنیم،
#             # ولی در کلاس فرزند می‌توان آن را override کرد.
#             row_data = {
#                 'object': obj,
#                 'values': row_values
#             }
#             rows.append(row_data)
#         context['table_rows'] = rows
#         return context

#     def get_list_columns(self):
#         raise NotImplementedError("ستون‌ها را مشخص کنید")

#     def get_create_url(self):
#         return None


class BaseListView(BaseManagementView, ListView):
    paginate_by = 20
    template_name = 'management/generic_list.html'
    search_fields = []
    ordering = ['id']

    def get_update_url_pattern(self):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        return f'management:{model_name}_update'

    def get_delete_url_pattern(self):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        return f'management:{model_name}_delete'

    def get_detail_url_pattern(self):
        return None

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('q', '')
        if search and self.search_fields:
            query = Q()
            for field in self.search_fields:
                query |= Q(**{f"{field}__icontains": search})
            qs = qs.filter(query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('q', '')
        context['model_verbose_name'] = self.model._meta.verbose_name

        columns = self.get_list_columns()
        context['list_columns'] = columns
        context['create_url'] = self.get_create_url()
        context['update_url_pattern'] = self.get_update_url_pattern()
        context['delete_url_pattern'] = self.get_delete_url_pattern()
        context['detail_url_pattern'] = self.get_detail_url_pattern()

        rows = []
        for obj in context['object_list']:
            row_values = []
            for col_name, col_label in columns:
                value = getattr(obj, col_name, '')
                if isinstance(value, datetime):
                    local_val = timezone.localtime(value)
                    j_date = jdatetime.datetime.fromgregorian(datetime=local_val)
                    value = j_date.strftime('%Y/%m/%d %H:%M')
                elif isinstance(value, date):
                    j_date = jdatetime.date.fromgregorian(date=value)
                    value = j_date.strftime('%Y/%m/%d')
                elif isinstance(value, (int, float, Decimal)):
                    value = f'{value:,.0f}'
                row_values.append(value)
            rows.append({'object': obj, 'values': row_values})
        context['table_rows'] = rows
        return context

    def get_list_columns(self):
        raise NotImplementedError("ستون‌ها را مشخص کنید")

    def get_create_url(self):
        return None




















class BaseCreateView(BaseManagementView, CreateView):
    template_name = 'management/generic_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_verbose_name'] = self.model._meta.verbose_name
        context['is_update'] = False
        return context


class BaseUpdateView(BaseManagementView, UpdateView):
    template_name = 'management/generic_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_verbose_name'] = self.model._meta.verbose_name
        context['is_update'] = True
        return context


class BaseDeleteView(BaseManagementView, DeleteView):
    template_name = 'management/delete_confirm.html'

    def get_success_url(self):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        return reverse_lazy(f'management:{model_name}_list')


# ==================== ویوهای مدل‌ها ====================

# ----- Category -----
class CategoryListView(BaseListView):
    model = Category
    search_fields = ['name']
    def get_list_columns(self): return [('name', 'نام'), ('parent', 'والد')]
    def get_create_url(self): return reverse_lazy('management:category_create')

class CategoryCreateView(BaseCreateView):
    model = Category
    fields = ['name', 'parent']
    success_url = reverse_lazy('management:category_list')

class CategoryUpdateView(BaseUpdateView):
    model = Category
    fields = ['name', 'parent']
    success_url = reverse_lazy('management:category_list')

class CategoryDeleteView(BaseDeleteView):
    model = Category
    success_url = reverse_lazy('management:category_list')

# ----- Product -----
class ProductListView(BaseListView):
    model = Product
    search_fields = ['name', 'barcode']
    def get_list_columns(self): return [('name', 'نام'), ('barcode', 'بارکد'), ('selling_price', 'قیمت فروش'), ('stock_quantity', 'موجودی')]
    def get_create_url(self): return reverse_lazy('management:product_create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for row in context['table_rows']:
            row['purchase_history_url'] = reverse_lazy(
                'management:product_purchase_history', args=[row['object'].pk]
            )
        return context

class ProductCreateView(BaseCreateView):
    model = Product
    fields = ['name', 'barcode', 'category', 'unit', 'purchase_price', 'selling_price', 'stock_quantity', 'is_active']
    success_url = reverse_lazy('management:product_list')

    def form_valid(self, form):
        product = form.save(commit=False)
        if product.stock_quantity > 0 and product.purchase_price > 0:
            product.inventory_cost = product.stock_quantity * product.purchase_price
        else:
            product.inventory_cost = 0
        product.save()
        return super().form_valid(form)

# class ProductUpdateView(BaseUpdateView):
#     model = Product
#     fields = ['name', 'barcode', 'category', 'unit', 'purchase_price', 'selling_price', 'stock_quantity', 'is_active']
#     success_url = reverse_lazy('management:product_list')

class ProductUpdateView(BaseUpdateView):
    model = Product
    fields = ['name', 'barcode', 'category', 'unit', 'purchase_price', 'selling_price', 'stock_quantity', 'is_active']
    success_url = reverse_lazy('management:product_list')

    def form_valid(self, form):
        product = form.save(commit=False)
        # دریافت شیء قبلی از دیتابیس برای محاسبه تغییرات
        old_product = Product.objects.get(pk=product.pk)
        old_qty = old_product.stock_quantity
        new_qty = product.stock_quantity

        if old_qty > 0:
            # میانگین موزون قبل از تغییر
            avg_cost = old_product.inventory_cost / old_qty
            # تغییر موجودی = new_qty - old_qty
            delta_qty = new_qty - old_qty
            # ارزش جدید = ارزش قبلی + (تغییر تعداد × میانگین قبلی)
            product.inventory_cost = old_product.inventory_cost + (delta_qty * avg_cost)
        else:
            # اگر موجودی قبلاً صفر بوده، هر تغییری با قیمت خرید فعلی حساب شود
            if new_qty > 0 and product.purchase_price > 0:
                product.inventory_cost = new_qty * product.purchase_price
            else:
                product.inventory_cost = 0

        product.save()
        return super().form_valid(form)










class ProductDeleteView(BaseDeleteView):
    model = Product
    success_url = reverse_lazy('management:product_list')

# ----- Supplier -----
class SupplierListView(BaseListView):
    model = Supplier
    search_fields = ['name', 'phone']
    def get_list_columns(self): return [('name', 'نام'), ('phone', 'تلفن')]
    def get_create_url(self): return reverse_lazy('management:supplier_create')

class SupplierCreateView(BaseCreateView):
    model = Supplier
    fields = ['name', 'phone', 'address']
    success_url = reverse_lazy('management:supplier_list')

class SupplierUpdateView(BaseUpdateView):
    model = Supplier
    fields = ['name', 'phone', 'address']
    success_url = reverse_lazy('management:supplier_list')

class SupplierDeleteView(BaseDeleteView):
    model = Supplier
    success_url = reverse_lazy('management:supplier_list')

# ----- StockMovement (فقط لیست) -----
class StockMovementListView(BaseListView):
    model = StockMovement
    def get_list_columns(self): return [('product', 'کالا'), ('quantity', 'تعداد'), ('movement_type', 'نوع'), ('created_at', 'تاریخ')]
    def get_update_url_pattern(self): return None
    def get_delete_url_pattern(self): return None

class PurchaseListView(BaseListView):
    model = Purchase
    def get_list_columns(self): return [('supplier', 'تأمین‌کننده'), ('total_amount', 'مبلغ'), ('created_at', 'تاریخ')]
    def get_update_url_pattern(self): return None
    def get_delete_url_pattern(self): return None
    def get_detail_url_pattern(self): return 'management:purchase_detail'   # فعال کردن دکمه جزئیات
    def get_create_url(self): return reverse_lazy('purchase_create')        # دکمه ثبت خرید جدید

# ----- TaxRule -----
class TaxRuleListView(BaseListView):
    model = TaxRule
    search_fields = ['name']
    def get_list_columns(self): return [('name', 'نام'), ('calculation_type', 'نوع'), ('value', 'مقدار'), ('order', 'ترتیب')]
    def get_create_url(self): return reverse_lazy('management:taxrule_create')

class TaxRuleCreateView(BaseCreateView):
    model = TaxRule
    fields = '__all__'
    success_url = reverse_lazy('management:taxrule_list')

class TaxRuleUpdateView(BaseUpdateView):
    model = TaxRule
    fields = '__all__'
    success_url = reverse_lazy('management:taxrule_list')

class TaxRuleDeleteView(BaseDeleteView):
    model = TaxRule
    success_url = reverse_lazy('management:taxrule_list')

# ----- ProductTaxProfile -----
class ProductTaxProfileListView(BaseListView):
    model = ProductTaxProfile
    def get_list_columns(self): return [('product', 'محصول')]
    def get_create_url(self): return reverse_lazy('management:producttaxprofile_create')

class ProductTaxProfileCreateView(BaseCreateView):
    model = ProductTaxProfile
    fields = ['product', 'tax_rules']
    success_url = reverse_lazy('management:producttaxprofile_list')

class ProductTaxProfileUpdateView(BaseUpdateView):
    model = ProductTaxProfile
    fields = ['product', 'tax_rules']
    success_url = reverse_lazy('management:producttaxprofile_list')

class ProductTaxProfileDeleteView(BaseDeleteView):
    model = ProductTaxProfile
    success_url = reverse_lazy('management:producttaxprofile_list')

# ----- Order -----
class OrderListView(BaseListView):
    model = Order
    ordering = ['-created_at']
    def get_list_columns(self): return [('id', 'شماره'), ('created_at', 'تاریخ'), ('grand_total', 'مبلغ'), ('is_paid', 'وضعیت')]
    def get_update_url_pattern(self): return None
    def get_delete_url_pattern(self): return None
    def get_detail_url_pattern(self): return 'management:order_detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for row in context['table_rows']:
            # اضافه کردن URL مستقیم (برای لینک کردن ستون شماره نیز مفید است)
            row['detail_url'] = reverse_lazy('management:order_detail', args=[row['object'].pk])
        return context

class OrderDetailView(BaseManagementView, DetailView):
    model = Order
    template_name = 'management/order_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.object.items.all()
        for item in items:
            item.row_total = item.unit_price * item.quantity + item.tax_amount
        context['items'] = items
        context['payments'] = self.object.payment_set.all()
        return context

# ----- Payment -----
class PaymentListView(BaseListView):
    model = Payment
    ordering = ['-paid_at']
    def get_list_columns(self): return [('order', 'سفارش'), ('amount', 'مبلغ'), ('method', 'روش'), ('paid_at', 'تاریخ')]
    def get_update_url_pattern(self): return None
    def get_delete_url_pattern(self): return None







class PurchaseDetailView(BaseManagementView, DetailView):
    model = Purchase
    template_name = 'management/purchase_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.object.items.all()
        for item in items:
            item.row_total = item.unit_price * item.quantity
        context['items'] = items
        return context


class ProductPurchaseHistoryView(BaseManagementView, DetailView):
    model = Product
    template_name = 'management/product_purchase_history.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        purchases = PurchaseItem.objects.filter(
            product=self.object
        ).select_related('purchase__supplier').order_by('-purchase__created_at')
        for item in purchases:
            item.row_total = item.quantity * item.unit_price

        context['purchases'] = purchases
        context['sales'] = OrderItem.objects.filter(
            product=self.object
        ).select_related('order').order_by('-order__created_at')[:50]

        context['current_stock'] = self.object.stock_quantity
        if self.object.stock_quantity > 0:
            context['current_avg'] = self.object.inventory_cost / self.object.stock_quantity
        else:
            context['current_avg'] = Decimal('0')
        context['current_value'] = self.object.inventory_cost
        return context


class PurchaseItemUpdateView(BaseManagementView, UpdateView):
    model = PurchaseItem
    template_name = 'management/purchase_item_form.html'
    fields = ['quantity', 'unit_price']

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.old_quantity = self.object.quantity
        self.old_price = self.object.unit_price
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        purchase_item = form.save(commit=False)
        new_quantity = purchase_item.quantity
        new_price = purchase_item.unit_price
        product = purchase_item.product

        product.inventory_cost -= self.old_quantity * self.old_price
        StockMovement.objects.create(
            product=product,
            quantity=self.old_quantity,
            movement_type='out',
            reference=f"Edit PurchaseItem #{purchase_item.pk}",
        )

        product.inventory_cost += new_quantity * new_price
        product.save()
        StockMovement.objects.create(
            product=product,
            quantity=new_quantity,
            movement_type='in',
            reference=f"Edit PurchaseItem #{purchase_item.pk}",
        )

        purchase_item.save()

        purchase = purchase_item.purchase
        total = purchase.items.aggregate(
            total=Sum(F('quantity') * F('unit_price'))
        )['total'] or Decimal('0')
        purchase.total_amount = total
        purchase.save()

        messages.success(self.request, 'قلم خرید با موفقیت ویرایش شد.')
        return redirect('management:product_purchase_history', pk=product.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for field in context['form'].fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        return context


class PurchaseItemDeleteView(BaseManagementView, DeleteView):
    model = PurchaseItem
    template_name = 'management/purchase_item_confirm_delete.html'

    def form_valid(self, form):
        purchase_item = self.get_object()
        product = purchase_item.product
        purchase = purchase_item.purchase

        product.inventory_cost -= purchase_item.quantity * purchase_item.unit_price
        product.save()
        StockMovement.objects.create(
            product=product,
            quantity=purchase_item.quantity,
            movement_type='out',
            reference=f"Delete PurchaseItem #{purchase_item.pk}",
        )

        purchase_item.delete()

        total = purchase.items.aggregate(
            total=Sum(F('quantity') * F('unit_price'))
        )['total'] or Decimal('0')
        purchase.total_amount = total
        purchase.save()

        messages.success(self.request, 'قلم خرید با موفقیت حذف شد.')
        return redirect('management:product_purchase_history', pk=product.pk)