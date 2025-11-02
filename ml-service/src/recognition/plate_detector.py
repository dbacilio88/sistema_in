"""
License Plate Detector using YOLOv8 or specialized models.

This module detects license plate regions in vehicle images
with high accuracy and real-time performance.
"""

import logging
import time
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
import cv2
from dataclasses import dataclass
import onnxruntime as ort

from ..config import get_ml_settings

logger = logging.getLogger(__name__)

@dataclass
class PlateDetection:
    """License plate detection result."""
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float
    plate_image: np.ndarray
    vehicle_bbox: Optional[Tuple[int, int, int, int]] = None

class LicensePlateDetector:
    """
    License plate detector using YOLOv8 or specialized models.
    
    Features:
    - High-accuracy plate detection
    - Real-time performance
    - Multiple detection strategies
    - Plate region extraction and preprocessing
    """
    
    def __init__(self, model_path: Optional[str] = None, use_cascade: bool = True):
        """
        Initialize license plate detector.
        
        Args:
            model_path: Path to custom ONNX model (optional)
            use_cascade: Whether to use OpenCV cascade as fallback
        """
        self.settings = get_ml_settings()
        self.model_path = model_path
        self.use_cascade = use_cascade
        self.session = None
        self.cascade = None
        
        # Performance metrics
        self.total_processing_time = 0.0
        self.total_detections = 0
        
        self._initialize_models()
        
        logger.info("LicensePlateDetector initialized")
    
    def _initialize_models(self):
        """Initialize detection models."""
        # Initialize ONNX model if provided
        if self.model_path:
            try:
                providers = self.settings.onnx_providers
                self.session = ort.InferenceSession(self.model_path, providers=providers)
                logger.info(f"Loaded ONNX plate detection model from {self.model_path}")
            except Exception as e:
                logger.warning(f"Failed to load ONNX model: {e}")
                self.session = None
        
        # Initialize OpenCV cascade as fallback
        if self.use_cascade:
            try:
                # Try to load Russian license plate cascade (works well for many formats)
                cascade_path = cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml'
                self.cascade = cv2.CascadeClassifier(cascade_path)
                
                if self.cascade.empty():
                    logger.warning("Failed to load plate cascade classifier")
                    self.cascade = None
                else:
                    logger.info("Loaded OpenCV cascade classifier for plates")
            except Exception as e:
                logger.warning(f"Failed to initialize cascade: {e}")
                self.cascade = None
    
    def detect_plates(self, image: np.ndarray, vehicle_bbox: Optional[Tuple[int, int, int, int]] = None) -> List[PlateDetection]:
        """
        Detect license plates in image.
        
        Args:
            image: Input image (BGR format)
            vehicle_bbox: Optional vehicle bounding box to focus search
            
        Returns:
            List of plate detections
        """
        start_time = time.time()
        
        # Focus on vehicle region if provided
        search_region = image
        region_offset = (0, 0)
        
        if vehicle_bbox:
            x1, y1, x2, y2 = vehicle_bbox
            # Expand region slightly for better detection
            margin = 20
            x1 = max(0, x1 - margin)
            y1 = max(0, y1 - margin)
            x2 = min(image.shape[1], x2 + margin)
            y2 = min(image.shape[0], y2 + margin)
            
            search_region = image[y1:y2, x1:x2]
            region_offset = (x1, y1)
        
        detections = []
        
        # Try ONNX model first
        if self.session:
            onnx_detections = self._detect_with_onnx(search_region, region_offset)
            detections.extend(onnx_detections)
        
        # Fallback to cascade if no ONNX detections
        if not detections and self.cascade:
            cascade_detections = self._detect_with_cascade(search_region, region_offset)
            detections.extend(cascade_detections)
        
        # Fallback to contour-based detection
        if not detections:
            contour_detections = self._detect_with_contours(search_region, region_offset)
            detections.extend(contour_detections)
        
        # Update performance metrics
        processing_time = time.time() - start_time
        self.total_processing_time += processing_time
        self.total_detections += 1
        
        # Filter and sort detections
        detections = self._filter_detections(detections, image)
        
        return detections
    
    def _detect_with_onnx(self, image: np.ndarray, offset: Tuple[int, int]) -> List[PlateDetection]:
        """Detect plates using ONNX model."""
        if not self.session:
            return []
        
        try:
            # Preprocess image for ONNX model
            input_image = self._preprocess_for_onnx(image)
            
            # Run inference
            input_name = self.session.get_inputs()[0].name
            outputs = self.session.run(None, {input_name: input_image})
            
            # Process outputs (assuming YOLOv8-style output)
            detections = self._process_onnx_output(outputs, image, offset)
            
            return detections
            
        except Exception as e:
            logger.error(f"ONNX detection failed: {e}")
            return []
    
    def _detect_with_cascade(self, image: np.ndarray, offset: Tuple[int, int]) -> List[PlateDetection]:
        """Detect plates using OpenCV cascade classifier."""
        if not self.cascade:
            return []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect plates
            plates = self.cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(50, 15),  # Minimum plate size
                maxSize=(300, 100)  # Maximum plate size
            )
            
            detections = []
            for (x, y, w, h) in plates:
                # Adjust coordinates with offset
                x1 = x + offset[0]
                y1 = y + offset[1]
                x2 = x1 + w
                y2 = y1 + h
                
                # Extract plate region
                plate_image = image[y:y+h, x:x+w]
                
                # Calculate confidence based on aspect ratio
                aspect_ratio = w / h
                confidence = self._calculate_cascade_confidence(aspect_ratio, w, h)
                
                detections.append(PlateDetection(
                    bbox=(x1, y1, x2, y2),
                    confidence=confidence,
                    plate_image=plate_image
                ))
            
            return detections
            
        except Exception as e:
            logger.error(f"Cascade detection failed: {e}")
            return []
    
    def _detect_with_contours(self, image: np.ndarray, offset: Tuple[int, int]) -> List[PlateDetection]:
        """Detect plates using contour analysis."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply bilateral filter to reduce noise
            filtered = cv2.bilateralFilter(gray, 11, 17, 17)
            
            # Edge detection
            edges = cv2.Canny(filtered, 30, 200)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            detections = []
            
            for contour in contours:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by size and aspect ratio
                aspect_ratio = w / h
                area = cv2.contourArea(contour)
                
                if (2.0 <= aspect_ratio <= 6.0 and  # Typical plate aspect ratio
                    1000 <= area <= 20000 and      # Reasonable area
                    w >= 50 and h >= 15):          # Minimum size
                    
                    # Adjust coordinates with offset
                    x1 = x + offset[0]
                    y1 = y + offset[1]
                    x2 = x1 + w
                    y2 = y1 + h
                    
                    # Extract plate region
                    plate_image = image[y:y+h, x:x+w]
                    
                    # Calculate confidence based on contour properties
                    confidence = self._calculate_contour_confidence(contour, aspect_ratio, area)
                    
                    detections.append(PlateDetection(
                        bbox=(x1, y1, x2, y2),
                        confidence=confidence,
                        plate_image=plate_image
                    ))
            
            # Sort by confidence and take top candidates
            detections.sort(key=lambda d: d.confidence, reverse=True)
            return detections[:5]  # Return top 5 candidates
            
        except Exception as e:
            logger.error(f"Contour detection failed: {e}")
            return []
    
    def _preprocess_for_onnx(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for ONNX model."""
        # Resize to model input size (assuming 640x640 for YOLOv8)
        resized = cv2.resize(image, (640, 640))
        
        # Convert BGR to RGB and normalize
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        normalized = rgb.astype(np.float32) / 255.0
        
        # Add batch dimension and transpose to CHW format
        input_image = np.transpose(normalized, (2, 0, 1))
        input_image = np.expand_dims(input_image, axis=0)
        
        return input_image
    
    def _process_onnx_output(self, outputs: List[np.ndarray], image: np.ndarray, offset: Tuple[int, int]) -> List[PlateDetection]:
        """Process ONNX model output."""
        # This is a placeholder - actual implementation depends on model output format
        # For YOLOv8-style output: [batch, 84, num_detections] where 84 = 4 bbox + 80 classes
        
        detections = []
        
        if outputs and len(outputs) > 0:
            output = outputs[0]  # First output tensor
            
            # Assuming output shape: [1, 84, num_detections]
            if len(output.shape) == 3:
                num_detections = output.shape[2]
                
                for i in range(num_detections):
                    detection = output[0, :, i]
                    
                    # Extract bbox and confidence (format depends on model)
                    x_center, y_center, width, height = detection[:4]
                    confidence = detection[4]  # Assuming object confidence
                    
                    if confidence > 0.3:  # Confidence threshold
                        # Convert to absolute coordinates
                        h, w = image.shape[:2]
                        x1 = int((x_center - width/2) * w) + offset[0]
                        y1 = int((y_center - height/2) * h) + offset[1]
                        x2 = int((x_center + width/2) * w) + offset[0]
                        y2 = int((y_center + height/2) * h) + offset[1]
                        
                        # Extract plate region
                        plate_y1 = max(0, y1 - offset[1])
                        plate_y2 = min(image.shape[0], y2 - offset[1])
                        plate_x1 = max(0, x1 - offset[0])
                        plate_x2 = min(image.shape[1], x2 - offset[0])
                        
                        plate_image = image[plate_y1:plate_y2, plate_x1:plate_x2]
                        
                        detections.append(PlateDetection(
                            bbox=(x1, y1, x2, y2),
                            confidence=float(confidence),
                            plate_image=plate_image
                        ))
        
        return detections
    
    def _calculate_cascade_confidence(self, aspect_ratio: float, width: int, height: int) -> float:
        """Calculate confidence for cascade detection."""
        # Ideal aspect ratio for license plates is around 3.5-4.5
        ratio_score = 1.0 - abs(aspect_ratio - 4.0) / 4.0
        ratio_score = max(0.0, ratio_score)
        
        # Size score - prefer medium-sized detections
        size_score = min(width * height / 10000, 1.0)
        
        return (ratio_score * 0.7 + size_score * 0.3) * 0.8  # Max 0.8 for cascade
    
    def _calculate_contour_confidence(self, contour: np.ndarray, aspect_ratio: float, area: float) -> float:
        """Calculate confidence for contour detection."""
        # Aspect ratio score
        ratio_score = 1.0 - abs(aspect_ratio - 4.0) / 4.0
        ratio_score = max(0.0, ratio_score)
        
        # Area score
        area_score = min(area / 5000, 1.0)
        
        # Contour approximation score (rectangularity)
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        rect_score = 1.0 / (1.0 + abs(len(approx) - 4))  # Prefer 4-sided shapes
        
        return (ratio_score * 0.5 + area_score * 0.3 + rect_score * 0.2) * 0.6  # Max 0.6 for contour
    
    def _filter_detections(self, detections: List[PlateDetection], image: np.ndarray) -> List[PlateDetection]:
        """Filter and clean up detections."""
        if not detections:
            return []
        
        # Sort by confidence
        detections.sort(key=lambda d: d.confidence, reverse=True)
        
        # Remove overlapping detections (NMS)
        filtered = []
        for detection in detections:
            is_duplicate = False
            for existing in filtered:
                iou = self._calculate_iou(detection.bbox, existing.bbox)
                if iou > 0.5:  # IoU threshold for NMS
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append(detection)
        
        # Limit to top 3 detections
        return filtered[:3]
    
    def _calculate_iou(self, bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> float:
        """Calculate Intersection over Union for two bounding boxes."""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def preprocess_plate_image(self, plate_image: np.ndarray) -> np.ndarray:
        """
        Preprocess plate image for better OCR.
        
        Args:
            plate_image: Raw plate image
            
        Returns:
            Preprocessed image for OCR
        """
        if plate_image.size == 0:
            return plate_image
        
        # Resize to standard height while maintaining aspect ratio
        height = 64
        width = int(plate_image.shape[1] * height / plate_image.shape[0])
        resized = cv2.resize(plate_image, (width, height))
        
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
        
        # Threshold to binary
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get detection performance statistics."""
        avg_time = self.total_processing_time / max(self.total_detections, 1)
        
        return {
            "total_detections": self.total_detections,
            "avg_processing_time_ms": avg_time * 1000,
            "fps": 1.0 / max(avg_time, 0.001),
            "has_onnx_model": self.session is not None,
            "has_cascade": self.cascade is not None
        }
    
    def visualize_detections(self, image: np.ndarray, detections: List[PlateDetection]) -> np.ndarray:
        """
        Draw detection visualization on image.
        
        Args:
            image: Input image
            detections: List of plate detections
            
        Returns:
            Image with detections drawn
        """
        vis_image = image.copy()
        
        for i, detection in enumerate(detections):
            x1, y1, x2, y2 = detection.bbox
            confidence = detection.confidence
            
            # Draw bounding box
            color = (0, 255, 0)  # Green for plates
            cv2.rectangle(vis_image, (x1, y1), (x2, y2), color, 2)
            
            # Draw confidence
            label = f"Plate {confidence:.2f}"
            cv2.putText(vis_image, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return vis_image