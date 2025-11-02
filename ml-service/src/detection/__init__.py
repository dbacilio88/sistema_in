"""
Detection module for vehicle and object detection
"""

from .vehicle_detector import YOLOv8VehicleDetector, Detection, PerformanceMetrics, create_detector

__all__ = [
    "YOLOv8VehicleDetector",
    "Detection", 
    "PerformanceMetrics",
    "create_detector"
]