from django.contrib import admin

from django.contrib import admin
from .models import Vehicle, Driver, VehicleOwnership


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['license_plate', 'make', 'model', 'year', 'vehicle_type', 'owner_name', 'is_stolen', 'is_wanted']
    list_filter = ['vehicle_type', 'is_stolen', 'is_wanted', 'year']
    search_fields = ['license_plate', 'owner_name', 'owner_dni']
    readonly_fields = ['created_at', 'updated_at', 'sunarp_last_updated']
    fieldsets = (
        ('Vehicle Information', {
            'fields': ['license_plate', 'make', 'model', 'year', 'color', 'vehicle_type']
        }),
        ('Owner Information (SUNARP)', {
            'fields': ['owner_name', 'owner_dni', 'owner_address', 'registration_date', 'sunarp_last_updated']
        }),
        ('Status', {
            'fields': ['is_stolen', 'is_wanted', 'notes']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    )


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['document_number', 'full_name', 'license_number', 'license_expiry', 'is_suspended']
    list_filter = ['document_type', 'is_suspended', 'license_class']
    search_fields = ['document_number', 'first_name', 'last_name', 'license_number']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Personal Information', {
            'fields': ['document_type', 'document_number', 'first_name', 'last_name', 'birth_date']
        }),
        ('Contact Information', {
            'fields': ['phone', 'email', 'address']
        }),
        ('License Information', {
            'fields': ['license_number', 'license_class', 'license_expiry']
        }),
        ('Status', {
            'fields': ['is_suspended', 'suspension_reason']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    )


@admin.register(VehicleOwnership)
class VehicleOwnershipAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'driver', 'is_primary_owner', 'ownership_percentage', 'start_date', 'end_date']
    list_filter = ['is_primary_owner', 'start_date', 'end_date']
    search_fields = ['vehicle__license_plate', 'driver__first_name', 'driver__last_name', 'driver__document_number']
    readonly_fields = ['created_at', 'updated_at']
