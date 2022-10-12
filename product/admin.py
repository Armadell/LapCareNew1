

from django.contrib import admin
from . models import Products,Variation,Banner
# Register your models here.
#slug prepopulate and display
#modelAdmin is a class which tells how models are displayed on the admin
#interface
class ProductsAdmin(admin.ModelAdmin):
     list_display=('product_name','slug','price','stock','category','newbrand','modified_date','available')
     prepopulated_fields={'slug':('product_name',)}
class VariationAdmin(admin.ModelAdmin):
     list_display=('product','variation_category','variation_value','is_active','created_date')
     list_editable=('is_active',)
     list_filter=('product','variation_category','variation_value')
admin.site.register(Products,ProductsAdmin)
admin.site.register(Variation,VariationAdmin)
admin.site.register(Banner)