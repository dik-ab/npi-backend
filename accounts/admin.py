from django.contrib import admin

from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "last_login_at", "deleted_at")
    search_fields = ("name", "email")
