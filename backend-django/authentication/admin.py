"""
Admin configuration for authentication app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User, LoginHistory, UserRole


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for User model
    """
    list_display = [
        'email', 'username', 'full_name_display', 'role_badge',
        'is_active_badge', 'last_login', 'date_joined'
    ]
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'dni']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'username', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'dni', 'phone', 'profile_image')
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Security', {
            'fields': (
                'failed_login_attempts',
                'account_locked_until',
                'password_changed_at',
                'must_change_password'
            )
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        ('Authentication', {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
        ('Personal Information', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'role'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login', 'updated_at', 'password_changed_at']
    
    def full_name_display(self, obj):
        """Display full name"""
        return obj.get_full_name()
    full_name_display.short_description = 'Full Name'
    
    def role_badge(self, obj):
        """Display role with color badge"""
        colors = {
            UserRole.ADMIN: '#dc3545',
            UserRole.SUPERVISOR: '#fd7e14',
            UserRole.OPERATOR: '#0dcaf0',
            UserRole.AUDITOR: '#6c757d',
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = 'Role'
    
    def is_active_badge(self, obj):
        """Display active status with badge"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #198754; color: white; padding: 3px 10px; border-radius: 3px;">Active</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 3px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for LoginHistory model
    """
    list_display = [
        'user', 'login_at', 'logout_at', 'ip_address',
        'success_badge', 'failure_reason'
    ]
    list_filter = ['success', 'login_at']
    search_fields = ['user__email', 'user__username', 'ip_address']
    ordering = ['-login_at']
    readonly_fields = ['user', 'login_at', 'logout_at', 'ip_address', 'user_agent', 'success', 'failure_reason']
    
    def has_add_permission(self, request):
        """Disable adding login history manually"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable changing login history"""
        return False
    
    def success_badge(self, obj):
        """Display success status with badge"""
        if obj.success:
            return format_html(
                '<span style="background-color: #198754; color: white; padding: 3px 10px; border-radius: 3px;">Success</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Failed</span>'
        )
    success_badge.short_description = 'Status'
