"""
ML Models Service - Handles loading and inference with YOLOv8 and OCR
"""
import os
from typing import Optional, List, Tuple, Dict, Any
import numpy as np
import cv2
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core import get_logger, settings

logger = get_logger(__name__)


class ModelService:
    """Service for managing ML models (YOLO, OCR)"""
    
    def __init__(self):
        self.yolo_model = None
        self.ocr_reader = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._initialized = False
        
    async def initialize(self):
        """Initialize and load all ML models"""
        if self._initialized:
            return
            
        try:
            logger.info("Initializing ML models...")
            
            # Load YOLO model in thread pool to avoid blocking
            self.yolo_model = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._load_yolo_model
            )
            
            # Load OCR reader (optional - don't fail if it doesn't work)
            try:
                self.ocr_reader = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self._load_ocr_reader
                )
                logger.info("OCR reader loaded successfully")
            except Exception as ocr_error:
                logger.warning(f"Failed to load OCR reader: {str(ocr_error)}")
                logger.warning("Continuing without OCR support")
                self.ocr_reader = None
            
            self._initialized = True
            logger.info("ML models initialized successfully (YOLO ready)")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {str(e)}")
            raise
    
    def _load_yolo_model(self):
        """Load YOLOv8 model (runs in thread pool)"""
        try:
            from ultralytics import YOLO
            
            model_path = settings.YOLO_MODEL_PATH
            
            # Check if model exists, if not download it
            if not os.path.exists(model_path):
                logger.info(f"YOLO model not found at {model_path}, downloading...")
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                # This will download the model to the models directory
                model = YOLO('yolov8n.pt')
                # Move the downloaded file to our models directory
                import shutil
                if os.path.exists('yolov8n.pt') and not os.path.exists(model_path):
                    shutil.move('yolov8n.pt', model_path)
                # Now load from the correct path
                model = YOLO(model_path)
            else:
                model = YOLO(model_path)
            
            logger.info(f"YOLO model loaded from {model_path}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {str(e)}")
            raise
    
    def _load_ocr_reader(self):
        """Load EasyOCR reader (runs in thread pool)"""
        try:
            import easyocr
            
            reader = easyocr.Reader(
                settings.OCR_LANGUAGES,
                gpu=settings.OCR_GPU
            )
            
            logger.info(f"OCR reader loaded for languages: {settings.OCR_LANGUAGES}")
            return reader
            
        except Exception as e:
            logger.error(f"Failed to load OCR reader: {str(e)}")
            raise
    
    async def detect_vehicles(
        self,
        frame: np.ndarray,
        confidence_threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Detect vehicles in a frame using YOLO
        
        Args:
            frame: Input image as numpy array
            confidence_threshold: Minimum confidence for detection
            
        Returns:
            List of detections with bbox, confidence, and class
        """
        if not self._initialized:
            await self.initialize()
        
        if confidence_threshold is None:
            confidence_threshold = settings.YOLO_CONFIDENCE_THRESHOLD
        
        try:
            # Run YOLO inference in thread pool
            results = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.yolo_model.predict(
                    frame,
                    conf=confidence_threshold,
                    iou=settings.YOLO_IOU_THRESHOLD,
                    verbose=False
                )
            )
            
            detections = []
            
            # YOLO vehicle classes (COCO dataset)
            vehicle_classes = {
                2: 'car',
                3: 'motorcycle', 
                5: 'bus',
                7: 'truck'
            }
            
            # Process results
            for result in results:
                boxes = result.boxes
                logger.info(f"YOLO detected {len(boxes)} objects total")
                
                vehicle_count = 0
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    logger.debug(f"Detected object: class={cls}, confidence={conf:.2f}")
                    
                    # Only process vehicle classes
                    if cls in vehicle_classes:
                        vehicle_count += 1
                        xyxy = box.xyxy[0].cpu().numpy()
                        
                        detection = {
                            'type': 'vehicle',
                            'vehicle_type': vehicle_classes[cls],
                            'confidence': conf,
                            'bbox': {
                                'x': int(xyxy[0]),
                                'y': int(xyxy[1]),
                                'width': int(xyxy[2] - xyxy[0]),
                                'height': int(xyxy[3] - xyxy[1])
                            }
                        }
                        detections.append(detection)
                
                logger.info(f"Filtered to {vehicle_count} vehicles from {len(boxes)} objects")
            
            return detections
            
        except Exception as e:
            logger.error(f"Vehicle detection failed: {str(e)}")
            return []
    
    async def detect_license_plate(
        self,
        frame: np.ndarray,
        bbox: Dict[str, int]
    ) -> Optional[Tuple[str, float]]:
        """
        Detect and read license plate from vehicle crop
        
        Args:
            frame: Full frame
            bbox: Bounding box of vehicle {x, y, width, height}
            
        Returns:
            Tuple of (plate_text, confidence) or None
        """
        if not self._initialized:
            await self.initialize()
        
        # Check if OCR is available
        if self.ocr_reader is None:
            logger.debug("OCR reader not available, skipping plate detection")
            return None
        
        try:
            # Extract vehicle region
            x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
            
            # Add some padding and ensure within bounds
            padding = 10
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(frame.shape[1], x + w + padding)
            y2 = min(frame.shape[0], y + h + padding)
            
            vehicle_crop = frame[y1:y2, x1:x2]
            
            if vehicle_crop.size == 0:
                return None
            
            # Run OCR in thread pool
            results = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.ocr_reader.readtext(vehicle_crop)
            )
            
            # Process OCR results
            plates = []
            for (bbox, text, conf) in results:
                # Clean text: remove spaces, keep only alphanumeric and hyphens
                text = text.replace(' ', '').upper()
                text = ''.join(c for c in text if c.isalnum() or c == '-')
                
                # Validate plate format (basic)
                if self._is_valid_plate_format(text):
                    plates.append((text, conf))
            
            # Return best match
            if plates:
                plates.sort(key=lambda x: x[1], reverse=True)
                return plates[0]
            
            return None
            
        except Exception as e:
            logger.error(f"License plate detection failed: {str(e)}")
            return None
    
    def _is_valid_plate_format(self, text: str) -> bool:
        """
        Validate license plate format (Peru format)
        AAA-123, AB-1234, A12-345
        """
        if len(text) < 5 or len(text) > 8:
            return False
        
        if '-' not in text:
            return False
        
        parts = text.split('-')
        if len(parts) != 2:
            return False
        
        letters, numbers = parts[0], parts[1]
        
        # Check various Peru formats
        valid_formats = [
            len(letters) == 3 and letters.isalpha() and numbers.isdigit() and len(numbers) in [3, 4],  # AAA-123 or AAA-1234
            len(letters) == 2 and letters.isalpha() and numbers.isdigit() and len(numbers) == 4,  # AB-1234
            len(letters) == 3 and letters[:1].isalpha() and letters[1:].isdigit() and numbers.isdigit() and len(numbers) == 3  # A12-345
        ]
        
        return any(valid_formats)
    
    async def estimate_speed(
        self,
        detections_history: List[Dict],
        fps: float,
        calibration_data: Optional[Dict] = None
    ) -> Optional[float]:
        """
        Estimate vehicle speed based on tracking history
        
        Args:
            detections_history: List of detections over time
            fps: Frames per second
            calibration_data: Camera calibration data
            
        Returns:
            Estimated speed in km/h or None
        """
        # Simplified speed estimation for MVP
        # In production, use proper optical flow and Kalman filtering
        
        if len(detections_history) < 2:
            return None
        
        try:
            # Calculate pixel displacement
            first = detections_history[0]
            last = detections_history[-1]
            
            x1 = first['bbox']['x'] + first['bbox']['width'] / 2
            y1 = first['bbox']['y'] + first['bbox']['height'] / 2
            
            x2 = last['bbox']['x'] + last['bbox']['width'] / 2
            y2 = last['bbox']['y'] + last['bbox']['height'] / 2
            
            pixel_distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            # Time elapsed
            time_elapsed = len(detections_history) / fps
            
            # Simplified conversion: assume 1 pixel ≈ 0.05 meters (needs calibration)
            # This is a placeholder - real implementation needs camera calibration
            meters_per_pixel = 0.05
            if calibration_data and 'meters_per_pixel' in calibration_data:
                meters_per_pixel = calibration_data['meters_per_pixel']
            
            distance_meters = pixel_distance * meters_per_pixel
            speed_ms = distance_meters / time_elapsed
            speed_kmh = speed_ms * 3.6
            
            # Sanity check
            if speed_kmh > 0 and speed_kmh < 200:
                return round(speed_kmh, 1)
            
            return None
            
        except Exception as e:
            logger.error(f"Speed estimation failed: {str(e)}")
            return None
    
    def shutdown(self):
        """Cleanup resources"""
        if self.executor:
            self.executor.shutdown(wait=True)
        logger.info("Model service shut down")


# Global model service instance
model_service = ModelService()
