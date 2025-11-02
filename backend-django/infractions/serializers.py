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
            'status', 'detected_at'
        ]
        extra_kwargs = {
            'device': {'required': False},
            'zone': {'required': False},
            'detected_at': {'required': True},
        }
    
    def validate(self, attrs):
        """Validate and set defaults for device and zone if not provided"""
        # If no device provided, try to get a default one
        if not attrs.get('device'):
            default_device = Device.objects.filter(is_active=True).first()
            if default_device:
                attrs['device'] = default_device.id
        
        # If no zone provided, try to get from device or use default
        if not attrs.get('zone'):
            if attrs.get('device'):
                device = Device.objects.get(id=attrs['device'])
                attrs['zone'] = device.zone.id
            else:
                default_zone = Zone.objects.filter(is_active=True).first()
                if default_zone:
                    attrs['zone'] = default_zone.id
        
        return attrs
    
    def create(self, validated_data):
        """Create infraction with auto-generated code"""
        # Generate unique infraction code
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        infraction_type_code = validated_data['infraction_type'][:3].upper()
        validated_data['infraction_code'] = f"INF-{infraction_type_code}-{timestamp}"
        
        return super().create(validated_data)
