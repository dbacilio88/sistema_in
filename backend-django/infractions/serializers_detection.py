"""
Serializers for vehicle detections
"""
from rest_framework import serializers
from .models_detection import VehicleDetection, DetectionStatistics
from devices.models import Device, Zone


class VehicleDetectionSerializer(serializers.ModelSerializer):
    """Serializer for vehicle detections"""
    
    device_name = serializers.CharField(source='device.name', read_only=True)
    zone_name = serializers.CharField(source='zone.name', read_only=True, allow_null=True)
    bbox_area = serializers.FloatField(read_only=True)
    
    class Meta:
        model = VehicleDetection
        fields = [
            'id',
            'vehicle_type',
            'confidence',
            'device',
            'device_name',
            'zone',
            'zone_name',
            'vehicle',
            'license_plate_detected',
            'license_plate_confidence',
            'bbox_x1',
            'bbox_y1',
            'bbox_x2',
            'bbox_y2',
            'bbox_area',
            'estimated_speed',
            'has_infraction',
            'infraction',
            'metadata',
            'source',
            'detected_at',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'bbox_area']


class VehicleDetectionCreateSerializer(serializers.Serializer):
    """Serializer for creating detections from inference service"""
    
    vehicle_type = serializers.ChoiceField(
        choices=['car', 'truck', 'bus', 'motorcycle', 'bicycle', 'person', 'other']
    )
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    bbox = serializers.ListField(
        child=serializers.FloatField(),
        min_length=4,
        max_length=4,
        help_text="Bounding box [x1, y1, x2, y2]"
    )
    license_plate = serializers.CharField(required=False, allow_blank=True)
    license_plate_confidence = serializers.FloatField(required=False, default=0.0)
    speed = serializers.FloatField(required=False, allow_null=True)
    has_infraction = serializers.BooleanField(default=False)
    metadata = serializers.JSONField(required=False, default=dict)


class BulkDetectionCreateSerializer(serializers.Serializer):
    """Serializer for bulk creation of detections"""
    
    detections = VehicleDetectionCreateSerializer(many=True)
    device_id = serializers.UUIDField(required=False, allow_null=True)
    source = serializers.CharField(default='webcam_local')
    zone_id = serializers.UUIDField(required=False, allow_null=True)


class DetectionStatisticsSerializer(serializers.ModelSerializer):
    """Serializer for detection statistics"""
    
    device_name = serializers.CharField(source='device.name', read_only=True, allow_null=True)
    zone_name = serializers.CharField(source='zone.name', read_only=True, allow_null=True)
    
    class Meta:
        model = DetectionStatistics
        fields = [
            'id',
            'period_type',
            'period_start',
            'period_end',
            'device',
            'device_name',
            'zone',
            'zone_name',
            'car_count',
            'truck_count',
            'bus_count',
            'motorcycle_count',
            'bicycle_count',
            'person_count',
            'other_count',
            'total_detections',
            'total_with_plate',
            'total_infractions',
            'avg_confidence',
            'avg_speed',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DetectionSummarySerializer(serializers.Serializer):
    """Serializer for detection summary/analytics"""
    
    total_detections = serializers.IntegerField()
    by_vehicle_type = serializers.DictField()
    by_hour = serializers.DictField()
    avg_confidence = serializers.FloatField()
    with_license_plate = serializers.IntegerField()
    with_infractions = serializers.IntegerField()
