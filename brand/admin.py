from django.contrib import admin
from .models import brand
class brandAdmin(admin.ModelAdmin):
    list_display=('brand_name','slug','brand_image')
    prepopulated_fields={'slug':('brand_name',)}
admin.site.register(brand,brandAdmin)