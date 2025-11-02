"""
URL configuration for authentication app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    LoginView,
    LogoutView,
    RefreshTokenView,
    UserViewSet,
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Authentication endpoints
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='token-refresh'),
    
    # User management endpoints
    path('', include(router.urls)),
]
