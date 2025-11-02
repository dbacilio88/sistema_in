"""
URL configuration for vehicles app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet, DriverViewSet, VehicleOwnershipViewSet

router = DefaultRouter()
router.register(r'', VehicleViewSet, basename='vehicle')
router.register(r'drivers', DriverViewSet, basename='driver')
router.register(r'ownerships', VehicleOwnershipViewSet, basename='vehicle-ownership')

urlpatterns = router.urls
