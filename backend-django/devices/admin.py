from django.contrib import admin
from .models import Zone, Device, DeviceEvent


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'speed_limit', 'is_active', 'created_at']
    list_filter = ['is_active', 'speed_limit']
    search_fields = ['code', 'name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['code']


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'device_type', 'zone', 'status', 'is_online', 'last_seen']
    list_filter = ['device_type', 'status', 'zone', 'is_active']
    search_fields = ['code', 'name', 'ip_address']
    readonly_fields = ['created_at', 'updated_at', 'last_seen']
    fieldsets = (
        ('Información Básica', {
            'fields': ['code', 'name', 'device_type', 'zone']
        }),
        ('Ubicación', {
            'fields': ['location_lat', 'location_lon', 'address']
        }),
        ('Configuración de Red', {
            'fields': ['ip_address', 'rtsp_url', 'rtsp_username', 'rtsp_password']
        }),
        ('Especificaciones Técnicas', {
            'fields': ['model', 'manufacturer', 'firmware_version', 'resolution', 'fps']
        }),
        ('Calibración', {
            'fields': ['calibration_matrix'],
            'classes': ['collapse']
        }),
        ('Estado', {
            'fields': ['status', 'last_seen', 'is_active']
        }),
        ('Metadatos', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    )


@admin.register(DeviceEvent)
class DeviceEventAdmin(admin.ModelAdmin):
    list_display = ['device', 'event_type', 'timestamp', 'message']
    list_filter = ['event_type', 'timestamp', 'device__zone']
    search_fields = ['device__code', 'message']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
