"""
URL configuration for infractions app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InfractionViewSet, AppealViewSet, InfractionEventViewSet
from .views_detection import VehicleDetectionViewSet, DetectionStatisticsViewSet

router = DefaultRouter()
router.register(r'', InfractionViewSet, basename='infraction')
router.register(r'appeals', AppealViewSet, basename='appeal')
router.register(r'events', InfractionEventViewSet, basename='infraction-event')
router.register(r'detections', VehicleDetectionViewSet, basename='detection')
router.register(r'detection-stats', DetectionStatisticsViewSet, basename='detection-stats')

urlpatterns = router.urls
