"""
Views for vehicles app
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from .models import Vehicle, Driver, VehicleOwnership
from .serializers import (
    VehicleListSerializer,
    VehicleDetailSerializer,
    DriverListSerializer,
    DriverDetailSerializer,
    VehicleOwnershipSerializer
)


class VehicleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Vehicles
    """
    queryset = Vehicle.objects.all().order_by('license_plate')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['vehicle_type', 'is_stolen', 'is_wanted']
    search_fields = ['license_plate', 'brand', 'model', 'owner_dni']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VehicleListSerializer
        return VehicleDetailSerializer
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get vehicle statistics
        """
        qs = self.get_queryset()
        
        total = qs.count()
        by_type = dict(qs.values_list('vehicle_type').annotate(count=Count('id')))
        stolen = qs.filter(is_stolen=True).count()
        wanted = qs.filter(is_wanted=True).count()
        
        return Response({
            'total_vehicles': total,
            'by_type': by_type,
            'stolen': stolen,
            'wanted': wanted,
        })


class DriverViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Drivers
    """
    queryset = Driver.objects.all().order_by('last_name', 'first_name')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_suspended', 'license_class']
    search_fields = ['document_number', 'first_name', 'last_name', 'license_number']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DriverListSerializer
        return DriverDetailSerializer
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get driver statistics
        """
        qs = self.get_queryset()
        
        total = qs.count()
        suspended = qs.filter(is_suspended=True).count()
        by_license = dict(qs.values_list('license_class').annotate(count=Count('id')))
        
        return Response({
            'total_drivers': total,
            'suspended': suspended,
            'by_license_class': by_license,
        })


class VehicleOwnershipViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Vehicle Ownership (Read-only)
    """
    queryset = VehicleOwnership.objects.select_related('vehicle', 'driver').order_by('-start_date')
    serializer_class = VehicleOwnershipSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['vehicle', 'driver', 'is_primary_owner']
