from django.contrib import admin
from .models import Category, Product, ProductImage, ShippingFee
# Register your models here.

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ShippingFee)