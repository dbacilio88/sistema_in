"""
Views for notifications app
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Notification
from .serializers import NotificationSerializer, NotificationCreateSerializer

logger = logging.getLogger(__name__)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['notification_type', 'is_read']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Return notifications for the current user only
        """
        queryset = Notification.objects.filter(user=self.request.user)
        
        # Filter by unread_only parameter
        unread_only = self.request.query_params.get('unread_only', None)
        if unread_only and unread_only.lower() == 'true':
            queryset = queryset.filter(is_read=False)
        
        return queryset
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer
    
    @extend_schema(
        tags=['Notifications'],
        summary='Mark notification as read',
        description='Mark a specific notification as read',
        responses={200: NotificationSerializer}
    )
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Mark notification as read
        """
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        
        return Response({
            'success': True,
            'message': 'Notificación marcada como leída',
            'data': serializer.data
        })
    
    @extend_schema(
        tags=['Notifications'],
        summary='Mark all notifications as read',
        description='Mark all user notifications as read',
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        Mark all notifications as read
        """
        updated = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        
        return Response({
            'success': True,
            'message': f'{updated} notificaciones marcadas como leídas',
            'data': {'updated_count': updated}
        })
    
    @extend_schema(
        tags=['Notifications'],
        summary='Get unread count',
        description='Get count of unread notifications for current user',
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Get count of unread notifications
        """
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return Response({
            'success': True,
            'data': {'unread_count': count}
        })
