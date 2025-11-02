"""
Speed analysis module for traffic violation detection.

This module provides camera calibration, speed calculation, and
violation detection capabilities for traffic monitoring systems.

Features:
- Camera calibration with homography transformation
- Real-world speed calculation from pixel tracking
- Multi-zone speed limit enforcement
- Violation detection and evidence collection
- Performance optimization for real-time processing

Components:
- CameraCalibrator: Camera calibration and coordinate transformation
- SpeedCalculator: Speed calculation from tracking trajectories
- SpeedAnalyzer: Complete violation detection pipeline
"""

from .camera_calibrator import CameraCalibrator, CalibrationPoint, CalibrationZone
from .speed_calculator import SpeedCalculator, SpeedMeasurement, SpeedViolation, SpeedUnit
from .speed_analyzer import SpeedAnalyzer, AnalysisMode, ViolationEvent, AnalysisResult

__version__ = "1.0.0"

__all__ = [
    "CameraCalibrator",
    "CalibrationPoint", 
    "CalibrationZone",
    "SpeedCalculator",
    "SpeedMeasurement",
    "SpeedViolation",
    "SpeedUnit",
    "SpeedAnalyzer",
    "AnalysisMode",
    "ViolationEvent",
    "AnalysisResult"
]

# Module level configuration
DEFAULT_SPEED_LIMITS = {
    "highway": 100.0,      # km/h
    "urban": 60.0,         # km/h
    "school_zone": 30.0,   # km/h
    "residential": 50.0    # km/h
}

CALIBRATION_QUALITY_THRESHOLDS = {
    "excellent": 0.1,      # < 10cm error
    "good": 0.3,          # < 30cm error
    "acceptable": 0.5,     # < 50cm error
    "poor": 1.0           # < 1m error
}

PERFORMANCE_TARGETS = {
    "min_fps": 15.0,              # Minimum processing FPS
    "target_fps": 25.0,           # Target processing FPS
    "max_processing_time": 0.04,  # Maximum frame processing time (40ms)
    "calibration_confidence": 0.8  # Minimum calibration confidence
}