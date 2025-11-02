"""
Views for infractions app
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta

from .models import Infraction, Appeal, InfractionEvent
from .serializers import (
    InfractionListSerializer,
    InfractionDetailSerializer,
    InfractionCreateSerializer,
    AppealSerializer,
    InfractionEventSerializer
)


class InfractionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Infractions
    """
    queryset = Infraction.objects.select_related(
        'device', 'zone', 'vehicle', 'driver', 'reviewed_by'
    ).order_by('-detected_at')
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'infraction_type', 'severity', 'device', 'zone']
    search_fields = ['infraction_code', 'license_plate_detected']
    ordering_fields = ['detected_at', 'created_at', 'fine_amount']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InfractionListSerializer
        elif self.action == 'create':
            return InfractionCreateSerializer
        return InfractionDetailSerializer
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get infraction statistics
        """
        # Time ranges
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        # Base queryset
        qs = self.get_queryset()
        
        # Total counts
        total_infractions = qs.count()
        today_infractions = qs.filter(detected_at__gte=today_start).count()
        week_infractions = qs.filter(detected_at__gte=week_start).count()
        month_infractions = qs.filter(detected_at__gte=month_start).count()
        
        # By status
        by_status = dict(qs.values_list('status').annotate(count=Count('id')))
        
        # By type
        by_type = dict(qs.values_list('infraction_type').annotate(count=Count('id')))
        
        # By severity
        by_severity = dict(qs.values_list('severity').annotate(count=Count('id')))
        
        # Pending review
        pending_review = qs.filter(status='pending').count()
        
        return Response({
            'total_infractions': total_infractions,
            'today': today_infractions,
            'this_week': week_infractions,
            'this_month': month_infractions,
            'by_status': by_status,
            'by_type': by_type,
            'by_severity': by_severity,
            'pending_review': pending_review,
        })
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent infractions (last 24 hours)
        """
        last_24h = timezone.now() - timedelta(hours=24)
        recent = self.get_queryset().filter(detected_at__gte=last_24h)[:20]
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)


class AppealViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Appeals
    """
    queryset = Appeal.objects.select_related('infraction', 'reviewed_by').order_by('-submitted_at')
    serializer_class = AppealSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['submitted_at', 'updated_at']


class InfractionEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Infraction Events (Read-only)
    """
    queryset = InfractionEvent.objects.select_related('infraction', 'user').order_by('-timestamp')
    serializer_class = InfractionEventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['infraction', 'event_type']

