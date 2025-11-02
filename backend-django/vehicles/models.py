"""
Models for vehicle management and driver information
"""
import uuid
from django.db import models
from django.core.validators import RegexValidator


class Vehicle(models.Model):
    """Vehicle information"""
    
    VEHICLE_TYPES = [
        ('car', 'Automobile'),
        ('truck', 'Truck'),
        ('bus', 'Bus'),
        ('motorcycle', 'Motorcycle'),
        ('bicycle', 'Bicycle'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # License plate with Peru format validation
    license_plate = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{3}-\d{3,4}$|^[A-Z]{2}-\d{4}$|^[A-Z]\d{2}-\d{3}$',
                message='Invalid license plate format. Use AAA-123, AB-1234, or A12-345 format.'
            )
        ],
        help_text="License plate in Peru format (e.g., ABC-123, AB-1234)"
    )
    
    # Vehicle details
    make = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=50, blank=True)
    year = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=30, blank=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, default='car')
    
    # SUNARP data (will be populated via API)
    owner_name = models.CharField(max_length=200, blank=True)
    owner_dni = models.CharField(max_length=20, blank=True)
    owner_address = models.TextField(blank=True)
    registration_date = models.DateField(null=True, blank=True)
    
    # Status
    is_stolen = models.BooleanField(default=False)
    is_wanted = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    # Metadata
    sunarp_last_updated = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['license_plate']
        indexes = [
            models.Index(fields=['license_plate']),
            models.Index(fields=['owner_dni']),
            models.Index(fields=['is_stolen']),
            models.Index(fields=['is_wanted']),
        ]
    
    def __str__(self):
        return self.license_plate


class Driver(models.Model):
    """Driver/person information"""
    
    DOCUMENT_TYPES = [
        ('dni', 'DNI'),
        ('passport', 'Passport'),
        ('foreign_card', 'Foreign Card'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Personal information
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='dni')
    document_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    
    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    # License information
    license_number = models.CharField(max_length=20, blank=True)
    license_class = models.CharField(max_length=10, blank=True)
    license_expiry = models.DateField(null=True, blank=True)
    
    # Status
    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['document_number']),
            models.Index(fields=['license_number']),
            models.Index(fields=['is_suspended']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.document_number})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class VehicleOwnership(models.Model):
    """Relationship between vehicles and drivers/owners"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='ownerships')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='vehicles')
    
    # Ownership details
    is_primary_owner = models.BooleanField(default=True)
    ownership_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['vehicle']),
            models.Index(fields=['driver']),
            models.Index(fields=['is_primary_owner']),
        ]
    
    def __str__(self):
        return f"{self.driver.full_name} owns {self.vehicle.license_plate}"
