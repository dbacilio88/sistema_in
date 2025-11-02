"""
URL configuration for infractions app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InfractionViewSet, AppealViewSet, InfractionEventViewSet

router = DefaultRouter()
router.register(r'', InfractionViewSet, basename='infraction')
router.register(r'appeals', AppealViewSet, basename='appeal')
router.register(r'events', InfractionEventViewSet, basename='infraction-event')

urlpatterns = router.urls
