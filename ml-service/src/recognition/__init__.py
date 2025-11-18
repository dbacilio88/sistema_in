"""
License plate recognition module.

This module provides classes and utilities for detecting and reading
license plates from vehicle images using advanced ML techniques including
YOLOv8, EasyOCR, and TrOCR with Peru-specific validation and formatting.

Enhanced components:
- VehicleDetection: Multi-class vehicle detection with YOLOv8
- PlateSegmentation: Specialized plate detection with YOLOv8
- TextExtraction: Dual OCR pipeline (EasyOCR + TrOCR)
- PlateRecognitionPipeline: Complete end-to-end pipeline
"""

# Legacy components
from .plate_detector import LicensePlateDetector
from .plate_reader import LicensePlateReader
from .plate_validator import PeruvianPlateValidator, PlateFormat

# Enhanced components
from .vehicle_detection import VehicleDetector, VehicleDetection
from .plate_segmentation import PlateSegmenter, PlateSegmentation
from .text_extraction import TextExtractor, PlateText, TextDetection
from .plate_recognition_pipeline import (
    PlateRecognitionPipeline,
    PlateRecognitionResult
)
from .config import (
    VehicleDetectionConfig,
    PlateSegmentationConfig,
    TextExtractionConfig,
    VehicleTrackingConfig,
    PlateValidationConfig,
    PipelineConfig,
    get_high_accuracy_config,
    get_high_performance_config,
    get_balanced_config,
    get_cpu_config,
    get_config_from_env,
)

__all__ = [
    # Legacy
    "LicensePlateDetector",
    "LicensePlateReader",
    "PeruvianPlateValidator",
    "PlateFormat",
    # Enhanced - Detection
    "VehicleDetector",
    "VehicleDetection",
    # Enhanced - Segmentation
    "PlateSegmenter",
    "PlateSegmentation",
    # Enhanced - OCR
    "TextExtractor",
    "PlateText",
    "TextDetection",
    # Enhanced - Pipeline
    "PlateRecognitionPipeline",
    "PlateRecognitionResult",
    # Enhanced - Config
    "VehicleDetectionConfig",
    "PlateSegmentationConfig",
    "TextExtractionConfig",
    "VehicleTrackingConfig",
    "PlateValidationConfig",
    "PipelineConfig",
    "get_high_accuracy_config",
    "get_high_performance_config",
    "get_balanced_config",
    "get_cpu_config",
    "get_config_from_env",
]

__version__ = "2.0.0"