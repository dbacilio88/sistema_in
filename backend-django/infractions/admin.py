from django.contrib import admin
from django.utils.html import format_html
from .models import Infraction, InfractionEvent, Appeal
from .models_detection import VehicleDetection, DetectionStatistics


@admin.register(Infraction)
class InfractionAdmin(admin.ModelAdmin):
    list_display = [
        'infraction_code', 'infraction_type', 'license_plate_detected', 
        'detected_speed', 'speed_limit', 'device', 'status', 
        'processing_time_display', 'ml_prediction_time_display', 
        'recidivism_risk_display', 'detected_at'
    ]
    list_filter = [
        'infraction_type', 'status', 'severity', 'device__zone', 
        'device', 'detected_at'
    ]
    search_fields = [
        'infraction_code', 'license_plate_detected', 
        'vehicle__license_plate', 'driver__document_number'
    ]
    readonly_fields = [
        'infraction_code', 'created_at', 'updated_at', 
        'evidence_preview', 'speed_excess_display'
    ]
    date_hierarchy = 'detected_at'
    ordering = ['-detected_at']
    
    fieldsets = (
        ('Detalles de Infracción', {
            'fields': [
                'infraction_code', 'infraction_type', 'severity', 
                'detected_at', 'device', 'zone', 'location_lat', 'location_lon'
            ]
        }),
        ('Vehículo y Conductor', {
            'fields': [
                'license_plate_detected', 'license_plate_confidence',
                'vehicle', 'driver'
            ]
        }),
        ('Datos de Velocidad', {
            'fields': [
                'detected_speed', 'speed_limit', 'speed_excess_display'
            ],
            'classes': ['collapse']
        }),
        ('Evidencia', {
            'fields': [
                'snapshot_url', 'video_url', 'evidence_metadata', 'evidence_preview'
            ]
        }),
        ('Revisión', {
            'fields': [
                'status', 'reviewed_by', 'reviewed_at', 'review_notes'
            ]
        }),
        ('Información de Multa', {
            'fields': [
                'fine_amount', 'fine_due_date', 'payment_date'
            ],
            'classes': ['collapse']
        }),
        ('🤖 ML & Performance Metrics', {
            'fields': [
                'recidivism_risk', 'risk_factors',
                'processing_time_seconds', 'ml_prediction_time_ms'
            ]
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    )
    
    def evidence_preview(self, obj):
        """Display a preview of the evidence"""
        if obj.snapshot_url:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 150px;" />',
                obj.snapshot_url
            )
        return "No snapshot available"
    evidence_preview.short_description = "Evidence Preview"
    
    def speed_excess_display(self, obj):
        """Display speed excess in a readable format"""
        if obj.is_speed_violation:
            excess = obj.speed_excess
            if excess > 0:
                return f"+{excess:.1f} km/h over limit"
            else:
                return "Within speed limit"
        return "N/A"
    speed_excess_display.short_description = "Speed Excess"
    
    def processing_time_display(self, obj):
        """Display processing time in seconds"""
        if obj.processing_time_seconds:
            return f"{obj.processing_time_seconds:.3f}s"
        return "-"
    processing_time_display.short_description = "⏱️ Processing"
    processing_time_display.admin_order_field = 'processing_time_seconds'
    
    def ml_prediction_time_display(self, obj):
        """Display ML prediction time in milliseconds"""
        if obj.ml_prediction_time_ms:
            return f"{obj.ml_prediction_time_ms:.2f}ms"
        return "-"
    ml_prediction_time_display.short_description = "🤖 ML Time"
    ml_prediction_time_display.admin_order_field = 'ml_prediction_time_ms'
    
    def recidivism_risk_display(self, obj):
        """Display recidivism risk with color coding"""
        if obj.recidivism_risk is not None:
            risk_pct = int(obj.recidivism_risk * 100)
            if obj.recidivism_risk >= 0.75:
                color = '#dc3545'  # red
                icon = '🔴'
            elif obj.recidivism_risk >= 0.50:
                color = '#fd7e14'  # orange
                icon = '🟠'
            elif obj.recidivism_risk >= 0.25:
                color = '#ffc107'  # yellow
                icon = '🟡'
            else:
                color = '#28a745'  # green
                icon = '🟢'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} {}%</span>',
                color, icon, risk_pct
            )
        return "-"
    recidivism_risk_display.short_description = "🎯 Risk"
    recidivism_risk_display.admin_order_field = 'recidivism_risk'


@admin.register(InfractionEvent)
class InfractionEventAdmin(admin.ModelAdmin):
    list_display = ['infraction', 'event_type', 'user', 'timestamp']
    list_filter = ['event_type', 'timestamp']
    search_fields = ['infraction__infraction_code', 'notes']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']


@admin.register(Appeal)
class AppealAdmin(admin.ModelAdmin):
    list_display = [
        'infraction', 'appellant_name', 'status', 
        'submitted_at', 'reviewed_by', 'reviewed_at'
    ]
    list_filter = ['status', 'submitted_at', 'reviewed_at']
    search_fields = [
        'infraction__infraction_code', 'appellant_name', 'appellant_dni'
    ]
    readonly_fields = ['submitted_at', 'updated_at']
    fieldsets = (
        ('Appeal Information', {
            'fields': [
                'infraction', 'reason', 'evidence_description', 'supporting_documents'
            ]
        }),
        ('Appellant Details', {
            'fields': [
                'appellant_name', 'appellant_dni', 'appellant_phone', 'appellant_email'
            ]
        }),
        ('Review', {
            'fields': [
                'status', 'reviewed_by', 'review_decision', 'reviewed_at'
            ]
        }),
        ('Metadata', {
            'fields': ['submitted_at', 'updated_at'],
            'classes': ['collapse']
        })
    )


@admin.register(VehicleDetection)
class VehicleDetectionAdmin(admin.ModelAdmin):
    list_display = [
        'vehicle_type', 'confidence', 'license_plate_detected',
        'has_infraction', 'device', 'source', 'detected_at'
    ]
    list_filter = [
        'vehicle_type', 'has_infraction', 'source', 'device', 'detected_at'
    ]
    search_fields = ['license_plate_detected', 'vehicle__license_plate']
    readonly_fields = ['id', 'created_at', 'bbox_area']
    date_hierarchy = 'detected_at'
    ordering = ['-detected_at']


@admin.register(DetectionStatistics)
class DetectionStatisticsAdmin(admin.ModelAdmin):
    list_display = [
        'period_type', 'period_start', 'device', 'zone',
        'total_detections', 'total_infractions', 'avg_confidence'
    ]
    list_filter = ['period_type', 'device', 'zone', 'period_start']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'period_start'
    ordering = ['-period_start']
