"""
Configuration for Enhanced Plate Recognition System.

This module provides configuration settings for all components
of the plate recognition pipeline.
"""

from dataclasses import dataclass
from typing import Optional, List
import os


@dataclass
class VehicleDetectionConfig:
    """Configuration for vehicle detection."""
    model_path: str = 'yolov8n.pt'
    confidence_threshold: float = 0.5
    iou_threshold: float = 0.45
    device: str = 'auto'  # 'auto', 'cpu', 'cuda', 'mps'
    include_bicycle: bool = False
    target_classes: List[int] = None  # None = use default [2, 3, 5, 7]
    
    def __post_init__(self):
        if self.target_classes is None:
            self.target_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
            if self.include_bicycle:
                self.target_classes.insert(0, 1)


@dataclass
class PlateSegmentationConfig:
    """Configuration for plate segmentation."""
    model_path: Optional[str] = None  # Path to YOLOv8 plate model
    confidence_threshold: float = 0.4
    iou_threshold: float = 0.45
    device: str = 'auto'
    use_cascade_fallback: bool = True
    cascade_path: Optional[str] = None  # Auto-detect if None


@dataclass
class TextExtractionConfig:
    """Configuration for text extraction (OCR)."""
    languages: List[str] = None  # None = ['en']
    use_trocr: bool = True
    trocr_model: str = 'microsoft/trocr-base-printed'
    gpu: bool = True
    
    # EasyOCR parameters
    easyocr_allowlist: str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    easyocr_min_size: int = 10
    easyocr_text_threshold: float = 0.3
    easyocr_low_text: float = 0.2
    
    # Preprocessing
    use_clahe: bool = True
    clahe_clip_limit: float = 3.0
    clahe_tile_size: tuple = (8, 8)
    use_denoising: bool = True
    use_sharpening: bool = True
    
    # Multiple strategies
    use_multiple_strategies: bool = True
    min_confidence: float = 0.2
    
    def __post_init__(self):
        if self.languages is None:
            self.languages = ['en']


@dataclass
class VehicleTrackingConfig:
    """Configuration for vehicle tracking."""
    max_age: int = 30  # Frames to keep track alive without detection
    min_hits: int = 3  # Minimum detections before confirming track
    iou_threshold: float = 0.3
    max_distance: float = 100.0  # Maximum centroid distance for matching


@dataclass
class PlateValidationConfig:
    """Configuration for plate validation."""
    # Supported plate formats (regex patterns)
    valid_patterns: List[str] = None
    min_length: int = 5
    max_length: int = 10
    
    # Character corrections
    enable_corrections: bool = True
    correction_rules: dict = None
    
    def __post_init__(self):
        if self.valid_patterns is None:
            self.valid_patterns = [
                r'^[A-Z]{3}-?\d{3}$',      # AAA-123 or AAA123
                r'^[A-Z]{2}-?\d{4}$',      # AB-1234 or AB1234
                r'^[A-Z]\d{2}-?\d{3}$',    # A12-345 or A12345
                r'^[A-Z]{2}\d{2}-?\d{2}$', # AB12-34 or AB1234
            ]
        
        if self.correction_rules is None:
            self.correction_rules = {
                'O': '0',  # O to 0 in numeric contexts
                'I': '1',  # I to 1 in numeric contexts
                'S': '5',  # S to 5 in numeric contexts
                'B': '8',  # B to 8 in numeric contexts
            }


@dataclass
class PipelineConfig:
    """Configuration for complete plate recognition pipeline."""
    # Component configurations
    vehicle_detection: VehicleDetectionConfig = None
    plate_segmentation: PlateSegmentationConfig = None
    text_extraction: TextExtractionConfig = None
    vehicle_tracking: VehicleTrackingConfig = None
    plate_validation: PlateValidationConfig = None
    
    # Pipeline settings
    confidence_threshold: float = 0.5
    process_every_n_frames: int = 1  # Process every Nth frame (1 = all)
    
    # Performance
    gpu: bool = True
    batch_size: int = 1
    
    # Output
    save_annotations: bool = True
    annotation_color_vehicle: tuple = (0, 255, 0)  # Green
    annotation_color_plate: tuple = (0, 0, 255)    # Red
    annotation_thickness: int = 2
    
    # Storage
    save_results_json: bool = True
    save_detected_plates: bool = True
    plates_output_dir: str = 'output/detected_plates'
    
    def __post_init__(self):
        if self.vehicle_detection is None:
            self.vehicle_detection = VehicleDetectionConfig()
        
        if self.plate_segmentation is None:
            self.plate_segmentation = PlateSegmentationConfig()
        
        if self.text_extraction is None:
            self.text_extraction = TextExtractionConfig(gpu=self.gpu)
        
        if self.vehicle_tracking is None:
            self.vehicle_tracking = VehicleTrackingConfig()
        
        if self.plate_validation is None:
            self.plate_validation = PlateValidationConfig()
        
        # Ensure output directory exists
        os.makedirs(self.plates_output_dir, exist_ok=True)


