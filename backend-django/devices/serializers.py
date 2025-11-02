"""
Serializers for devices app
"""
from rest_framework import serializers
from .models import Device, Zone, DeviceEvent


class ZoneListSerializer(serializers.ModelSerializer):
    device_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Zone
        fields = ['id', 'code', 'name', 'speed_limit', 'is_active', 'device_count']
    
    def get_device_count(self, obj):
        return obj.devices.filter(status='active').count()


class ZoneDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = '__all__'


class DeviceListSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Device
        fields = [
            'id', 'code', 'name', 'device_type', 'status', 'status_display',
            'zone_name', 'location_lat', 'location_lon', 'ip_address',
            'resolution', 'fps', 'is_active'
        ]


class DeviceDetailSerializer(serializers.ModelSerializer):
    zone = ZoneListSerializer(read_only=True)
    device_type_display = serializers.CharField(source='get_device_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Device
        fields = '__all__'


class DeviceEventSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = DeviceEvent
        fields = '__all__'
