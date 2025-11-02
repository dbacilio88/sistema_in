"""
Real-time traffic analysis system initialization.

This module provides the main entry point and initialization for the 
complete real-time traffic analysis system.
"""

from .analysis_pipeline import RealTimeAnalysisPipeline, PipelineConfig, StreamProcessor
from .stream_service import VideoStreamService, StreamConfig, MultiStreamManager
from .monitoring import PerformanceMonitor, ViolationAnalytics, SystemMetrics, AlertRule

__all__ = [
    # Core pipeline components
    'RealTimeAnalysisPipeline',
    'PipelineConfig', 
    'StreamProcessor',
    
    # Stream handling
    'VideoStreamService',
    'StreamConfig',
    'MultiStreamManager',
    
    # Monitoring and analytics
    'PerformanceMonitor',
    'ViolationAnalytics', 
    'SystemMetrics',
    'AlertRule'
]

# Version information
__version__ = "1.0.0"
__author__ = "Traffic Analysis Team"
__description__ = "Real-time traffic analysis and violation detection system"

# Default configurations
DEFAULT_PIPELINE_CONFIG = PipelineConfig(
    detection_model_path="models/yolov8x.onnx",
    detection_confidence_threshold=0.5,
    detection_iou_threshold=0.4,
    
    max_disappeared=30,
    max_distance=100.0,
    tracker_memory=100,
    
    plate_detection_enabled=True,
    plate_confidence_threshold=0.7,
    
    speed_analysis_enabled=True,
    speed_calculation_window=30,
    speed_limit_kmh=60.0,
    
    violation_detection_enabled=True,
    notification_enabled=True,
    
    target_fps=30.0,
    max_frame_buffer_size=300,
    reconnect_delay_seconds=5.0,
    
    metrics_enabled=True,
    log_metrics_interval=100,
    
    save_violations=True,
    save_evidence=True,
    evidence_retention_days=30
)

DEFAULT_STREAM_CONFIG = StreamConfig(
    reconnect_attempts=5,
    reconnect_delay_seconds=2.0,
    connection_timeout_seconds=10.0,
    
    buffer_size=10,
    drop_frames_on_delay=True,
    
    rtsp_transport="tcp",
    target_fps=30.0,
    resize_width=None,
    resize_height=None
)