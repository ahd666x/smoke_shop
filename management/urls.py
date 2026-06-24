from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    # Category
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Product
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('products/<int:pk>/purchases/', views.ProductPurchaseHistoryView.as_view(), name='product_purchase_history'),

    # Supplier
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/create/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/update/', views.SupplierUpdateView.as_view(), name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),

    # StockMovement (فقط نمایش)
    path('stock-movements/', views.StockMovementListView.as_view(), name='stockmovement_list'),

    # Purchase
    path('purchases/', views.PurchaseListView.as_view(), name='purchase_list'),
    path('purchases/<int:pk>/', views.PurchaseDetailView.as_view(), name='purchase_detail'),

    path('purchase-items/<int:pk>/update/', views.PurchaseItemUpdateView.as_view(), name='purchase_item_update'),
    path('purchase-items/<int:pk>/delete/', views.PurchaseItemDeleteView.as_view(), name='purchase_item_delete'),

    # TaxRule
    path('taxrules/', views.TaxRuleListView.as_view(), name='taxrule_list'),
    path('taxrules/create/', views.TaxRuleCreateView.as_view(), name='taxrule_create'),
    path('taxrules/<int:pk>/update/', views.TaxRuleUpdateView.as_view(), name='taxrule_update'),
    path('taxrules/<int:pk>/delete/', views.TaxRuleDeleteView.as_view(), name='taxrule_delete'),

    # ProductTaxProfile
    path('tax-profiles/', views.ProductTaxProfileListView.as_view(), name='producttaxprofile_list'),
    path('tax-profiles/create/', views.ProductTaxProfileCreateView.as_view(), name='producttaxprofile_create'),
    path('tax-profiles/<int:pk>/update/', views.ProductTaxProfileUpdateView.as_view(), name='producttaxprofile_update'),
    path('tax-profiles/<int:pk>/delete/', views.ProductTaxProfileDeleteView.as_view(), name='producttaxprofile_delete'),

    # Order
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),

    # Payment
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
]


