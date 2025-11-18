"""
Plate Segmentation using YOLOv8.

Specialized license plate segmentation for accurate plate region extraction
from vehicle images.
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
    logging.warning("Ultralytics YOLO not available")

from ..config import get_ml_settings

logger = logging.getLogger(__name__)


@dataclass
class PlateSegmentation:
    """License plate segmentation result."""
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float
    plate_image: np.ndarray
    mask: Optional[np.ndarray] = None  # Segmentation mask if available
    vehicle_bbox: Optional[Tuple[int, int, int, int]] = None


class PlateSegmenter:
    """
    License plate segmenter using YOLOv8 for precise plate localization.
    
    Features:
    - YOLOv8-based plate detection/segmentation
    - Precise plate region extraction
    - Multiple fallback strategies
    - Automatic image enhancement
    - Real-time performance
    
    This module uses a specialized YOLOv8 model trained specifically for
    license plate detection, providing superior accuracy compared to 
    traditional methods.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        confidence_threshold: float = 0.4,
        iou_threshold: float = 0.45,
        device: str = 'auto',
        use_cascade_fallback: bool = True
    ):
        """
        Initialize plate segmenter.
        
        Args:
            model_path: Path to YOLOv8 plate detection model
            confidence_threshold: Minimum confidence for detection
            iou_threshold: IOU threshold for NMS
            device: Device to run inference
            use_cascade_fallback: Whether to use cascade as fallback
        """
        self.settings = get_ml_settings()
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.use_cascade_fallback = use_cascade_fallback
        
        # Select device
        self.device = self._select_device(device)
        
        # Initialize models
        self.model = None
        self.cascade = None
        
        # Performance metrics
        self.total_processing_time = 0.0
        self.total_detections = 0
        self.frames_processed = 0
        
        self._initialize_models(model_path)
        
        logger.info(f"PlateSegmenter initialized with device: {self.device}")
    
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
    
    def _initialize_models(self, model_path: Optional[str]):
        """Initialize detection models."""
        # Initialize YOLO model for plate detection
        if YOLO_AVAILABLE and model_path:
            try:
                logger.info(f"Loading YOLO plate detection model from {model_path}...")
                self.model = YOLO(model_path)
                
                # Warm up model
                dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
                _ = self.model.predict(dummy_img, verbose=False, device=self.device)
                
                logger.info("YOLO plate detection model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load YOLO plate model: {e}")
                self.model = None
        
        # Initialize cascade as fallback
        if self.use_cascade_fallback:
            try:
                cascade_path = cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml'
                self.cascade = cv2.CascadeClassifier(cascade_path)
                
                if self.cascade.empty():
                    logger.warning("Failed to load plate cascade classifier")
                    self.cascade = None
                else:
                    logger.info("Loaded OpenCV cascade classifier as fallback")
            except Exception as e:
                logger.warning(f"Failed to initialize cascade: {e}")
                self.cascade = None
    
    def segment(
        self,
        image: np.ndarray,
        vehicle_bbox: Optional[Tuple[int, int, int, int]] = None,
        confidence_threshold: Optional[float] = None
    ) -> List[PlateSegmentation]:
        """
        Segment license plates in image.
        
        Args:
            image: Input image (BGR format)
            vehicle_bbox: Optional vehicle bounding box to focus search (x1, y1, x2, y2)
            confidence_threshold: Override default confidence threshold
            
        Returns:
            List of plate segmentations
        """
        start_time = time.time()
        
        if confidence_threshold is None:
            confidence_threshold = self.confidence_threshold
        
        # Focus on vehicle region if provided
        search_region = image
        region_offset = (0, 0)
        
        if vehicle_bbox:
            x1, y1, x2, y2 = vehicle_bbox
            # Expand region slightly for better detection
            margin = 10
            x1 = max(0, x1 - margin)
            y1 = max(0, y1 - margin)
            x2 = min(image.shape[1], x2 + margin)
            y2 = min(image.shape[0], y2 + margin)
            
            search_region = image[y1:y2, x1:x2]
            region_offset = (x1, y1)
        
        segmentations = []
        
        # Try YOLO model first
        if self.model:
            yolo_results = self._segment_with_yolo(
                search_region, 
                region_offset, 
                confidence_threshold
            )
            segmentations.extend(yolo_results)
        
        # Fallback to cascade if no YOLO detections
        if not segmentations and self.cascade:
            cascade_results = self._segment_with_cascade(
                search_region,
                region_offset
            )
            segmentations.extend(cascade_results)
        
        # Update metrics
        processing_time = time.time() - start_time
        self.total_processing_time += processing_time
        self.frames_processed += 1
        self.total_detections += len(segmentations)
        
        if len(segmentations) > 0:
            logger.debug(
                f"Segmented {len(segmentations)} plates in {processing_time*1000:.1f}ms"
            )
        
        return segmentations
    
    def _segment_with_yolo(
        self,
        image: np.ndarray,
        offset: Tuple[int, int],
        confidence_threshold: float
    ) -> List[PlateSegmentation]:
        """Segment plates using YOLO model."""
        segmentations = []
        
        try:
            # Run inference
            results = self.model.predict(
                image,
                conf=confidence_threshold,
                iou=self.iou_threshold,
                verbose=False,
                device=self.device
            )
            
            if results and len(results) > 0:
                result = results[0]
                boxes = result.boxes
                
                if boxes is not None and len(boxes) > 0:
                    for box in boxes:
                        # Extract box data
                        xyxy = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0].cpu().numpy())
                        
                        # Adjust coordinates with offset
                        x1 = int(xyxy[0]) + offset[0]
                        y1 = int(xyxy[1]) + offset[1]
                        x2 = int(xyxy[2]) + offset[0]
                        y2 = int(xyxy[3]) + offset[1]
                        
                        # Extract plate region from original image
                        plate_image = image[
                            int(xyxy[1]):int(xyxy[3]),
                            int(xyxy[0]):int(xyxy[2])
                        ]
                        
                        # Get mask if available (segmentation models)
                        mask = None
                        if hasattr(result, 'masks') and result.masks is not None:
                            # TODO: Extract segmentation mask
                            pass
                        
                        segmentation = PlateSegmentation(
                            bbox=(x1, y1, x2, y2),
                            confidence=conf,
                            plate_image=plate_image,
                            mask=mask
                        )
                        segmentations.append(segmentation)
        
        except Exception as e:
            logger.error(f"YOLO plate segmentation failed: {e}")
        
        return segmentations
    
    def _segment_with_cascade(
        self,
        image: np.ndarray,
        offset: Tuple[int, int]
    ) -> List[PlateSegmentation]:
        """Segment plates using OpenCV cascade classifier."""
        if not self.cascade:
            return []
        
        segmentations = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect plates
            plates = self.cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(50, 15),
                maxSize=(300, 100)
            )
            
            for (x, y, w, h) in plates:
                # Adjust coordinates with offset
                x1 = x + offset[0]
                y1 = y + offset[1]
                x2 = x1 + w
                y2 = y1 + h
                
                # Extract plate region
                plate_image = image[y:y+h, x:x+w]
                
                # Calculate confidence based on aspect ratio
                aspect_ratio = w / h if h > 0 else 0
                confidence = self._calculate_cascade_confidence(aspect_ratio, w, h)
                
                segmentation = PlateSegmentation(
                    bbox=(x1, y1, x2, y2),
                    confidence=confidence,
                    plate_image=plate_image,
                    mask=None
                )
                segmentations.append(segmentation)
        
        except Exception as e:
            logger.error(f"Cascade plate segmentation failed: {e}")
        
        return segmentations
    
    def _calculate_cascade_confidence(
        self,
        aspect_ratio: float,
        width: int,
        height: int
    ) -> float:
        """Calculate confidence score for cascade detection."""
        # Typical plate aspect ratios: 2.5 - 5.0
        confidence = 0.5
        
        if 2.5 <= aspect_ratio <= 5.0:
            confidence = 0.7
        
        # Boost confidence for larger detections
        if width > 100:
            confidence += 0.1
        
        return min(confidence, 0.95)
    
    def preprocess_plate(self, plate_image: np.ndarray) -> np.ndarray:
        """
        Preprocess plate image for better OCR.
        
        Args:
            plate_image: Raw plate image
            
        Returns:
            Preprocessed image
        """
        if plate_image.size == 0:
            return plate_image
        
        # Resize to standard height while maintaining aspect ratio
        target_height = 64
        if plate_image.shape[0] > 0:
            width = int(plate_image.shape[1] * target_height / plate_image.shape[0])
            resized = cv2.resize(plate_image, (width, target_height))
        else:
            resized = plate_image
        
        # Convert to grayscale
        if len(resized.shape) == 3:
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        else:
            gray = resized
        
        # Apply CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        return binary
    
    def get_stats(self) -> Dict[str, Any]:
        """Get segmenter statistics."""
        avg_time = self.total_processing_time / self.frames_processed if self.frames_processed > 0 else 0
        return {
            'frames_processed': self.frames_processed,
            'total_detections': self.total_detections,
            'avg_processing_time_ms': avg_time * 1000,
            'avg_fps': 1.0 / avg_time if avg_time > 0 else 0,
            'detections_per_frame': self.total_detections / self.frames_processed if self.frames_processed > 0 else 0
        }
