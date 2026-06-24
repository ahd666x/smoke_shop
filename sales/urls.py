from django.urls import path
from . import views

urlpatterns = [
    path('pos/', views.pos_view, name='pos'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('reports/daily/', views.daily_report, name='daily_report'),
    path('reports/low-stock/', views.low_stock_report, name='low_stock_report'),
    path('reports/tax/', views.detailed_tax_report, name='tax_report'),
    path('receipt/<int:order_id>/', views.receipt_view, name='receipt'),
    path('invoice/<int:order_id>/xml/', views.invoice_xml, name='invoice_xml'),
    path('purchases/', views.purchase_list, name='purchase_list'),
    path('purchases/create/', views.purchase_create, name='purchase_create'),
    path('search-products-purchase/', views.search_products_for_purchase, name='search_products_purchase'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('export/', views.export_data, name='export_data'),
    path('import-export/', views.import_data, name='import_export'),

    path('apply-discount/', views.apply_discount, name='apply_discount'),
    path('hold-order/', views.hold_order, name='hold_order'),
    path('held-orders/', views.list_held_orders, name='held_orders'),
    path('resume-held/', views.resume_held_order, name='resume_held'),
    path('search-products/', views.search_products, name='search_products'),
    path('featured-products/', views.get_featured_products, name='featured_products'),

    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart-item/', views.update_cart_item, name='update_cart_item'),
    path('delete-held-order/', views.delete_held_order, name='delete_held_order'),
    path('orders/<int:order_id>/return/', views.return_order, name='return_order'),
    path('orders/<int:order_id>/edit/', views.edit_order, name='edit_order'),
]
