# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, OTP_Code


@admin.register(OTP_Code)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'code', 'created_at']
    search_fields = ['phone_number']
    ordering = ['-created_at']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom user admin configuration
    """
    list_display = ['phone_number', 'username', 'email', 'is_active', 'is_admin', 'created_at']
    list_filter = ['is_active', 'is_admin', 'is_superuser', 'created_at']
    search_fields = ['phone_number', 'username', 'email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    

    fieldsets = (
        (None, {'fields': ('phone_number', 'username', 'password')}),
        (_('Personal info'), {'fields': ('email',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_admin', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('created_at', 'updated_at')}),
    )
    
    # Fields for adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'username', 'email', 'password1', 'password2'),
        }),
    )