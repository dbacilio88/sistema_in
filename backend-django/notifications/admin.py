"""
Admin configuration for notifications app
"""
from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for Notification model
    """
    list_display = [
        'title',
        'user',
        'notification_type',
        'is_read',
        'created_at',
    ]
    list_filter = [
        'notification_type',
        'is_read',
        'created_at',
    ]
    search_fields = [
        'title',
        'message',
        'user__username',
        'user__email',
    ]
    readonly_fields = ['created_at', 'read_at']
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'title', 'message', 'notification_type')
        }),
        ('Estado', {
            'fields': ('is_read', 'link')
        }),
        ('Fechas', {
            'fields': ('created_at', 'read_at')
        }),
    )
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
