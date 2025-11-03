"""
Models for vehicle detections (all detections, not just infractions)
"""
import uuid
from django.db import models
from devices.models import Device, Zone
from vehicles.models import Vehicle


class VehicleDetection(models.Model):
    """
    Store all vehicle detections, regardless of infractions
    This helps with analytics, traffic flow analysis, and ML model improvement
    """
    
    VEHICLE_TYPES = [
        ('car', 'Car'),
        ('truck', 'Truck'),
        ('bus', 'Bus'),
        ('motorcycle', 'Motorcycle'),
        ('bicycle', 'Bicycle'),
        ('person', 'Person'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Detection info
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    confidence = models.FloatField(help_text="Detection confidence score 0-1")
    
    # Location
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='detections')
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='detections', null=True, blank=True)
    
    # Vehicle info (if identified)
    vehicle = models.ForeignKey(
        Vehicle, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='detections'
    )
    license_plate_detected = models.CharField(max_length=10, blank=True)
    license_plate_confidence = models.FloatField(default=0.0, help_text="OCR confidence score 0-1")
    
    # Bounding box (normalized coordinates 0-1)
    bbox_x1 = models.FloatField(help_text="Top-left X coordinate (normalized)")
    bbox_y1 = models.FloatField(help_text="Top-left Y coordinate (normalized)")
    bbox_x2 = models.FloatField(help_text="Bottom-right X coordinate (normalized)")
    bbox_y2 = models.FloatField(help_text="Bottom-right Y coordinate (normalized)")
    
    # Speed data (if available)
    estimated_speed = models.FloatField(null=True, blank=True, help_text="Speed in km/h")
    
    # Metadata
    has_infraction = models.BooleanField(default=False, help_text="Whether this detection has an associated infraction")
    infraction = models.ForeignKey(
        'Infraction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_detection'
    )
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional detection data")
    
    # Source
    source = models.CharField(max_length=50, default='camera', help_text="Detection source (camera, webcam_local, etc)")
    
    # Timestamps
    detected_at = models.DateTimeField(db_index=True, help_text="When the detection occurred")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['device', '-detected_at']),
            models.Index(fields=['vehicle_type', '-detected_at']),
            models.Index(fields=['has_infraction']),
            models.Index(fields=['source', '-detected_at']),
            models.Index(fields=['license_plate_detected']),
        ]
        verbose_name = 'Vehicle Detection'
        verbose_name_plural = 'Vehicle Detections'
    
    def __str__(self):
        return f"{self.vehicle_type} - {self.detected_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
    @property
    def bbox_area(self):
        """Calculate normalized bounding box area"""
        width = abs(self.bbox_x2 - self.bbox_x1)
        height = abs(self.bbox_y2 - self.bbox_y1)
        return width * height


class DetectionStatistics(models.Model):
    """
    Aggregated statistics for detections by type and time period
    Updated periodically by Celery task
    """
    
    PERIOD_CHOICES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Period info
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    period_start = models.DateTimeField(db_index=True)
    period_end = models.DateTimeField()
    
    # Location
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='detection_stats', null=True, blank=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='detection_stats', null=True, blank=True)
    
    # Counts by vehicle type
    car_count = models.IntegerField(default=0)
    truck_count = models.IntegerField(default=0)
    bus_count = models.IntegerField(default=0)
    motorcycle_count = models.IntegerField(default=0)
    bicycle_count = models.IntegerField(default=0)
    person_count = models.IntegerField(default=0)
    other_count = models.IntegerField(default=0)
    
    # Total counts
    total_detections = models.IntegerField(default=0)
    total_with_plate = models.IntegerField(default=0, help_text="Detections with license plate identified")
    total_infractions = models.IntegerField(default=0)
    
    # Averages
    avg_confidence = models.FloatField(default=0.0)
    avg_speed = models.FloatField(null=True, blank=True, help_text="Average speed in km/h")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-period_start']
        unique_together = [['period_type', 'period_start', 'device', 'zone']]
        indexes = [
            models.Index(fields=['period_type', '-period_start']),
            models.Index(fields=['device', '-period_start']),
            models.Index(fields=['zone', '-period_start']),
        ]
        verbose_name = 'Detection Statistics'
        verbose_name_plural = 'Detection Statistics'
    
    def __str__(self):
        device_name = self.device.name if self.device else "All Devices"
        return f"{self.period_type} - {device_name} - {self.period_start.strftime('%Y-%m-%d %H:%M')}"
