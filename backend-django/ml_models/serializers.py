"""
Serializers for ML models
"""
from rest_framework import serializers
from .models import MLModel, MLPrediction


class MLModelSerializer(serializers.ModelSerializer):
    """Serializer for MLModel"""
    
    age_days = serializers.SerializerMethodField()
    accuracy = serializers.SerializerMethodField()
    
    class Meta:
        model = MLModel
        fields = [
            'id',
            'model_name',
            'version',
            'model_type',
            'framework',
            'model_path',
            'metrics',
            'hyperparameters',
            'feature_importance',
            'features_used',
            'is_active',
            'prediction_count',
            'last_prediction_at',
            'avg_prediction_time_ms',
            'deployment_environment',
            'created_at',
            'updated_at',
            'age_days',
            'accuracy'
        ]
        read_only_fields = [
            'id',
            'prediction_count',
            'last_prediction_at',
            'avg_prediction_time_ms',
            'created_at',
            'updated_at'
        ]
    
    def get_age_days(self, obj):
        """Calculate model age in days"""
        from django.utils import timezone
        return (timezone.now() - obj.created_at).days
    
    def get_accuracy(self, obj):
        """Extract accuracy from metrics"""
        if obj.metrics and 'accuracy' in obj.metrics:
            return obj.metrics['accuracy']
        return None


class MLPredictionSerializer(serializers.ModelSerializer):
    """Serializer for MLPrediction"""
    
    model_name = serializers.CharField(source='model.model_name', read_only=True)
    model_version = serializers.CharField(source='model.version', read_only=True)
    driver_dni = serializers.CharField(source='driver.document_number', read_only=True)
    driver_name = serializers.CharField(source='driver.full_name', read_only=True)
    infraction_code = serializers.CharField(source='infraction.id', read_only=True)
    was_correct = serializers.SerializerMethodField()
    
    class Meta:
        model = MLPrediction
        fields = [
            'id',
            'model',
            'model_name',
            'model_version',
            'infraction',
            'infraction_code',
            'driver',
            'driver_dni',
            'driver_name',
            'prediction_type',
            'prediction_value',
            'prediction_class',
            'prediction_confidence',
            'features',
            'actual_value',
            'actual_class',
            'prediction_time_ms',
            'predicted_at',
            'was_correct'
        ]
        read_only_fields = [
            'id',
            'predicted_at'
        ]
    
    def get_was_correct(self, obj):
        """Check if prediction was correct"""
        if obj.actual_class and obj.prediction_class:
            return obj.actual_class == obj.prediction_class
        return None


class RecidivismPredictionRequestSerializer(serializers.Serializer):
    """Request serializer for recidivism prediction"""
    driver_dni = serializers.CharField(max_length=20, required=True)
    infraction_id = serializers.UUIDField(required=False)


class RecidivismPredictionResponseSerializer(serializers.Serializer):
    """Response serializer for recidivism prediction"""
    prediction_id = serializers.UUIDField()
    driver_dni = serializers.CharField()
    driver_name = serializers.CharField()
    recidivism_probability = serializers.FloatField()
    risk_category = serializers.CharField()
    risk_factors = serializers.ListField(child=serializers.DictField())
    model_version = serializers.CharField()
    prediction_time_ms = serializers.FloatField()
    prediction_timestamp = serializers.CharField()
    confidence = serializers.FloatField()


class FeatureExtractionRequestSerializer(serializers.Serializer):
    """Request serializer for feature extraction"""
    driver_dni = serializers.CharField(max_length=20, required=True)


class FeatureExtractionResponseSerializer(serializers.Serializer):
    """Response serializer for feature extraction"""
    driver_dni = serializers.CharField()
    features = serializers.DictField()
    feature_count = serializers.IntegerField()
