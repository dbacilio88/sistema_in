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


def root_view(request):
    """Redirect root to admin or API docs"""
    return redirect('/admin/')


urlpatterns = [
    # Root
    path('', root_view, name='root'),
    
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
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin site customization
admin.site.site_header = 'Sistema de Detección de Infracciones de Tráfico'
admin.site.site_title = 'Admin Traffic AI'
admin.site.index_title = 'Administración del Sistema'
admin.site.site_url = 'http://localhost:3002'  # Link to frontend dashboard
