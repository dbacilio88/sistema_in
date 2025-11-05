"""
Machine Learning models for predictive analytics
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from infractions.models import Infraction
from vehicles.models import Driver

User = get_user_model()


class MLModel(models.Model):
    """ML Models registry with versioning and metadata"""
    
    MODEL_TYPES = [
        ('classification', 'Classification'),
        ('regression', 'Regression'),
        ('clustering', 'Clustering'),
        ('detection', 'Object Detection'),
    ]
    
    FRAMEWORKS = [
        ('xgboost', 'XGBoost'),
        ('sklearn', 'Scikit-Learn'),
        ('tensorflow', 'TensorFlow'),
        ('pytorch', 'PyTorch'),
        ('lightgbm', 'LightGBM'),
    ]
    
    ENVIRONMENTS = [
        ('development', 'Development'),
        ('staging', 'Staging'),
        ('production', 'Production'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_name = models.CharField(
        max_length=100,
        help_text="Model name (e.g., 'recidivism_xgboost', 'accident_lstm')"
    )
    version = models.CharField(
        max_length=50,
        help_text="Model version (e.g., 'v1.2.3', '2025-11-01')"
    )
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES)
    
    # Framework
    framework = models.CharField(max_length=50, choices=FRAMEWORKS)
    framework_version = models.CharField(max_length=50, blank=True)
    
    # Artifacts
    model_path = models.TextField(
        help_text="Path to model file (e.g., 's3://models/recidivism_v1.2.3.pkl')"
    )
    model_size_mb = models.FloatField(null=True, blank=True)
    
    # MLflow integration
    mlflow_run_id = models.CharField(max_length=100, blank=True)
    mlflow_experiment_id = models.CharField(max_length=100, blank=True)
    mlflow_model_uri = models.TextField(blank=True)
    
    # Performance metrics
    metrics = models.JSONField(
        default=dict,
        help_text="Model metrics (accuracy, precision, recall, f1_score, auc_roc, etc.)"
    )
    
    # Hyperparameters
    hyperparameters = models.JSONField(
        default=dict,
        help_text="Model hyperparameters"
    )
    
    # Dataset
    training_dataset_path = models.TextField(blank=True)
    training_dataset_size = models.IntegerField(null=True, blank=True)
    validation_dataset_path = models.TextField(blank=True)
    test_dataset_path = models.TextField(blank=True)
    
    # Features
    feature_names = models.JSONField(default=list, help_text="List of feature names")
    feature_importance = models.JSONField(
        default=dict,
        help_text="Feature importance scores"
    )
    
    # Deployment
    is_active = models.BooleanField(
        default=False,
        help_text="Is this model currently active/deployed?"
    )
    deployed_at = models.DateTimeField(null=True, blank=True)
    deployed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deployed_ml_models'
    )
    deployment_environment = models.CharField(
        max_length=50,
        choices=ENVIRONMENTS,
        default='development'
    )
    
    # Monitoring
    prediction_count = models.BigIntegerField(default=0)
    avg_prediction_time_ms = models.FloatField(null=True, blank=True)
    last_prediction_at = models.DateTimeField(null=True, blank=True)
    
    # Drift detection
    data_drift_detected = models.BooleanField(default=False)
    concept_drift_detected = models.BooleanField(default=False)
    drift_check_at = models.DateTimeField(null=True, blank=True)
    
    # Description
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_ml_models'
    )
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model_name', 'version']),
            models.Index(fields=['is_active']),
            models.Index(fields=['deployment_environment']),
            models.Index(fields=['-last_prediction_at']),
        ]
        unique_together = [['model_name', 'version']]
    
    def __str__(self):
        status = "ACTIVE" if self.is_active else "INACTIVE"
        return f"{self.model_name} {self.version} ({status})"


class MLPrediction(models.Model):
    """Log of all ML predictions made by the system"""
    
    PREDICTION_TYPES = [
        ('recidivism', 'Recidivism Risk'),
        ('accident_risk', 'Accident Risk'),
        ('severity', 'Infraction Severity'),
        ('driver_risk', 'Driver Risk Score'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    
    # Model reference
    model = models.ForeignKey(
        MLModel,
        on_delete=models.CASCADE,
        related_name='predictions'
    )
    
    # Related entities
    infraction = models.ForeignKey(
        Infraction,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ml_predictions'
    )
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ml_predictions'
    )
    
    # Prediction
    prediction_type = models.CharField(max_length=50, choices=PREDICTION_TYPES)
    prediction_value = models.FloatField(
        help_text="Predicted value (probability for classification, value for regression)"
    )
    prediction_class = models.CharField(
        max_length=50,
        blank=True,
        help_text="Predicted class for classification (e.g., 'high', 'medium', 'low')"
    )
    prediction_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Confidence score 0-1"
    )
    
    # Features used
    features = models.JSONField(
        help_text="Feature values used for this prediction"
    )
    
    # Result (for evaluation)
    actual_value = models.FloatField(
        null=True,
        blank=True,
        help_text="Actual outcome (filled in later for model evaluation)"
    )
    actual_class = models.CharField(max_length=50, blank=True)
    
    # Timing
    prediction_time_ms = models.FloatField(
        null=True,
        blank=True,
        help_text="Time taken to make prediction"
    )
    predicted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-predicted_at']
        indexes = [
            models.Index(fields=['model', '-predicted_at']),
            models.Index(fields=['infraction']),
            models.Index(fields=['driver', '-predicted_at']),
            models.Index(fields=['prediction_type', '-predicted_at']),
        ]
    
    def __str__(self):
        return f"{self.prediction_type}: {self.prediction_value:.3f} at {self.predicted_at}"
