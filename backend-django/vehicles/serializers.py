"""
Serializers for vehicles app
"""
from rest_framework import serializers
from .models import Vehicle, Driver, VehicleOwnership


class DriverListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = [
            'id', 'document_number', 'first_name', 'last_name', 
            'email', 'phone', 'license_number', 'license_class',
            'is_suspended'
        ]


class DriverDetailSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    license_class_display = serializers.CharField(source='get_license_class_display', read_only=True)
    
    class Meta:
        model = Driver
        fields = '__all__'


class VehicleListSerializer(serializers.ModelSerializer):
    vehicle_type_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'license_plate', 'vehicle_type', 'vehicle_type_display',
            'brand', 'model', 'year', 'color', 'is_stolen', 'is_wanted'
        ]


class VehicleDetailSerializer(serializers.ModelSerializer):
    vehicle_type_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = '__all__'


class VehicleOwnershipSerializer(serializers.ModelSerializer):
    vehicle = VehicleListSerializer(read_only=True)
    driver = DriverListSerializer(read_only=True)
    
    class Meta:
        model = VehicleOwnership
        fields = '__all__'
