"""
Views for vehicle detections
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
import logging

from .models_detection import VehicleDetection, DetectionStatistics
from .serializers_detection import (
    VehicleDetectionSerializer,
    VehicleDetectionCreateSerializer,
    BulkDetectionCreateSerializer,
    DetectionStatisticsSerializer,
    DetectionSummarySerializer
)
from devices.models import Device, Zone
from vehicles.models import Vehicle

logger = logging.getLogger(__name__)


class VehicleDetectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Vehicle Detections
    """
    queryset = VehicleDetection.objects.select_related(
        'device', 'zone', 'vehicle', 'infraction'
    ).order_by('-detected_at')
    
    serializer_class = VehicleDetectionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['vehicle_type', 'has_infraction', 'device', 'zone', 'source']
    search_fields = ['license_plate_detected']
    ordering_fields = ['detected_at', 'confidence', 'estimated_speed']
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def bulk_create(self, request):
        """
        Create multiple detections in bulk (called by inference service)
        
        Expected payload:
        {
            "detections": [
                {
                    "vehicle_type": "car",
                    "confidence": 0.95,
                    "bbox": [0.1, 0.2, 0.3, 0.4],
                    "license_plate": "ABC-123",
                    "license_plate_confidence": 0.85,
                    "speed": 65.5,
                    "has_infraction": false,
                    "metadata": {}
                }
            ],
            "device_id": "uuid-optional",
            "zone_id": "uuid-optional",
            "source": "webcam_local"
        }
        """
        try:
            serializer = BulkDetectionCreateSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(
                    {'error': 'Invalid data', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            validated_data = serializer.validated_data
            detections_data = validated_data['detections']
            device_id = validated_data.get('device_id')
            zone_id = validated_data.get('zone_id')
            source = validated_data.get('source', 'webcam_local')
            
            # Get or create device
            if device_id:
                try:
                    device = Device.objects.get(id=device_id)
                except Device.DoesNotExist:
                    device = None
            else:
                device = None
            
            if not device:
                device, _ = Device.objects.get_or_create(
                    name=f"Device-{source}",
                    defaults={
                        "device_type": "webcam" if source == "webcam_local" else "camera",
                        "status": "active",
                        "ip_address": "127.0.0.1",
                        "is_active": True
                    }
                )
            
            # Get zone if provided
            zone = None
            if zone_id:
                try:
                    zone = Zone.objects.get(id=zone_id)
                except Zone.DoesNotExist:
                    pass
            
            # Create detections
            created_detections = []
            
            for det_data in detections_data:
                bbox = det_data['bbox']
                
                # Get or create vehicle if license plate present
                vehicle = None
                if det_data.get('license_plate'):
                    vehicle, _ = Vehicle.objects.get_or_create(
                        license_plate=det_data['license_plate'],
                        defaults={
                            'vehicle_type': det_data['vehicle_type'],
                            'make': 'Unknown',
                            'model': 'Unknown'
                        }
                    )
                
                # Create detection
                detection = VehicleDetection.objects.create(
                    vehicle_type=det_data['vehicle_type'],
                    confidence=det_data['confidence'],
                    device=device,
                    zone=zone,
                    vehicle=vehicle,
                    license_plate_detected=det_data.get('license_plate', ''),
                    license_plate_confidence=det_data.get('license_plate_confidence', 0.0),
                    bbox_x1=bbox[0],
                    bbox_y1=bbox[1],
                    bbox_x2=bbox[2],
                    bbox_y2=bbox[3],
                    estimated_speed=det_data.get('speed'),
                    has_infraction=det_data.get('has_infraction', False),
                    metadata=det_data.get('metadata', {}),
                    source=source,
                    detected_at=timezone.now()
                )
                
                created_detections.append(detection)
            
            logger.info(
                f"Created {len(created_detections)} detections from source: {source}"
            )
            
            # Serialize response
            response_serializer = VehicleDetectionSerializer(created_detections, many=True)
            
            return Response({
                'status': 'success',
                'created_count': len(created_detections),
                'detections': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating detections: {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get detection summary/analytics
        """
        # Time filter
        hours = int(request.query_params.get('hours', 24))
        start_time = timezone.now() - timedelta(hours=hours)
        
        queryset = self.get_queryset().filter(detected_at__gte=start_time)
        
        # Aggregate data
        total = queryset.count()
        
        by_vehicle_type = dict(
            queryset.values('vehicle_type')
            .annotate(count=Count('id'))
            .values_list('vehicle_type', 'count')
        )
        
        by_hour = {}
        for i in range(hours):
            hour_start = timezone.now() - timedelta(hours=i+1)
            hour_end = timezone.now() - timedelta(hours=i)
            count = queryset.filter(
                detected_at__gte=hour_start,
                detected_at__lt=hour_end
            ).count()
            by_hour[f"{i}h_ago"] = count
        
        avg_confidence = queryset.aggregate(avg=Avg('confidence'))['avg'] or 0.0
        with_plate = queryset.exclude(license_plate_detected='').count()
        with_infractions = queryset.filter(has_infraction=True).count()
        
        summary_data = {
            'total_detections': total,
            'by_vehicle_type': by_vehicle_type,
            'by_hour': by_hour,
            'avg_confidence': round(avg_confidence, 2),
            'with_license_plate': with_plate,
            'with_infractions': with_infractions
        }
        
        serializer = DetectionSummarySerializer(summary_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent detections (last N results)
        """
        limit = int(request.query_params.get('limit', 50))
        recent = self.get_queryset()[:limit]
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        Get detection counts grouped by vehicle type
        """
        hours = int(request.query_params.get('hours', 24))
        start_time = timezone.now() - timedelta(hours=hours)
        
        counts = (
            self.get_queryset()
            .filter(detected_at__gte=start_time)
            .values('vehicle_type')
            .annotate(
                total=Count('id'),
                with_plate=Count('id', filter=Q(license_plate_detected__isnull=False)),
                with_infraction=Count('id', filter=Q(has_infraction=True)),
                avg_confidence=Avg('confidence')
            )
            .order_by('-total')
        )
        
        return Response(list(counts))


class DetectionStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Detection Statistics (Read-only)
    """
    queryset = DetectionStatistics.objects.select_related('device', 'zone').order_by('-period_start')
    serializer_class = DetectionStatisticsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['period_type', 'device', 'zone']
