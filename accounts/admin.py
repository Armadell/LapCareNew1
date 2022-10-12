

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from accounts.views import register
from .models import Account,UserProfile


# Register your models here.

class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self,object):
        return format_html('<img src="{}" width="30" style="border_radius:50%;">)'.format(object.profile_picture.url))
   
    list_display=('thumbnail','user','city','state','country')


admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile,UserProfileAdmin)