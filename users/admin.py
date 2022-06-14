from django.contrib import admin

from .models import Account


class AccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'name', 'is_online', 'is_staff')
    search_fields = ('email', 'username')
    readonly_fields = ('id', 'password')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Account, AccountAdmin)
