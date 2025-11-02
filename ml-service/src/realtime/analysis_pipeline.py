"""
Real-time traffic analysis pipeline that integrates all ML components.

This module provides the main pipeline for processing video streams and
detecting traffic violations in real-time.
"""

import asyncio
import time
import logging
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
from collections import deque
import json
import cv2
import numpy as np

from ..detection.yolo_detector import YOLODetector, Detection
from ..tracking.vehicle_tracker import VehicleTracker, TrackedVehicle  
from ..plate_recognition.plate_detector import PlateDetector, PlateResult
from ..speed.speed_analyzer import SpeedAnalyzer, SpeedViolation
from ..violations.violation_manager import ViolationManager, TrafficViolation
from ..violations.notification_system import NotificationSystem


@dataclass
class StreamMetrics:
    """Metrics for stream processing performance."""
    frames_processed: int = 0
    detections_count: int = 0
    violations_count: int = 0
    
    # Timing metrics (in milliseconds)
    detection_time_ms: float = 0.0
    tracking_time_ms: float = 0.0
    plate_recognition_time_ms: float = 0.0
    speed_analysis_time_ms: float = 0.0
    violation_detection_time_ms: float = 0.0
    total_processing_time_ms: float = 0.0
    
    # Performance metrics
    fps: float = 0.0
    avg_latency_ms: float = 0.0
    memory_usage_mb: float = 0.0
    
    # Error tracking
    errors_count: int = 0
    last_error: Optional[str] = None
    
    def update_timing(self, stage: str, duration_ms: float):
        """Update timing metrics for a specific stage."""
        if stage == "detection":
            self.detection_time_ms = duration_ms
        elif stage == "tracking":
            self.tracking_time_ms = duration_ms
        elif stage == "plate_recognition":
            self.plate_recognition_time_ms = duration_ms
        elif stage == "speed_analysis":
            self.speed_analysis_time_ms = duration_ms
        elif stage == "violation_detection":
            self.violation_detection_time_ms = duration_ms
        
        self.total_processing_time_ms = (
            self.detection_time_ms + 
            self.tracking_time_ms + 
            self.plate_recognition_time_ms + 
            self.speed_analysis_time_ms + 
            self.violation_detection_time_ms
        )
        
        if self.total_processing_time_ms > 0:
            self.fps = 1000.0 / self.total_processing_time_ms


@dataclass
class PipelineConfig:
    """Configuration for the real-time analysis pipeline."""
    
    # Detection configuration
    detection_model_path: str = "models/yolov8x.onnx"
    detection_confidence_threshold: float = 0.5
    detection_iou_threshold: float = 0.4
    
    # Tracking configuration
    max_disappeared: int = 30
    max_distance: float = 100.0
    tracker_memory: int = 100
    
    # Plate recognition configuration
    plate_detection_enabled: bool = True
    plate_confidence_threshold: float = 0.7
    
    # Speed analysis configuration
    speed_analysis_enabled: bool = True
    speed_calculation_window: int = 30  # frames
    speed_limit_kmh: float = 60.0
    
    # Violation detection configuration
    violation_detection_enabled: bool = True
    notification_enabled: bool = True
    
    # Stream processing configuration
    target_fps: float = 30.0
    max_frame_buffer_size: int = 300  # 10 seconds at 30fps
    reconnect_delay_seconds: float = 5.0
    
    # Performance monitoring
    metrics_enabled: bool = True
    log_metrics_interval: int = 100  # frames
    
    # Output configuration
    save_violations: bool = True
    save_evidence: bool = True
    evidence_retention_days: int = 30


@dataclass
class FrameData:
    """Container for frame and associated data."""
    frame: np.ndarray
    timestamp: float
    frame_id: int
    device_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingResult:
    """Result of processing a single frame."""
    frame_data: FrameData
    detections: List[Detection]
    tracked_vehicles: List[TrackedVehicle]
    plate_results: List[PlateResult]
    speed_violations: List[SpeedViolation]
    traffic_violations: List[TrafficViolation]
    processing_time_ms: float
    success: bool = True
    error: Optional[str] = None


