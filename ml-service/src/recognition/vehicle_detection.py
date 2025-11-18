"""
Vehicle Detection using YOLOv8.

Advanced vehicle detector for traffic infraction system with support
for multiple vehicle types and high-performance real-time detection.
"""

import logging
import time
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
import cv2
from dataclasses import dataclass
from pathlib import Path

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("Ultralytics YOLO not available. Install with: pip install ultralytics")

from ..config import get_ml_settings

logger = logging.getLogger(__name__)


@dataclass
class VehicleDetection:
    """Vehicle detection result."""
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float
    vehicle_class: str  # car, bus, truck, motorcycle, etc.
    class_id: int
    track_id: Optional[int] = None  # For tracking integration


class VehicleDetector:
    """
    Vehicle detector using YOLOv8 for traffic infraction detection.
    
    Features:
    - Multi-class vehicle detection (car, bus, truck, motorcycle, bicycle)
    - High-performance real-time detection
    - GPU acceleration support
    - Configurable confidence thresholds
    - Integration with tracking systems
    
    Supported vehicle classes:
    - car (class 2)
    - motorcycle (class 3)
    - bus (class 5)
    - truck (class 7)
    - bicycle (class 1) - optional
    """
    
    # COCO dataset class mapping for vehicles
    VEHICLE_CLASSES = {
        1: 'bicycle',
        2: 'car',
        3: 'motorcycle',
        5: 'bus',
        7: 'truck'
    }
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        confidence_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        device: str = 'auto',
        include_bicycle: bool = False
    ):
        """
        Initialize vehicle detector.
        
        Args:
            model_path: Path to YOLOv8 model (default: yolov8n.pt)
            confidence_threshold: Minimum confidence for detection
            iou_threshold: IOU threshold for NMS
            device: Device to run inference ('auto', 'cpu', 'cuda', 'mps')
            include_bicycle: Whether to include bicycle detections
        """
        if not YOLO_AVAILABLE:
            raise RuntimeError("Ultralytics YOLO not installed. Install with: pip install ultralytics")
        
        self.settings = get_ml_settings()
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.include_bicycle = include_bicycle
        
        # Filter vehicle classes
        self.target_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        if include_bicycle:
            self.target_classes.insert(0, 1)
        
        # Initialize model
        if model_path is None:
            model_path = self.settings.yolo_model_path if hasattr(self.settings, 'yolo_model_path') else 'yolov8n.pt'
        
        self.model_path = model_path
        self.device = self._select_device(device)
        
        # Performance metrics
        self.total_processing_time = 0.0
        self.total_detections = 0
        self.frames_processed = 0
        
        self._initialize_model()
        
        logger.info(f"VehicleDetector initialized with model: {model_path}, device: {self.device}")
    
    def _select_device(self, device: str) -> str:
        """Select appropriate device for inference."""
        if device == 'auto':
            try:
                import torch
                if torch.cuda.is_available():
                    return 'cuda'
                elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    return 'mps'
                else:
                    return 'cpu'
            except ImportError:
                return 'cpu'
        return device
    
    def _initialize_model(self):
        """Initialize YOLO model."""
        try:
            logger.info(f"Loading YOLO model from {self.model_path}...")
            self.model = YOLO(self.model_path)
            
            # Warm up model
            dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
            _ = self.model.predict(dummy_img, verbose=False, device=self.device)
            
            logger.info("YOLO model loaded and warmed up successfully")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise
    
    def detect(
        self,
        image: np.ndarray,
        confidence_threshold: Optional[float] = None,
        return_annotated: bool = False
    ) -> Tuple[List[VehicleDetection], Optional[np.ndarray]]:
        """
        Detect vehicles in image.
        
        Args:
            image: Input image (BGR format)
            confidence_threshold: Override default confidence threshold
            return_annotated: Whether to return annotated image
            
        Returns:
            Tuple of (list of detections, optional annotated image)
        """
        start_time = time.time()
        
        if confidence_threshold is None:
            confidence_threshold = self.confidence_threshold
        
        try:
            # Run inference
            results = self.model.predict(
                image,
                conf=confidence_threshold,
                iou=self.iou_threshold,
                classes=self.target_classes,
                verbose=False,
                device=self.device
            )
            
            # Process results
            detections = []
            
            if results and len(results) > 0:
                result = results[0]
                boxes = result.boxes
                
                if boxes is not None and len(boxes) > 0:
                    for box in boxes:
                        # Extract box data
                        xyxy = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0].cpu().numpy())
                        cls = int(box.cls[0].cpu().numpy())
                        
                        # Create detection
                        detection = VehicleDetection(
                            bbox=(int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])),
                            confidence=conf,
                            vehicle_class=self.VEHICLE_CLASSES.get(cls, f'class_{cls}'),
                            class_id=cls
                        )
                        detections.append(detection)
            
            # Get annotated image if requested
            annotated_image = None
            if return_annotated and results:
                annotated_image = results[0].plot()
            
            # Update metrics
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            self.frames_processed += 1
            self.total_detections += len(detections)
            
            if len(detections) > 0:
                logger.debug(
                    f"Detected {len(detections)} vehicles in {processing_time*1000:.1f}ms "
                    f"(avg: {self.get_avg_processing_time()*1000:.1f}ms)"
                )
            
            return detections, annotated_image
            
        except Exception as e:
            logger.error(f"Vehicle detection failed: {e}")
            return [], None
    
    def detect_batch(
        self,
        images: List[np.ndarray],
        confidence_threshold: Optional[float] = None
    ) -> List[List[VehicleDetection]]:
        """
        Detect vehicles in multiple images (batch processing).
        
        Args:
            images: List of input images
            confidence_threshold: Override default confidence threshold
            
        Returns:
            List of detection lists for each image
        """
        if confidence_threshold is None:
            confidence_threshold = self.confidence_threshold
        
        try:
            # Run batch inference
            results = self.model.predict(
                images,
                conf=confidence_threshold,
                iou=self.iou_threshold,
                classes=self.target_classes,
                verbose=False,
                device=self.device
            )
            
            # Process results for each image
            all_detections = []
            
            for result in results:
                detections = []
                boxes = result.boxes
                
                if boxes is not None and len(boxes) > 0:
                    for box in boxes:
                        xyxy = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0].cpu().numpy())
                        cls = int(box.cls[0].cpu().numpy())
                        
                        detection = VehicleDetection(
                            bbox=(int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])),
                            confidence=conf,
                            vehicle_class=self.VEHICLE_CLASSES.get(cls, f'class_{cls}'),
                            class_id=cls
                        )
                        detections.append(detection)
                
                all_detections.append(detections)
            
            return all_detections
            
        except Exception as e:
            logger.error(f"Batch vehicle detection failed: {e}")
            return [[] for _ in images]
    
    def get_avg_processing_time(self) -> float:
        """Get average processing time per frame."""
        if self.frames_processed == 0:
            return 0.0
        return self.total_processing_time / self.frames_processed
    
    def get_fps(self) -> float:
        """Get average FPS."""
        avg_time = self.get_avg_processing_time()
        return 1.0 / avg_time if avg_time > 0 else 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detector statistics."""
        return {
            'frames_processed': self.frames_processed,
            'total_detections': self.total_detections,
            'avg_processing_time_ms': self.get_avg_processing_time() * 1000,
            'avg_fps': self.get_fps(),
            'detections_per_frame': self.total_detections / self.frames_processed if self.frames_processed > 0 else 0
        }
    
    def reset_stats(self):
        """Reset performance statistics."""
        self.total_processing_time = 0.0
        self.total_detections = 0
        self.frames_processed = 0
