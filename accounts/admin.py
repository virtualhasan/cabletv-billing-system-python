from django import forms
from django.contrib.auth.models import Group
from accounts.models import AuditTable
from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()




class NewUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser','is_admin','is_collector', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

# Register your models here.
admin.site.register(AuditTable)
admin.site.register(User, NewUserAdmin)