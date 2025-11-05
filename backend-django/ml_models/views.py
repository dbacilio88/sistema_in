"""
API views for ML predictions
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import MLModel, MLPrediction
from .services import RecidivismPredictionService, FeatureEngineeringService
from .serializers import MLModelSerializer, MLPredictionSerializer
from infractions.models import Infraction
from vehicles.models import Driver


class MLModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ML Models
    
    list: Get all ML models
    retrieve: Get specific ML model
    """
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get currently active models"""
        active_models = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_models, many=True)
        return Response(serializer.data)


class MLPredictionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ML Predictions
    
    list: Get all predictions
    retrieve: Get specific prediction
    create: Make a new prediction
    """
    queryset = MLPrediction.objects.all()
    serializer_class = MLPredictionSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def recidivism(self, request):
        """
        Predict recidivism risk for a driver
        
        POST /api/ml/predictions/recidivism/
        {
            "driver_dni": "12345678",
            "infraction_id": "uuid" (optional)
        }
        """
        driver_dni = request.data.get('driver_dni')
        infraction_id = request.data.get('infraction_id')
        
        if not driver_dni:
            return Response(
                {'error': 'driver_dni is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if driver exists
        try:
            driver = Driver.objects.get(document_number=driver_dni)
        except Driver.DoesNotExist:
            return Response(
                {'error': f'Driver with DNI {driver_dni} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Make prediction
        start_time = timezone.now()
        prediction_result = RecidivismPredictionService.predict_recidivism_risk(driver_dni)
        end_time = timezone.now()
        prediction_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Get or create placeholder model (heuristic)
        model, _ = MLModel.objects.get_or_create(
            model_name='recidivism_heuristic',
            version='v1.0.0',
            defaults={
                'model_type': 'classification',
                'framework': 'sklearn',
                'model_path': 'heuristic://recidivism_v1.0.0',
                'metrics': {
                    'accuracy': 0.75,
                    'note': 'Heuristic model - placeholder for XGBoost'
                },
                'is_active': True,
                'deployment_environment': 'development'
            }
        )
        
        # Get infraction if provided
        infraction = None
        if infraction_id:
            try:
                infraction = Infraction.objects.get(id=infraction_id)
            except Infraction.DoesNotExist:
                pass
        
        # Save prediction
        ml_prediction = MLPrediction.objects.create(
            model=model,
            infraction=infraction,
            driver=driver,
            prediction_type='recidivism',
            prediction_value=prediction_result['recidivism_probability'],
            prediction_class=prediction_result['risk_category'],
            prediction_confidence=prediction_result['confidence'],
            features=prediction_result['features'],
            prediction_time_ms=prediction_time_ms
        )
        
        # Update infraction with prediction
        if infraction:
            infraction.recidivism_risk = prediction_result['recidivism_probability']
            infraction.risk_factors = {
                'factors': prediction_result['risk_factors']
            }
            infraction.ml_prediction_time_ms = prediction_time_ms
            infraction.save(update_fields=['recidivism_risk', 'risk_factors', 'ml_prediction_time_ms'])
        
        # Update driver risk score (weighted average of recent predictions)
        recent_predictions = MLPrediction.objects.filter(
            driver=driver,
            prediction_type='recidivism',
            predicted_at__gte=timezone.now() - timezone.timedelta(days=90)
        ).order_by('-predicted_at')[:10]
        
        if recent_predictions:
            # Weight more recent predictions higher
            weights = [0.9 ** i for i in range(len(recent_predictions))]
            weighted_scores = [
                pred.prediction_value * weight
                for pred, weight in zip(recent_predictions, weights)
            ]
            driver.risk_score = sum(weighted_scores) / sum(weights)
            
            # Update category
            if driver.risk_score < 0.25:
                driver.risk_category = 'low'
            elif driver.risk_score < 0.50:
                driver.risk_category = 'medium'
            elif driver.risk_score < 0.75:
                driver.risk_category = 'high'
            else:
                driver.risk_category = 'critical'
            
            driver.risk_updated_at = timezone.now()
            driver.save(update_fields=['risk_score', 'risk_category', 'risk_updated_at'])
        
        # Update model stats
        model.prediction_count += 1
        model.last_prediction_at = timezone.now()
        if model.avg_prediction_time_ms:
            # Running average
            model.avg_prediction_time_ms = (
                model.avg_prediction_time_ms * 0.9 + prediction_time_ms * 0.1
            )
        else:
            model.avg_prediction_time_ms = prediction_time_ms
        model.save(update_fields=['prediction_count', 'last_prediction_at', 'avg_prediction_time_ms'])
        
        # Return response
        return Response({
            'prediction_id': ml_prediction.id,
            'driver_dni': driver_dni,
            'driver_name': driver.full_name,
            'recidivism_probability': prediction_result['recidivism_probability'],
            'risk_category': prediction_result['risk_category'],
            'risk_factors': prediction_result['risk_factors'],
            'model_version': prediction_result['model_version'],
            'prediction_time_ms': prediction_time_ms,
            'prediction_timestamp': prediction_result['prediction_timestamp'],
            'confidence': prediction_result['confidence']
        })
    
    @action(detail=False, methods=['post'])
    def features(self, request):
        """
        Extract features for a driver without making prediction
        
        POST /api/ml/predictions/features/
        {
            "driver_dni": "12345678"
        }
        """
        driver_dni = request.data.get('driver_dni')
        
        if not driver_dni:
            return Response(
                {'error': 'driver_dni is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract features
        features = FeatureEngineeringService.extract_features(driver_dni)
        
        return Response({
            'driver_dni': driver_dni,
            'features': features,
            'feature_count': len(features)
        })
