"""
Serializers for infractions app
"""
from rest_framework import serializers
from .models import Infraction, Appeal, InfractionEvent
from devices.models import Device, Zone
from vehicles.models import Vehicle, Driver


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['id', 'code', 'name', 'speed_limit']


class DeviceSerializer(serializers.ModelSerializer):
    zone = ZoneSerializer(read_only=True)
    
    class Meta:
        model = Device
        fields = ['id', 'code', 'name', 'device_type', 'status', 'zone', 'location_lat', 'location_lon']


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'license_plate', 'vehicle_type', 'brand', 'model', 'year', 'color']


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['id', 'document_number', 'first_name', 'last_name', 'phone', 'email']


class InfractionListSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    infraction_type_display = serializers.CharField(source='get_infraction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = Infraction
        fields = [
            'id', 'infraction_code', 'infraction_type', 'infraction_type_display',
            'severity', 'severity_display', 'status', 'status_display',
            'device_name', 'zone_name', 'license_plate_detected',
            'detected_speed', 'speed_limit', 'fine_amount',
            'recidivism_risk', 'processing_time_seconds', 'ml_prediction_time_ms',
            'detected_at', 'created_at'
        ]


class InfractionDetailSerializer(serializers.ModelSerializer):
    device = DeviceSerializer(read_only=True)
    zone = ZoneSerializer(read_only=True)
    vehicle = VehicleSerializer(read_only=True)
    driver = DriverSerializer(read_only=True)
    infraction_type_display = serializers.CharField(source='get_infraction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = Infraction
        fields = '__all__'


class InfractionEventSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True, allow_null=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = InfractionEvent
        fields = ['id', 'event_type', 'event_type_display', 'notes', 'timestamp', 'user_name']


class AppealSerializer(serializers.ModelSerializer):
    infraction = InfractionListSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Appeal
        fields = '__all__'


class InfractionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating infractions from inference service
    Accepts flexible input and handles defaults
    """
    vehicle = serializers.UUIDField(required=False, allow_null=True)
    device = serializers.UUIDField(required=False, allow_null=True)
    zone = serializers.UUIDField(required=False, allow_null=True)
    
    class Meta:
        model = Infraction
        fields = [
            'infraction_type', 'severity', 'vehicle', 'device', 'zone',
            'license_plate_detected', 'license_plate_confidence',
            'detected_speed', 'speed_limit', 'location_lat', 'location_lon',
            'snapshot_url', 'video_url', 'evidence_metadata',
            'status', 'detected_at',
            'processing_time_seconds', 'ml_prediction_time_ms', 'recidivism_risk'
        ]
        extra_kwargs = {
            'device': {'required': False},
            'zone': {'required': False},
            'detected_at': {'required': True},
        }
    
    def validate(self, attrs):
        """Validate and set defaults for device and zone if not provided"""
        # CRITICAL: Don't set device/zone here - they are handled by to_internal_value
        # Just validate that we have them or will get defaults in create()
        return attrs
    
    def create(self, validated_data):
        """Create infraction with auto-generated code"""
        # Generate unique infraction code (max 20 chars)
        from datetime import datetime
        import random
        # Use shorter timestamp: HHMMSS + random 2 digits
        timestamp = datetime.now().strftime('%H%M%S')
        random_suffix = random.randint(10, 99)
        infraction_type_code = validated_data['infraction_type'][:3].upper()
        # Format: INF-SPE-142530-45 = 17 chars (within 20 limit)
        validated_data['infraction_code'] = f"INF-{infraction_type_code}-{timestamp}-{random_suffix}"
        
        # CRITICAL: Set default device and zone if not provided
        if 'device' not in validated_data or validated_data['device'] is None:
            default_device = Device.objects.filter(is_active=True).first()
            if default_device:
                validated_data['device'] = default_device
        
        if 'zone' not in validated_data or validated_data['zone'] is None:
            if validated_data.get('device'):
                # Use device's zone
                validated_data['zone'] = validated_data['device'].zone
            else:
                # Fallback to default zone
                default_zone = Zone.objects.filter(is_active=True).first()
                if default_zone:
                    validated_data['zone'] = default_zone
        
        return super().create(validated_data)