# Predefined configurations

def get_high_accuracy_config() -> PipelineConfig:
    """Get configuration optimized for high accuracy."""
    config = PipelineConfig(
        confidence_threshold=0.7,
        gpu=True,
    )
    config.vehicle_detection.confidence_threshold = 0.7
    config.plate_segmentation.confidence_threshold = 0.6
    config.text_extraction.use_trocr = True
    config.text_extraction.use_multiple_strategies = True
    config.vehicle_tracking.min_hits = 5
    
    return config


def get_high_performance_config() -> PipelineConfig:
    """Get configuration optimized for speed."""
    config = PipelineConfig(
        confidence_threshold=0.4,
        gpu=True,
        process_every_n_frames=2,  # Process every 2nd frame
    )
    config.vehicle_detection.confidence_threshold = 0.4
    config.plate_segmentation.confidence_threshold = 0.3
    config.text_extraction.use_trocr = False  # Disable TrOCR for speed
    config.text_extraction.use_multiple_strategies = False
    config.vehicle_tracking.min_hits = 2
    
    return config


def get_balanced_config() -> PipelineConfig:
    """Get balanced configuration (default)."""
    return PipelineConfig(
        confidence_threshold=0.5,
        gpu=True,
    )


def get_cpu_config() -> PipelineConfig:
    """Get configuration optimized for CPU."""
    config = PipelineConfig(
        confidence_threshold=0.5,
        gpu=False,
        process_every_n_frames=3,  # Process every 3rd frame
    )
    config.vehicle_detection.device = 'cpu'
    config.plate_segmentation.device = 'cpu'
    config.text_extraction.gpu = False
    config.text_extraction.use_trocr = False  # Disable TrOCR on CPU
    
    return config


# Environment-based configuration
def get_config_from_env() -> PipelineConfig:
    """Get configuration from environment variables."""
    config = PipelineConfig()
    
    # Vehicle detection
    if os.getenv('VEHICLE_MODEL_PATH'):
        config.vehicle_detection.model_path = os.getenv('VEHICLE_MODEL_PATH')
    if os.getenv('VEHICLE_CONFIDENCE'):
        config.vehicle_detection.confidence_threshold = float(os.getenv('VEHICLE_CONFIDENCE'))
    
    # Plate segmentation
    if os.getenv('PLATE_MODEL_PATH'):
        config.plate_segmentation.model_path = os.getenv('PLATE_MODEL_PATH')
    if os.getenv('PLATE_CONFIDENCE'):
        config.plate_segmentation.confidence_threshold = float(os.getenv('PLATE_CONFIDENCE'))
    
    # Text extraction
    if os.getenv('USE_TROCR'):
        config.text_extraction.use_trocr = os.getenv('USE_TROCR').lower() == 'true'
    if os.getenv('TROCR_MODEL'):
        config.text_extraction.trocr_model = os.getenv('TROCR_MODEL')
    
    # GPU
    if os.getenv('USE_GPU'):
        config.gpu = os.getenv('USE_GPU').lower() == 'true'
        config.text_extraction.gpu = config.gpu
    
    return config


# Export commonly used configurations
__all__ = [
    'VehicleDetectionConfig',
    'PlateSegmentationConfig',
    'TextExtractionConfig',
    'VehicleTrackingConfig',
    'PlateValidationConfig',
    'PipelineConfig',
    'get_high_accuracy_config',
    'get_high_performance_config',
    'get_balanced_config',
    'get_cpu_config',
    'get_config_from_env',
]
