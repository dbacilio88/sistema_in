"""
Views for devices app
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
import threading
import time
from urllib.parse import urlparse

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
    
    @action(detail=True, methods=['get'])
    def stream(self, request, pk=None):
        """
        Stream video from camera
        """
        device = get_object_or_404(Device, pk=pk)
        
        if device.device_type != 'camera':
            return JsonResponse({
                'error': 'Device is not a camera'
            }, status=400)
        
        if not device.rtsp_url:
            return JsonResponse({
                'error': 'Camera RTSP URL not configured'
            }, status=400)
        
        if device.status != 'active':
            return JsonResponse({
                'error': 'Camera is not active'
            }, status=400)
        
        def generate_frames():
            """Generator function to yield video frames"""
            cap = None
            try:
                # Import cv2 only when needed
                import cv2
                
                # Connect to RTSP stream
                cap = cv2.VideoCapture(device.rtsp_url)
                
                if not cap.isOpened():
                    yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + b'Error: Cannot connect to camera\r\n'
                    return
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Encode frame to JPEG
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    frame_bytes = buffer.tobytes()
                    
                    # Yield frame in multipart format
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    
                    time.sleep(0.033)  # ~30 FPS
                    
            except Exception as e:
                yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + f'Error: {str(e)}'.encode() + b'\r\n'
            finally:
                if cap:
                    cap.release()
        
        response = StreamingHttpResponse(
            generate_frames(),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
        response['Cache-Control'] = 'no-cache'
        return response
    
    @action(detail=True, methods=['get'])
    def stream_info(self, request, pk=None):
        """
        Get camera stream information
        """
        device = get_object_or_404(Device, pk=pk)
        
        if device.device_type != 'camera':
            return Response({
                'error': 'Device is not a camera'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'device_code': device.code,
            'device_name': device.name,
            'status': device.status,
            'resolution': device.resolution,
            'fps': device.fps,
            'location': {
                'lat': float(device.location_lat) if device.location_lat else None,
                'lon': float(device.location_lon) if device.location_lon else None,
                'address': device.address
            },
            'zone': {
                'code': device.zone.code if device.zone else None,
                'name': device.zone.name if device.zone else None
            },
            'stream_url': f'/api/devices/{device.id}/stream/',
            'has_rtsp': bool(device.rtsp_url)
        })
    
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
