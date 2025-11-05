"""
Models for devices/cameras management
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Zone(models.Model):
    """Traffic zones with speed limits and geographical boundaries"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, help_text="Unique zone code (e.g., ZN001)")
    description = models.TextField(blank=True)
    
    # Geographic data (simplified for local testing - upgrade to PostGIS for production)
    boundary = models.JSONField(help_text="Zone geographical boundary (GeoJSON)", null=True, blank=True)
    center_point_lat = models.DecimalField(max_digits=9, decimal_places=6, help_text="Latitude", null=True, blank=True)
    center_point_lon = models.DecimalField(max_digits=9, decimal_places=6, help_text="Longitude", null=True, blank=True)
    
    # Traffic rules
    speed_limit = models.IntegerField(
        validators=[MinValueValidator(10), MaxValueValidator(200)],
        help_text="Speed limit in km/h"
    )
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Device(models.Model):
    """IoT devices (cameras) for traffic monitoring"""
    
    DEVICE_TYPES = [
        ('camera', 'Traffic Camera'),
        ('sensor', 'Traffic Sensor'),
        ('radar', 'Speed Radar'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, help_text="Device identifier (e.g., CAM001)")
    name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, default='camera')
    
    # Location
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='devices')
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, help_text="Device GPS Latitude", null=True, blank=True)
    location_lon = models.DecimalField(max_digits=9, decimal_places=6, help_text="Device GPS Longitude", null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    
    # Network configuration
    ip_address = models.GenericIPAddressField()
    rtsp_url = models.CharField(
        max_length=255,
        help_text="RTSP stream URL (supports rtsp://user:pass@ip:port/stream format)"
    )
    rtsp_username = models.CharField(max_length=50, blank=True)
    rtsp_password = models.CharField(max_length=100, blank=True)
    
    # Technical specs
    model = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    firmware_version = models.CharField(max_length=50, blank=True)
    resolution = models.CharField(max_length=20, default='1920x1080')
    fps = models.IntegerField(default=30, validators=[MinValueValidator(1), MaxValueValidator(60)])
    
    # Calibration data (JSON field for camera calibration matrix)
    calibration_matrix = models.JSONField(null=True, blank=True, help_text="Camera calibration data")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    last_seen = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['zone']),
            models.Index(fields=['status']),
            models.Index(fields=['device_type']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def is_online(self):
        """Check if device is currently online"""
        from django.utils import timezone
        from datetime import timedelta
        
        if not self.last_seen:
            return False
        
        # Consider device online if last seen within 5 minutes
        return timezone.now() - self.last_seen < timedelta(minutes=5)


class DeviceEvent(models.Model):
    """Events from devices (timestamped data for TimescaleDB)"""
    
    EVENT_TYPES = [
        ('online', 'Device Online'),
        ('offline', 'Device Offline'),
        ('error', 'Device Error'),
        ('maintenance', 'Maintenance Mode'),
        ('calibration', 'Calibration Updated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # TimescaleDB will handle this as a hypertable
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', '-timestamp']),
            models.Index(fields=['event_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.device.code} - {self.event_type} at {self.timestamp}"
