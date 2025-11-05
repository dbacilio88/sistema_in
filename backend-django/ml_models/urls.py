"""
URL configuration for ml_models app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MLModelViewSet, MLPredictionViewSet

app_name = 'ml_models'

router = DefaultRouter()
router.register(r'models', MLModelViewSet, basename='mlmodel')
router.register(r'predictions', MLPredictionViewSet, basename='mlprediction')

urlpatterns = [
    path('', include(router.urls)),
]
