from django.contrib import admin
from .models import Category, Product, StockMovement, Supplier, Purchase, PurchaseItem

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(StockMovement)
admin.site.register(Supplier)
admin.site.register(Purchase)
admin.site.register(PurchaseItem)