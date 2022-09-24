from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account
from .forms import RegisterForm

@admin.register(Account)
class AccountAdmin(UserAdmin):
    add_form = RegisterForm
    list_display = ('email', 'username', 'name', 'is_online', 'is_staff', 'last_login')
    search_fields = ('email', 'username')
    readonly_fields = ('id',)

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('email',)}),
    )