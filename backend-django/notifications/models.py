"""
Models for notifications app
"""
from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    Model representing user notifications
    """
    NOTIFICATION_TYPES = [
        ('info', 'Información'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('success', 'Éxito'),
        ('infraction', 'Infracción'),
        ('device', 'Dispositivo'),
        ('system', 'Sistema'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Usuario'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    message = models.TextField(
        verbose_name='Mensaje'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='info',
        verbose_name='Tipo de Notificación'
    )
    link = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Enlace'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Leída'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    read_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Lectura'
    )
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            from django.utils import timezone
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
