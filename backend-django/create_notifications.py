"""
Script to create sample notifications for testing
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from authentication.models import User
from notifications.models import Notification

def create_sample_notifications():
    """Create sample notifications for all users"""
    
    # Get admin user
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("Admin user not found. Please create it first.")
        return
    
    # Sample notifications
    notifications_data = [
        {
            'title': 'Nueva infracción detectada',
            'message': 'Se detectó una infracción de exceso de velocidad en Zona Centro',
            'notification_type': 'infraction',
            'link': '/infractions',
        },
        {
            'title': 'Dispositivo desconectado',
            'message': 'La cámara CAM-001 no responde. Verificar conexión.',
            'notification_type': 'device',
            'link': '/devices',
        },
        {
            'title': 'Sistema actualizado',
            'message': 'El sistema se actualizó correctamente a la versión 1.0.1',
            'notification_type': 'success',
        },
        {
            'title': 'Alerta de mantenimiento',
            'message': 'Mantenimiento programado para mañana a las 02:00 AM',
            'notification_type': 'warning',
        },
        {
            'title': 'Informe mensual disponible',
            'message': 'El informe mensual de infracciones está listo para revisión',
            'notification_type': 'info',
            'link': '/reports',
        },
    ]
    
    # Create notifications
    created = 0
    for notif_data in notifications_data:
        notification = Notification.objects.create(
            user=admin_user,
            **notif_data
        )
        created += 1
        print(f"✓ Creada notificación: {notification.title}")
    
    print(f"\n✓ {created} notificaciones creadas exitosamente")

if __name__ == '__main__':
    create_sample_notifications()
