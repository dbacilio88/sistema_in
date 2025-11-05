"""
Models for traffic infractions and violations
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from devices.models import Device, Zone
from vehicles.models import Vehicle, Driver

User = get_user_model()


class Infraction(models.Model):
    """Traffic infractions detected by the system"""
    
    INFRACTION_TYPES = [
        ('speed', 'Speed Violation'),
        ('red_light', 'Red Light Violation'),
        ('wrong_lane', 'Wrong Lane Usage'),
        ('no_helmet', 'No Helmet'),
        ('parking', 'Illegal Parking'),
        ('phone_use', 'Phone Use While Driving'),
        ('seatbelt', 'No Seatbelt'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('validated', 'Validated'),
        ('rejected', 'Rejected'),
        ('appealed', 'Under Appeal'),
        ('paid', 'Fine Paid'),
        ('dismissed', 'Dismissed'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Infraction details
    infraction_code = models.CharField(max_length=20, unique=True, editable=False)
    infraction_type = models.CharField(max_length=20, choices=INFRACTION_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='medium')
    
    # Location and device
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='infractions')
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='infractions')
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, help_text="Infraction GPS Latitude", null=True, blank=True)
    location_lon = models.DecimalField(max_digits=9, decimal_places=6, help_text="Infraction GPS Longitude", null=True, blank=True)
    
    # Vehicle and driver (if identified)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='infractions')
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='infractions')
    
    # Detection data
    license_plate_detected = models.CharField(max_length=10, blank=True)
    license_plate_confidence = models.FloatField(default=0.0, help_text="OCR confidence score 0-1")
    
    # Speed-specific data
    detected_speed = models.FloatField(null=True, blank=True, help_text="Speed in km/h")
    speed_limit = models.IntegerField(null=True, blank=True, help_text="Speed limit at location")
    
    # Evidence
    snapshot_url = models.URLField(blank=True, help_text="URL to snapshot image")
    video_url = models.URLField(blank=True, help_text="URL to video evidence")
    evidence_metadata = models.JSONField(default=dict, blank=True, help_text="Additional evidence data")
    
    # Review and status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_infractions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    # Fine information
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fine_due_date = models.DateField(null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # ML Predictions
    recidivism_risk = models.FloatField(
        null=True,
        blank=True,
        help_text="Predicted recidivism probability (0-1)"
    )
    accident_risk = models.FloatField(
        null=True,
        blank=True,
        help_text="Predicted accident risk (0-1)"
    )
    risk_factors = models.JSONField(
        default=dict,
        blank=True,
        help_text="Top risk factors with importance scores"
    )
    
    # Performance Metrics
    processing_time_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Time taken to process and recognize the infraction (in seconds)"
    )
    ml_prediction_time_ms = models.FloatField(
        null=True,
        blank=True,
        help_text="Time taken for ML prediction (in milliseconds)"
    )
    
    # Timestamps
    detected_at = models.DateTimeField(db_index=True, help_text="When the infraction was detected")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['infraction_code']),
            models.Index(fields=['device', '-detected_at']),
            models.Index(fields=['zone', '-detected_at']),
            models.Index(fields=['infraction_type', '-detected_at']),
            models.Index(fields=['status']),
            models.Index(fields=['license_plate_detected']),
            models.Index(fields=['vehicle']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.infraction_code:
            # Generate unique infraction code
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT nextval('infraction_code_seq')")
                seq_value = cursor.fetchone()[0]
                self.infraction_code = f"INF{seq_value:06d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.infraction_code} - {self.get_infraction_type_display()}"
    
    @property
    def is_speed_violation(self):
        return self.infraction_type == 'speed'
    
    @property
    def speed_excess(self):
        if self.is_speed_violation and self.detected_speed and self.speed_limit:
            return max(0, self.detected_speed - self.speed_limit)
        return 0


class InfractionEvent(models.Model):
    """Events in the lifecycle of an infraction (TimescaleDB hypertable)"""
    
    EVENT_TYPES = [
        ('detected', 'Infraction Detected'),
        ('reviewed', 'Manual Review'),
        ('validated', 'Validated'),
        ('rejected', 'Rejected'),
        ('appealed', 'Appeal Filed'),
        ('payment_received', 'Payment Received'),
        ('dismissed', 'Dismissed'),
        ('notice_sent', 'Notice Sent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    infraction = models.ForeignKey(Infraction, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    
    # Event details
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # TimescaleDB will handle this as a hypertable
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['infraction', '-timestamp']),
            models.Index(fields=['event_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.infraction.infraction_code} - {self.get_event_type_display()}"


class Appeal(models.Model):
    """Appeals filed against infractions"""
    
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    infraction = models.OneToOneField(Infraction, on_delete=models.CASCADE, related_name='appeal')
    
    # Appeal details
    reason = models.TextField(help_text="Reason for appeal")
    evidence_description = models.TextField(blank=True)
    supporting_documents = models.JSONField(default=list, blank=True, help_text="List of document URLs")
    
    # Appellant information
    appellant_name = models.CharField(max_length=200)
    appellant_dni = models.CharField(max_length=20)
    appellant_phone = models.CharField(max_length=20, blank=True)
    appellant_email = models.EmailField(blank=True)
    
    # Review
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    review_decision = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['infraction']),
            models.Index(fields=['status']),
            models.Index(fields=['appellant_dni']),
        ]
    
    def __str__(self):
        return f"Appeal for {self.infraction.infraction_code}"


# Import detection models
from .models_detection import VehicleDetection, DetectionStatistics
