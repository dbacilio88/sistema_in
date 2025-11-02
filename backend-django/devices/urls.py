"""
URL configuration for devices app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceViewSet, ZoneViewSet, DeviceEventViewSet

router = DefaultRouter()
router.register(r'', DeviceViewSet, basename='device')
router.register(r'zones', ZoneViewSet, basename='zone')
router.register(r'events', DeviceEventViewSet, basename='device-event')

urlpatterns = router.urls