class RealTimeAnalysisPipeline:
    """
    Real-time traffic analysis pipeline integrating all ML components.
    
    This pipeline processes video streams in real-time, performing:
    1. Vehicle detection using YOLOv8
    2. Multi-object tracking
    3. License plate recognition
    4. Speed analysis
    5. Violation detection
    6. Real-time notifications
    """
    
    def __init__(self, config: PipelineConfig, device_id: str):
        """
        Initialize the real-time analysis pipeline.
        
        Args:
            config: Pipeline configuration
            device_id: Unique identifier for the camera/device
        """
        self.config = config
        self.device_id = device_id
        self.logger = logging.getLogger(f"pipeline.{device_id}")
        
        # Initialize components
        self._init_components()
        
        # State management
        self.is_running = False
        self.frame_counter = 0
        self.start_time = None
        
        # Frame buffer for video analysis
        self.frame_buffer = deque(maxlen=config.max_frame_buffer_size)
        
        # Metrics and monitoring
        self.metrics = StreamMetrics()
        self.last_metrics_log = 0
        
        # Callbacks for external integration
        self.result_callbacks: List[Callable[[ProcessingResult], None]] = []
        self.metrics_callbacks: List[Callable[[StreamMetrics], None]] = []
        
        # Threading for async processing
        self._processing_lock = threading.Lock()
    
    def _init_components(self):
        """Initialize all ML components."""
        self.logger.info("Initializing pipeline components...")
        
        try:
            # Vehicle detection
            self.detector = YOLODetector(
                model_path=self.config.detection_model_path,
                confidence_threshold=self.config.detection_confidence_threshold,
                iou_threshold=self.config.detection_iou_threshold
            )
            self.logger.info("✓ Vehicle detector initialized")
            
            # Vehicle tracking
            self.tracker = VehicleTracker(
                max_disappeared=self.config.max_disappeared,
                max_distance=self.config.max_distance
            )
            self.logger.info("✓ Vehicle tracker initialized")
            
            # Plate recognition (optional)
            if self.config.plate_detection_enabled:
                self.plate_detector = PlateDetector(
                    confidence_threshold=self.config.plate_confidence_threshold
                )
                self.logger.info("✓ Plate detector initialized")
            else:
                self.plate_detector = None
                self.logger.info("- Plate detection disabled")
            
            # Speed analysis (optional)
            if self.config.speed_analysis_enabled:
                self.speed_analyzer = SpeedAnalyzer(
                    calculation_window=self.config.speed_calculation_window,
                    speed_limit_kmh=self.config.speed_limit_kmh
                )
                self.logger.info("✓ Speed analyzer initialized")
            else:
                self.speed_analyzer = None
                self.logger.info("- Speed analysis disabled")
            
            # Violation detection (optional)
            if self.config.violation_detection_enabled:
                self.violation_manager = ViolationManager()
                self.logger.info("✓ Violation manager initialized")
                
                if self.config.notification_enabled:
                    self.notification_system = NotificationSystem()
                    self.logger.info("✓ Notification system initialized")
                else:
                    self.notification_system = None
                    self.logger.info("- Notifications disabled")
            else:
                self.violation_manager = None
                self.notification_system = None
                self.logger.info("- Violation detection disabled")
            
            self.logger.info("All pipeline components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise
    
    def add_result_callback(self, callback: Callable[[ProcessingResult], None]):
        """Add callback for processing results."""
        self.result_callbacks.append(callback)
    
    def add_metrics_callback(self, callback: Callable[[StreamMetrics], None]):
        """Add callback for metrics updates."""
        self.metrics_callbacks.append(callback)
    
    def process_frame(self, frame: np.ndarray, timestamp: Optional[float] = None) -> ProcessingResult:
        """
        Process a single frame through the entire pipeline.
        
        Args:
            frame: Input video frame
            timestamp: Frame timestamp (current time if None)
            
        Returns:
            ProcessingResult: Complete processing results
        """
        if timestamp is None:
            timestamp = time.time()
        
        frame_data = FrameData(
            frame=frame,
            timestamp=timestamp,
            frame_id=self.frame_counter,
            device_id=self.device_id
        )
        
        processing_start = time.perf_counter()
        
        try:
            result = self._process_frame_internal(frame_data)
            
            # Update metrics
            processing_time = (time.perf_counter() - processing_start) * 1000
            result.processing_time_ms = processing_time
            
            self._update_metrics(result)
            
            # Call callbacks
            for callback in self.result_callbacks:
                try:
                    callback(result)
                except Exception as e:
                    self.logger.error(f"Result callback error: {e}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Frame processing error: {e}")
            self.metrics.errors_count += 1
            self.metrics.last_error = str(e)
            
            return ProcessingResult(
                frame_data=frame_data,
                detections=[],
                tracked_vehicles=[],
                plate_results=[],
                speed_violations=[],
                traffic_violations=[],
                processing_time_ms=(time.perf_counter() - processing_start) * 1000,
                success=False,
                error=str(e)
            )
    
    def _process_frame_internal(self, frame_data: FrameData) -> ProcessingResult:
        """Internal frame processing logic."""
        detections = []
        tracked_vehicles = []
        plate_results = []
        speed_violations = []
        traffic_violations = []
        
        # Stage 1: Vehicle Detection
        detection_start = time.perf_counter()
        detections = self.detector.detect(frame_data.frame)
        detection_time = (time.perf_counter() - detection_start) * 1000
        self.metrics.update_timing("detection", detection_time)
        
        self.logger.debug(f"Detected {len(detections)} vehicles in {detection_time:.1f}ms")
        
        # Stage 2: Vehicle Tracking
        tracking_start = time.perf_counter()
        tracked_vehicles = self.tracker.update(detections, frame_data.frame)
        tracking_time = (time.perf_counter() - tracking_start) * 1000
        self.metrics.update_timing("tracking", tracking_time)
        
        self.logger.debug(f"Tracking {len(tracked_vehicles)} vehicles in {tracking_time:.1f}ms")
        
        # Stage 3: Plate Recognition (if enabled and vehicles detected)
        if self.plate_detector and tracked_vehicles:
            plate_start = time.perf_counter()
            plate_results = self._process_plate_recognition(tracked_vehicles, frame_data.frame)
            plate_time = (time.perf_counter() - plate_start) * 1000
            self.metrics.update_timing("plate_recognition", plate_time)
            
            self.logger.debug(f"Recognized {len(plate_results)} plates in {plate_time:.1f}ms")
        
        # Stage 4: Speed Analysis (if enabled and tracking data available)
        if self.speed_analyzer and tracked_vehicles:
            speed_start = time.perf_counter()
            speed_violations = self._process_speed_analysis(tracked_vehicles, frame_data)
            speed_time = (time.perf_counter() - speed_start) * 1000
            self.metrics.update_timing("speed_analysis", speed_time)
            
            self.logger.debug(f"Detected {len(speed_violations)} speed violations in {speed_time:.1f}ms")
        
        # Stage 5: Violation Detection (if enabled)
        if self.violation_manager:
            violation_start = time.perf_counter()
            traffic_violations = self._process_violation_detection(
                tracked_vehicles, speed_violations, frame_data
            )
            violation_time = (time.perf_counter() - violation_start) * 1000
            self.metrics.update_timing("violation_detection", violation_time)
            
            self.logger.debug(f"Detected {len(traffic_violations)} violations in {violation_time:.1f}ms")
            
            # Send notifications if enabled
            if self.notification_system and traffic_violations:
                self._send_notifications(traffic_violations)
        
        # Add frame to buffer
        self.frame_buffer.append(frame_data)
        
        return ProcessingResult(
            frame_data=frame_data,
            detections=detections,
            tracked_vehicles=tracked_vehicles,
            plate_results=plate_results,
            speed_violations=speed_violations,
            traffic_violations=traffic_violations,
            processing_time_ms=0.0  # Will be set by caller
        )
    
    def _process_plate_recognition(self, vehicles: List[TrackedVehicle], frame: np.ndarray) -> List[PlateResult]:
        """Process plate recognition for tracked vehicles."""
        plate_results = []
        
        for vehicle in vehicles:
            try:
                # Extract vehicle region
                x1, y1, x2, y2 = vehicle.bbox
                vehicle_crop = frame[y1:y2, x1:x2]
                
                if vehicle_crop.size > 0:
                    results = self.plate_detector.detect_and_read(vehicle_crop)
                    
                    for result in results:
                        # Adjust coordinates to full frame
                        result.bbox = (
                            result.bbox[0] + x1,
                            result.bbox[1] + y1,
                            result.bbox[2] + x1,
                            result.bbox[3] + y1
                        )
                        result.vehicle_id = vehicle.track_id
                        plate_results.append(result)
                        
            except Exception as e:
                self.logger.warning(f"Plate recognition error for vehicle {vehicle.track_id}: {e}")
        
        return plate_results
    
    def _process_speed_analysis(self, vehicles: List[TrackedVehicle], frame_data: FrameData) -> List[SpeedViolation]:
        """Process speed analysis for tracked vehicles."""
        speed_violations = []
        
        for vehicle in vehicles:
            try:
                # Calculate speed based on trajectory
                speed = self.speed_analyzer.calculate_speed(
                    vehicle.trajectory, 
                    frame_data.timestamp
                )
                
                if speed is not None:
                    # Check for speed violations
                    violation = self.speed_analyzer.check_speed_violation(
                        vehicle.track_id,
                        speed,
                        frame_data.timestamp,
                        zone_id=f"zone_{self.device_id}"
                    )
                    
                    if violation:
                        speed_violations.append(violation)
                        
            except Exception as e:
                self.logger.warning(f"Speed analysis error for vehicle {vehicle.track_id}: {e}")
        
        return speed_violations
    
    def _process_violation_detection(
        self, 
        vehicles: List[TrackedVehicle], 
        speed_violations: List[SpeedViolation],
        frame_data: FrameData
    ) -> List[TrafficViolation]:
        """Process comprehensive violation detection."""
        try:
            violations = self.violation_manager.process_frame(
                frame_data.frame,
                vehicles,
                speed_violations
            )
            return violations
            
        except Exception as e:
            self.logger.error(f"Violation detection error: {e}")
            return []
    
    def _send_notifications(self, violations: List[TrafficViolation]):
        """Send notifications for detected violations."""
        for violation in violations:
            try:
                alert_id = self.notification_system.send_violation_alert(violation)
                if alert_id:
                    self.logger.info(f"Notification sent for violation {violation.violation_id}: {alert_id}")
                else:
                    self.logger.warning(f"Failed to send notification for violation {violation.violation_id}")
                    
            except Exception as e:
                self.logger.error(f"Notification error for violation {violation.violation_id}: {e}")
    
    def _update_metrics(self, result: ProcessingResult):
        """Update performance metrics."""
        self.frame_counter += 1
        self.metrics.frames_processed += 1
        self.metrics.detections_count += len(result.detections)
        self.metrics.violations_count += len(result.traffic_violations)
        
        # Update running average of latency
        if self.metrics.frames_processed == 1:
            self.metrics.avg_latency_ms = result.processing_time_ms
        else:
            # Exponential moving average
            alpha = 0.1
            self.metrics.avg_latency_ms = (
                alpha * result.processing_time_ms + 
                (1 - alpha) * self.metrics.avg_latency_ms
            )
        
        # Calculate FPS based on processing time
        if result.processing_time_ms > 0:
            instantaneous_fps = 1000.0 / result.processing_time_ms
            if self.metrics.fps == 0:
                self.metrics.fps = instantaneous_fps
            else:
                # Smooth FPS calculation
                self.metrics.fps = 0.9 * self.metrics.fps + 0.1 * instantaneous_fps
        
        # Log metrics periodically
        if (self.metrics.frames_processed - self.last_metrics_log) >= self.config.log_metrics_interval:
            self._log_metrics()
            self.last_metrics_log = self.metrics.frames_processed
            
            # Call metrics callbacks
            for callback in self.metrics_callbacks:
                try:
                    callback(self.metrics)
                except Exception as e:
                    self.logger.error(f"Metrics callback error: {e}")
    
    def _log_metrics(self):
        """Log current performance metrics."""
        self.logger.info(
            f"Pipeline metrics - "
            f"Frames: {self.metrics.frames_processed}, "
            f"FPS: {self.metrics.fps:.1f}, "
            f"Avg latency: {self.metrics.avg_latency_ms:.1f}ms, "
            f"Detections: {self.metrics.detections_count}, "
            f"Violations: {self.metrics.violations_count}, "
            f"Errors: {self.metrics.errors_count}"
        )
        
        # Detailed timing breakdown
        self.logger.debug(
            f"Timing breakdown - "
            f"Detection: {self.metrics.detection_time_ms:.1f}ms, "
            f"Tracking: {self.metrics.tracking_time_ms:.1f}ms, "
            f"Plates: {self.metrics.plate_recognition_time_ms:.1f}ms, "
            f"Speed: {self.metrics.speed_analysis_time_ms:.1f}ms, "
            f"Violations: {self.metrics.violation_detection_time_ms:.1f}ms"
        )
    
    def get_metrics(self) -> StreamMetrics:
        """Get current pipeline metrics."""
        return self.metrics
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive pipeline status."""
        return {
            "device_id": self.device_id,
            "is_running": self.is_running,
            "frame_counter": self.frame_counter,
            "uptime_seconds": time.time() - self.start_time if self.start_time else 0,
            "metrics": {
                "frames_processed": self.metrics.frames_processed,
                "fps": self.metrics.fps,
                "avg_latency_ms": self.metrics.avg_latency_ms,
                "total_processing_time_ms": self.metrics.total_processing_time_ms,
                "detections_count": self.metrics.detections_count,
                "violations_count": self.metrics.violations_count,
                "errors_count": self.metrics.errors_count,
                "last_error": self.metrics.last_error
            },
            "components": {
                "detector": "enabled",
                "tracker": "enabled", 
                "plate_detector": "enabled" if self.plate_detector else "disabled",
                "speed_analyzer": "enabled" if self.speed_analyzer else "disabled",
                "violation_manager": "enabled" if self.violation_manager else "disabled",
                "notification_system": "enabled" if self.notification_system else "disabled"
            },
            "configuration": {
                "target_fps": self.config.target_fps,
                "detection_confidence": self.config.detection_confidence_threshold,
                "speed_limit_kmh": self.config.speed_limit_kmh,
                "save_violations": self.config.save_violations,
                "save_evidence": self.config.save_evidence
            }
        }
    
    def start(self):
        """Start the pipeline."""
        self.is_running = True
        self.start_time = time.time()
        self.frame_counter = 0
        self.metrics = StreamMetrics()
        self.logger.info(f"Pipeline started for device {self.device_id}")
    
    def stop(self):
        """Stop the pipeline."""
        self.is_running = False
        self.logger.info(f"Pipeline stopped for device {self.device_id}")
    
    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics = StreamMetrics()
        self.last_metrics_log = 0
        self.logger.info("Pipeline metrics reset")


class StreamProcessor:
    """
    High-level stream processor that manages multiple camera streams.
    """
    
    def __init__(self):
        """Initialize the stream processor."""
        self.logger = logging.getLogger("stream_processor")
        self.pipelines: Dict[str, RealTimeAnalysisPipeline] = {}
        self.streams: Dict[str, cv2.VideoCapture] = {}
        self.processing_tasks: Dict[str, asyncio.Task] = {}
    
    def add_camera_stream(self, device_id: str, rtsp_url: str, config: PipelineConfig):
        """
        Add a camera stream for processing.
        
        Args:
            device_id: Unique identifier for the camera
            rtsp_url: RTSP stream URL
            config: Pipeline configuration
        """
        if device_id in self.pipelines:
            raise ValueError(f"Device {device_id} already exists")
        
        try:
            # Create pipeline
            pipeline = RealTimeAnalysisPipeline(config, device_id)
            self.pipelines[device_id] = pipeline
            
            # Initialize video capture
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                raise RuntimeError(f"Failed to open RTSP stream: {rtsp_url}")
            
            self.streams[device_id] = cap
            
            self.logger.info(f"Added camera stream: {device_id} -> {rtsp_url}")
            
        except Exception as e:
            self.logger.error(f"Failed to add camera stream {device_id}: {e}")
            raise
    
    def remove_camera_stream(self, device_id: str):
        """Remove a camera stream."""
        if device_id in self.processing_tasks:
            self.processing_tasks[device_id].cancel()
            del self.processing_tasks[device_id]
        
        if device_id in self.streams:
            self.streams[device_id].release()
            del self.streams[device_id]
        
        if device_id in self.pipelines:
            self.pipelines[device_id].stop()
            del self.pipelines[device_id]
        
        self.logger.info(f"Removed camera stream: {device_id}")
    
    async def start_processing(self, device_id: str):
        """Start processing a specific camera stream."""
        if device_id not in self.pipelines:
            raise ValueError(f"Device {device_id} not found")
        
        if device_id in self.processing_tasks:
            self.logger.warning(f"Processing already running for device {device_id}")
            return
        
        pipeline = self.pipelines[device_id]
        stream = self.streams[device_id]
        
        pipeline.start()
        
        # Create async processing task
        task = asyncio.create_task(self._process_stream(device_id, pipeline, stream))
        self.processing_tasks[device_id] = task
        
        self.logger.info(f"Started processing for device {device_id}")
    
    async def stop_processing(self, device_id: str):
        """Stop processing a specific camera stream."""
        if device_id in self.processing_tasks:
            self.processing_tasks[device_id].cancel()
            del self.processing_tasks[device_id]
        
        if device_id in self.pipelines:
            self.pipelines[device_id].stop()
        
        self.logger.info(f"Stopped processing for device {device_id}")
    
    async def _process_stream(self, device_id: str, pipeline: RealTimeAnalysisPipeline, stream: cv2.VideoCapture):
        """Process a single stream asynchronously."""
        try:
            target_frame_time = 1.0 / pipeline.config.target_fps
            
            while pipeline.is_running:
                loop_start = time.perf_counter()
                
                # Read frame
                ret, frame = stream.read()
                if not ret:
                    self.logger.warning(f"Failed to read frame from {device_id}, attempting reconnection...")
                    await asyncio.sleep(pipeline.config.reconnect_delay_seconds)
                    
                    # Try to reconnect
                    stream.release()
                    stream.open(stream.getBackendName())  # Reopen with same URL
                    continue
                
                # Process frame
                result = pipeline.process_frame(frame)
                
                # Calculate sleep time to maintain target FPS
                processing_time = time.perf_counter() - loop_start
                sleep_time = max(0, target_frame_time - processing_time)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                elif processing_time > target_frame_time * 1.5:  # 50% over target
                    self.logger.warning(
                        f"Processing too slow for {device_id}: "
                        f"{processing_time*1000:.1f}ms (target: {target_frame_time*1000:.1f}ms)"
                    )
        
        except asyncio.CancelledError:
            self.logger.info(f"Stream processing cancelled for {device_id}")
        except Exception as e:
            self.logger.error(f"Stream processing error for {device_id}: {e}")
            # Could implement auto-restart logic here
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all camera streams."""
        return {
            device_id: pipeline.get_status()
            for device_id, pipeline in self.pipelines.items()
        }
    
    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics across all streams."""
        total_frames = sum(p.metrics.frames_processed for p in self.pipelines.values())
        total_detections = sum(p.metrics.detections_count for p in self.pipelines.values())
        total_violations = sum(p.metrics.violations_count for p in self.pipelines.values())
        total_errors = sum(p.metrics.errors_count for p in self.pipelines.values())
        
        avg_fps = sum(p.metrics.fps for p in self.pipelines.values()) / len(self.pipelines) if self.pipelines else 0
        avg_latency = sum(p.metrics.avg_latency_ms for p in self.pipelines.values()) / len(self.pipelines) if self.pipelines else 0
        
        return {
            "total_streams": len(self.pipelines),
            "active_streams": len(self.processing_tasks),
            "total_frames_processed": total_frames,
            "total_detections": total_detections,
            "total_violations": total_violations,
            "total_errors": total_errors,
            "average_fps": avg_fps,
            "average_latency_ms": avg_latency,
            "streams": list(self.pipelines.keys())
        }