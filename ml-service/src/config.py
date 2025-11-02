"""
Configuration settings for ML Service
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict


class MLSettings(BaseSettings):
    """ML Service configuration settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        env_prefix="ML_"
    )
    
    # Service settings
    SERVICE_NAME: str = "ML Traffic Analysis Service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    MODELS_DIR: Path = BASE_DIR / "models"
    WEIGHTS_DIR: Path = MODELS_DIR / "weights"
    DATASETS_DIR: Path = BASE_DIR / "datasets"
    OUTPUTS_DIR: Path = BASE_DIR / "outputs"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # YOLOv8 Detection Settings
    YOLO_MODEL_SIZE: str = "x"  # n, s, m, l, x
    YOLO_WEIGHTS_PATH: Path = WEIGHTS_DIR / "yolov8x.pt"
    YOLO_ONNX_PATH: Path = WEIGHTS_DIR / "yolov8x.onnx"
    YOLO_TENSORRT_PATH: Path = WEIGHTS_DIR / "yolov8x.engine"
    
    # Detection parameters
    CONFIDENCE_THRESHOLD: float = 0.5
    NMS_THRESHOLD: float = 0.45
    MAX_DETECTIONS: int = 100
    
    # Vehicle classes from COCO dataset
    VEHICLE_CLASSES: List[int] = [2, 3, 5, 7]  # car, motorcycle, bus, truck
    CLASS_NAMES: Dict[int, str] = {
        2: "car",
        3: "motorcycle", 
        5: "bus",
        7: "truck"
    }
    
    # Performance settings
    TARGET_FPS: int = 30
    MAX_LATENCY_MS: float = 100.0
    BATCH_SIZE: int = 1
    
    # GPU settings
    USE_GPU: bool = True
    GPU_DEVICE_ID: int = 0
    TENSORRT_ENABLED: bool = True
    
    # ONNX Runtime settings
    ONNX_PROVIDERS: List[str] = [
        "TensorrtExecutionProvider",
        "CUDAExecutionProvider", 
        "CPUExecutionProvider"
    ]
    
    # Tracking settings
    TRACKER_TYPE: str = "deepsort"  # deepsort, sort, bytetrack
    MAX_TRACK_AGE: int = 30
    MIN_TRACK_HITS: int = 3
    TRACK_IOU_THRESHOLD: float = 0.3
    
    # OCR settings
    OCR_ENGINE: str = "easyocr"  # easyocr, tesseract
    OCR_LANGUAGES: List[str] = ["en"]
    PLATE_MIN_CONFIDENCE: float = 0.7
    
    # License plate patterns (Peru)
    PERU_PLATE_PATTERNS: List[str] = [
        r"^[A-Z]{3}-\d{3}$",      # ABC-123 (old format)
        r"^[A-Z]{3}\d{3}$",       # ABC123 (old format)
        r"^[A-Z]{2}\d{4}$",       # AB1234 (taxi)
        r"^[A-Z]{3}-\d{4}$",      # ABC-1234 (new format)
        r"^[A-Z]{4}\d{2}$",       # ABCD12 (diplomatic)
    ]
    
    # Speed calculation settings
    ZONE_LENGTH_METERS: float = 50.0  # Default zone length
    SPEED_CALCULATION_METHOD: str = "optical_flow"  # optical_flow, tracking
    SPEED_LIMIT_KMH: float = 60.0
    SPEED_TOLERANCE_PERCENT: float = 10.0  # 10% tolerance
    
    # Calibration settings
    PIXEL_TO_METER_RATIO: float = 0.05  # 1 pixel = 0.05 meters (to be calibrated)
    CAMERA_HEIGHT_METERS: float = 6.0
    CAMERA_ANGLE_DEGREES: float = 15.0
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    ENABLE_PERFORMANCE_LOGS: bool = True
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_COLLECTION_INTERVAL: int = 10  # seconds
    
    def create_directories(self):
        """Create necessary directories"""
        for dir_path in [
            self.MODELS_DIR,
            self.WEIGHTS_DIR, 
            self.DATASETS_DIR,
            self.OUTPUTS_DIR,
            self.LOGS_DIR
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_model_path(self, model_type: str = "onnx") -> Path:
        """Get model path based on type"""
        if model_type == "pytorch":
            return self.YOLO_WEIGHTS_PATH
        elif model_type == "onnx":
            return self.YOLO_ONNX_PATH
        elif model_type == "tensorrt":
            return self.YOLO_TENSORRT_PATH
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def get_onnx_providers(self) -> List[tuple]:
        """Get ONNX Runtime providers with configurations"""
        providers = []
        
        if self.USE_GPU and "TensorrtExecutionProvider" in self.ONNX_PROVIDERS:
            providers.append((
                "TensorrtExecutionProvider", 
                {
                    "device_id": self.GPU_DEVICE_ID,
                    "trt_max_workspace_size": 2147483648,  # 2GB
                    "trt_fp16_enable": True,
                }
            ))
        
        if self.USE_GPU and "CUDAExecutionProvider" in self.ONNX_PROVIDERS:
            providers.append((
                "CUDAExecutionProvider",
                {
                    "device_id": self.GPU_DEVICE_ID,
                }
            ))
        
        if "CPUExecutionProvider" in self.ONNX_PROVIDERS:
            providers.append("CPUExecutionProvider")
        
        return providers


# Global settings instance
ml_settings = MLSettings()

# Create directories on import
ml_settings.create_directories()