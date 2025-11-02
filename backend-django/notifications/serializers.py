"""
Serializers for notifications app
"""
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model
    """
    notification_type_display = serializers.CharField(
        source='get_notification_type_display',
        read_only=True
    )
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'title',
            'message',
            'notification_type',
            'notification_type_display',
            'link',
            'is_read',
            'created_at',
            'read_at',
        ]
        read_only_fields = ['id', 'created_at', 'read_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating notifications
    """
    class Meta:
        model = Notification
        fields = [
            'user',
            'title',
            'message',
            'notification_type',
            'link',
        ]
