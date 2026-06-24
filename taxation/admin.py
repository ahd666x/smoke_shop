from django.contrib import admin
from .models import TaxRule, ProductTaxProfile, TaxLine

admin.site.register(TaxRule)
admin.site.register(ProductTaxProfile)
admin.site.register(TaxLine)