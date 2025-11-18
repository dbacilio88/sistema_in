"""
Plate Recognition Orchestrator.

Complete pipeline integrating vehicle detection, tracking, plate segmentation,
and text extraction for comprehensive license plate recognition.
"""

import logging
import time
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
import cv2
from dataclasses import dataclass, field
from pathlib import Path

from .vehicle_detection import VehicleDetector, VehicleDetection
from .plate_segmentation import PlateSegmenter, PlateSegmentation
from .text_extraction import TextExtractor, PlateText
from ..tracking.vehicle_tracker import VehicleTracker, TrackedVehicle
from ..config import get_ml_settings

logger = logging.getLogger(__name__)


@dataclass
class PlateRecognitionResult:
    """Complete plate recognition result."""
    track_id: int
    vehicle_class: str
    vehicle_bbox: Tuple[int, int, int, int]
    plate_bbox: Tuple[int, int, int, int]
    plate_text: str
    plate_confidence: float
    detection_confidence: float
    frame_number: int
    timestamp: float
    trajectory: List[Tuple[int, int]] = field(default_factory=list)
    speed: Optional[float] = None


class PlateRecognitionPipeline:
    """
    Complete license plate recognition pipeline.
    
    Pipeline stages:
    1. Video Input
    2. Vehicle Detection (YOLOv8)
    3. Vehicle Tracking (DeepSORT/Simple)
    4. Plate Detection (YOLOv8 Specialized)
    5. Text Extraction (EasyOCR + TrOCR)
    6. Validation & Post-processing
    7. Database Storage
    
    Features:
    - End-to-end plate recognition
    - Multi-vehicle tracking
    - High accuracy OCR with dual pipeline
    - Real-time performance optimization
    - Comprehensive logging and metrics
    """
    
    def __init__(
        self,
        vehicle_model_path: Optional[str] = None,
        plate_model_path: Optional[str] = None,
        use_trocr: bool = True,
        gpu: bool = None,
        confidence_threshold: float = 0.5
    ):
        """
        Initialize plate recognition pipeline.
        
        Args:
            vehicle_model_path: Path to vehicle detection model
            plate_model_path: Path to plate detection model
            use_trocr: Whether to use TrOCR in addition to EasyOCR
            gpu: Whether to use GPU acceleration
            confidence_threshold: Minimum confidence for detections
        """
        self.settings = get_ml_settings()
        self.confidence_threshold = confidence_threshold
        
        # Initialize components
        logger.info("Initializing PlateRecognitionPipeline...")
        
        # Vehicle detector
        self.vehicle_detector = VehicleDetector(
            model_path=vehicle_model_path,
            confidence_threshold=confidence_threshold,
            device='auto'
        )
        logger.info("✓ Vehicle detector initialized")
        
        # Vehicle tracker
        self.vehicle_tracker = VehicleTracker(
            max_age=30,
            min_hits=3,
            iou_threshold=0.3
        )
        logger.info("✓ Vehicle tracker initialized")
        
        # Plate segmenter
        self.plate_segmenter = PlateSegmenter(
            model_path=plate_model_path,
            confidence_threshold=0.4,
            device='auto'
        )
        logger.info("✓ Plate segmenter initialized")
        
        # Text extractor
        self.text_extractor = TextExtractor(
            languages=['en'],
            use_trocr=use_trocr,
            gpu=gpu
        )
        logger.info("✓ Text extractor initialized")
        
        # State management
        self.frame_count = 0
        self.recognized_plates: Dict[int, PlateRecognitionResult] = {}
        
        # Performance metrics
        self.total_processing_time = 0.0
        self.total_vehicles_detected = 0
        self.total_plates_recognized = 0
        
        logger.info("PlateRecognitionPipeline initialized successfully")
    
    def process_frame(
        self,
        frame: np.ndarray,
        timestamp: Optional[float] = None
    ) -> List[PlateRecognitionResult]:
        """
        Process single frame through complete pipeline.
        
        Args:
            frame: Input frame (BGR format)
            timestamp: Frame timestamp
            
        Returns:
            List of plate recognition results
        """
        start_time = time.time()
        self.frame_count += 1
        
        if timestamp is None:
            timestamp = time.time()
        
        results = []
        
        try:
            # Stage 1: Detect vehicles
            vehicle_detections, _ = self.vehicle_detector.detect(frame)
            self.total_vehicles_detected += len(vehicle_detections)
            
            logger.debug(f"Frame {self.frame_count}: Detected {len(vehicle_detections)} vehicles")
            
            # Stage 2: Update tracking
            detection_tuples = [
                (det.bbox, det.confidence, det.vehicle_class)
                for det in vehicle_detections
            ]
            tracked_vehicles = self.vehicle_tracker.update(detection_tuples)
            
            logger.debug(f"Frame {self.frame_count}: Tracking {len(tracked_vehicles)} vehicles")
            
            # Stage 3-5: Process each tracked vehicle
            for track in tracked_vehicles:
                # Skip if we already have a high-confidence plate for this track
                if track.track_id in self.recognized_plates:
                    existing = self.recognized_plates[track.track_id]
                    if existing.plate_confidence > 0.85:
                        continue
                
                # Stage 3: Segment plate
                plate_segmentations = self.plate_segmenter.segment(
                    frame,
                    vehicle_bbox=track.current_bbox
                )
                
                if not plate_segmentations:
                    continue
                
                # Use best plate detection
                best_plate = max(plate_segmentations, key=lambda p: p.confidence)
                
                # Stage 4: Extract text
                plate_text_result = self.text_extractor.extract(best_plate.plate_image)
                
                if not plate_text_result.text:
                    continue
                
                # Stage 5: Validate and create result
                if self._validate_plate_format(plate_text_result.text):
                    # Create recognition result
                    result = PlateRecognitionResult(
                        track_id=track.track_id,
                        vehicle_class=track.vehicle_class,
                        vehicle_bbox=track.current_bbox,
                        plate_bbox=best_plate.bbox,
                        plate_text=plate_text_result.text,
                        plate_confidence=plate_text_result.confidence,
                        detection_confidence=track.confidence,
                        frame_number=self.frame_count,
                        timestamp=timestamp,
                        trajectory=list(track.trajectory),
                        speed=track.speed
                    )
                    
                    # Update tracker with plate
                    self.vehicle_tracker.associate_plate(
                        track.track_id,
                        plate_text_result.text,
                        plate_text_result.confidence
                    )
                    
                    # Store/update result
                    if track.track_id not in self.recognized_plates or \
                       plate_text_result.confidence > self.recognized_plates[track.track_id].plate_confidence:
                        self.recognized_plates[track.track_id] = result
                        self.total_plates_recognized += 1
                        
                        logger.info(
                            f"✓ Recognized plate '{plate_text_result.text}' "
                            f"(track {track.track_id}, conf: {plate_text_result.confidence:.2f})"
                        )
                    
                    results.append(result)
            
            # Update metrics
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            
            if results:
                logger.info(
                    f"Frame {self.frame_count}: Recognized {len(results)} plates "
                    f"in {processing_time*1000:.1f}ms"
                )
            
            return results
            
        except Exception as e:
            logger.error(f"Frame processing failed: {e}")
            return []
    
    def process_video(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        save_annotations: bool = True,
        fps_limit: Optional[int] = None
    ) -> List[PlateRecognitionResult]:
        """
        Process entire video file.
        
        Args:
            video_path: Path to input video
            output_path: Path to save annotated video (optional)
            save_annotations: Whether to draw annotations
            fps_limit: Limit processing FPS (for testing)
            
        Returns:
            List of all plate recognition results
        """
        logger.info(f"Processing video: {video_path}")
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Failed to open video: {video_path}")
            return []
        
        # Video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"Video: {width}x{height} @ {fps} FPS, {total_frames} frames")
        
        # Setup output writer if needed
        out_writer = None
        if output_path and save_annotations:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        all_results = []
        frame_idx = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # FPS limiting for testing
                if fps_limit and frame_idx % max(1, int(fps / fps_limit)) != 0:
                    frame_idx += 1
                    continue
                
                # Process frame
                timestamp = frame_idx / fps
                results = self.process_frame(frame, timestamp)
                all_results.extend(results)
                
                # Annotate frame if needed
                if out_writer and save_annotations:
                    annotated = self._annotate_frame(frame, results)
                    out_writer.write(annotated)
                
                frame_idx += 1
                
                # Progress logging
                if frame_idx % 30 == 0:
                    progress = (frame_idx / total_frames) * 100
                    logger.info(f"Progress: {progress:.1f}% ({frame_idx}/{total_frames})")
        
        finally:
            cap.release()
            if out_writer:
                out_writer.release()
        
        logger.info(
            f"Video processing complete: {len(all_results)} plates recognized "
            f"from {total_frames} frames"
        )
        
        return all_results
    
    def _validate_plate_format(self, plate_text: str) -> bool:
        """
        Validate plate text format for Peruvian plates.
        
        Peruvian formats:
        - Old Standard: ABC-123 (3 letters + 3 numbers)
        - New Standard: ABC-1234 (3 letters + 4 numbers)
        - Also accepts ABC 123 (space instead of hyphen)
        
        Args:
            plate_text: Plate text to validate
            
        Returns:
            True if valid Peruvian format
        """
        import re
        
        # Peruvian plate format patterns
        patterns = [
            r'^[A-Z]{3}[-\s]?\d{3}$',   # ABC-123 or ABC 123 (old standard)
            r'^[A-Z]{3}[-\s]?\d{4}$',   # ABC-1234 or ABC 1234 (new standard)
            r'^T\d[A-Z][-\s]?\d{3}$',   # T1A-123 (taxi)
            r'^[A-Z]\d[-\s]?\d{3}$',    # A1-123 (motorcycle)
            r'^[A-Z]{2}[-\s]?\d{4}$',   # AB-1234 (commercial)
            r'^PNP[-\s]?\d{3,4}$',      # PNP-123 (police)
        ]
        
        # Normalize text (remove multiple spaces, trim)
        normalized = ' '.join(plate_text.split())
        
        for pattern in patterns:
            if re.match(pattern, normalized):
                return True
        
        # Check minimum length for potential valid plates
        clean_text = normalized.replace('-', '').replace(' ', '')
        if len(clean_text) >= 5 and len(clean_text) <= 7:
            # Additional check: should have both letters and numbers
            has_letters = any(c.isalpha() for c in clean_text)
            has_numbers = any(c.isdigit() for c in clean_text)
            if has_letters and has_numbers:
                return True
        
        return False
    
    def _annotate_frame(
        self,
        frame: np.ndarray,
        results: List[PlateRecognitionResult]
    ) -> np.ndarray:
        """
        Annotate frame with detection results.
        
        Args:
            frame: Input frame
            results: Recognition results
            
        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        
        for result in results:
            # Draw vehicle bbox
            x1, y1, x2, y2 = result.vehicle_bbox
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw plate bbox
            px1, py1, px2, py2 = result.plate_bbox
            cv2.rectangle(annotated, (px1, py1), (px2, py2), (0, 0, 255), 2)
            
            # Draw plate text
            label = f"{result.plate_text} ({result.plate_confidence:.2f})"
            cv2.putText(
                annotated,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
            
            # Draw track ID
            track_label = f"ID: {result.track_id}"
            cv2.putText(
                annotated,
                track_label,
                (x1, y2 + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 0),
                1
            )
        
        return annotated
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        avg_time = self.total_processing_time / self.frame_count if self.frame_count > 0 else 0
        
        return {
            'frames_processed': self.frame_count,
            'total_vehicles_detected': self.total_vehicles_detected,
            'total_plates_recognized': self.total_plates_recognized,
            'unique_plates': len(self.recognized_plates),
            'avg_processing_time_ms': avg_time * 1000,
            'avg_fps': 1.0 / avg_time if avg_time > 0 else 0,
            'vehicle_detector_stats': self.vehicle_detector.get_stats(),
            'plate_segmenter_stats': self.plate_segmenter.get_stats(),
            'text_extractor_stats': self.text_extractor.get_stats(),
            'tracker_stats': self.vehicle_tracker.get_stats()
        }
    
    def reset(self):
        """Reset pipeline state."""
        self.frame_count = 0
        self.recognized_plates.clear()
        self.vehicle_tracker.reset()
        self.total_processing_time = 0.0
        self.total_vehicles_detected = 0
        self.total_plates_recognized = 0
