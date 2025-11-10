"""
URL configuration for Traffic Infraction Detection System.
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import redirect
from django.http import JsonResponse


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for service monitoring
    """
    return Response({
        'status': 'healthy',
        'service': 'django-admin',
        'version': '1.0.0'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API root endpoint showing available endpoints and database stats
    """
    from devices.models import Zone, Device
    from vehicles.models import Vehicle
    from infractions.models import Infraction
    from django.contrib.auth import get_user_model
    
    User = get_user_model()  # Obtener el modelo de usuario personalizado
    
    return Response({
        'message': 'Traffic Infraction Detection System API',
        'version': '1.0.0',
        'database_stats': {
            'users': User.objects.count(),
            'zones': Zone.objects.count(),
            'devices': Device.objects.count(),
            'vehicles': Vehicle.objects.count(),
            'infractions': Infraction.objects.count(),
        },
        'endpoints': {
            'admin': '/admin/',
            'api_docs': '/api/docs/',
            'devices': '/api/devices/',
            'zones': '/api/devices/zones/',
            'infractions': '/api/infractions/',
            'vehicles': '/api/vehicles/',
            'notifications': '/api/notifications/',
            'auth': '/api/auth/',
            'ml_models': '/api/ml/models/',
            'ml_predictions': '/api/ml/predictions/',
            'ml_predict_recidivism': '/api/ml/predictions/recidivism/',
            'ml_extract_features': '/api/ml/predictions/features/',
        }
    })


def root_view(request):
    """Redirect root to API overview"""
    return redirect('/api/')


urlpatterns = [
    # Root
    path('', root_view, name='root'),
    
    # API Root
    path('api/', api_root, name='api-root'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health-check'),
    path('api/health/', health_check, name='api-health-check'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API endpoints
    path('api/auth/', include('authentication.urls')),
    path('api/devices/', include('devices.urls')),
    path('api/infractions/', include('infractions.urls')),
    path('api/vehicles/', include('vehicles.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/ml/', include('ml_models.urls')),
]

# Serve static and media files - always in AWS environment
if settings.DEBUG or not settings.DEBUG:  # Always serve static files in our deployment
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin site customization
admin.site.site_header = 'Sistema de Detección de Infracciones de Tráfico'
admin.site.site_title = 'Admin Traffic AI'
admin.site.index_title = 'Administración del Sistema'
admin.site.site_url = 'http://localhost:3002'  # Link to frontend dashboard
