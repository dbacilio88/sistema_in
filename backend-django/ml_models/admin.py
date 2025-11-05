"""
Admin interface for ML Models
"""
from django.contrib import admin
from .models import MLModel, MLPrediction


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = [
        'model_name',
        'version',
        'model_type',
        'framework',
        'is_active',
        'deployment_environment',
        'prediction_count',
        'created_at'
    ]
    list_filter = [
        'model_type',
        'framework',
        'is_active',
        'deployment_environment',
        'data_drift_detected',
        'concept_drift_detected'
    ]
    search_fields = ['model_name', 'version', 'description']
    readonly_fields = [
        'id',
        'prediction_count',
        'last_prediction_at',
        'created_at',
        'updated_at'
    ]
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'model_name', 'version', 'model_type', 'description')
        }),
        ('Framework', {
            'fields': ('framework', 'framework_version')
        }),
        ('Artifacts', {
            'fields': ('model_path', 'model_size_mb')
        }),
        ('MLflow', {
            'fields': ('mlflow_run_id', 'mlflow_experiment_id', 'mlflow_model_uri'),
            'classes': ('collapse',)
        }),
        ('Performance', {
            'fields': ('metrics', 'hyperparameters', 'feature_names', 'feature_importance')
        }),
        ('Dataset', {
            'fields': (
                'training_dataset_path',
                'training_dataset_size',
                'validation_dataset_path',
                'test_dataset_path'
            ),
            'classes': ('collapse',)
        }),
        ('Deployment', {
            'fields': (
                'is_active',
                'deployment_environment',
                'deployed_at',
                'deployed_by'
            )
        }),
        ('Monitoring', {
            'fields': (
                'prediction_count',
                'avg_prediction_time_ms',
                'last_prediction_at',
                'data_drift_detected',
                'concept_drift_detected',
                'drift_check_at'
            )
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'notes', 'metadata'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MLPrediction)
class MLPredictionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'prediction_type',
        'prediction_value',
        'prediction_class',
        'model',
        'driver',
        'predicted_at'
    ]
    list_filter = [
        'prediction_type',
        'prediction_class',
        'model__model_name',
        'predicted_at'
    ]
    search_fields = [
        'driver__full_name',
        'infraction__infraction_code'
    ]
    readonly_fields = [
        'predicted_at',
        'prediction_time_ms'
    ]
    date_hierarchy = 'predicted_at'
    
    fieldsets = (
        ('Prediction', {
            'fields': (
                'model',
                'prediction_type',
                'prediction_value',
                'prediction_class',
                'prediction_confidence',
                'prediction_time_ms',
                'predicted_at'
            )
        }),
        ('Related Entities', {
            'fields': ('infraction', 'driver')
        }),
        ('Features', {
            'fields': ('features',),
            'classes': ('collapse',)
        }),
        ('Evaluation', {
            'fields': ('actual_value', 'actual_class'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
