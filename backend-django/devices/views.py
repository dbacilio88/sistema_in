"""
Views for devices app
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from .models import Device, Zone, DeviceEvent
from .serializers import (
    DeviceListSerializer,
    DeviceDetailSerializer,
    ZoneListSerializer,
    ZoneDetailSerializer,
    DeviceEventSerializer
)


class DeviceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Devices/Cameras
    """
    queryset = Device.objects.select_related('zone').order_by('code')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'device_type', 'zone', 'is_active']
    search_fields = ['code', 'name', 'address']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DeviceListSerializer
        return DeviceDetailSerializer
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get device statistics
        """
        qs = self.get_queryset()
        
        total = qs.count()
        by_status = dict(qs.values_list('status').annotate(count=Count('id')))
        by_type = dict(qs.values_list('device_type').annotate(count=Count('id')))
        active = qs.filter(status='active').count()
        
        return Response({
            'total_devices': total,
            'active': active,
            'by_status': by_status,
            'by_type': by_type,
        })


class ZoneViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Traffic Zones
    """
    queryset = Zone.objects.prefetch_related('devices').order_by('code')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['code', 'name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ZoneListSerializer
        return ZoneDetailSerializer


class DeviceEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Device Events (Read-only)
    """
    queryset = DeviceEvent.objects.select_related('device').order_by('-timestamp')
    serializer_class = DeviceEventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['device', 'event_type']
