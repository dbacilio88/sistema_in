"""
Speed Analyzer for comprehensive speed violation detection.

This module provides high-level speed analysis combining detection,
tracking, and speed calculation for traffic violation detection.
"""

import logging
import numpy as np
import cv2
from typing import List, Tuple, Optional, Dict, Any, Set
from dataclasses import dataclass, asdict
import time
import json
from enum import Enum
from pathlib import Path

from ..detection.vehicle_detector import YOLOv8VehicleDetector, Detection
from ..tracking.vehicle_tracker import VehicleTracker, TrackedVehicle
from ..tracking.trajectory import TrajectoryManager
from .camera_calibrator import CameraCalibrator, CalibrationZone
from .speed_calculator import SpeedCalculator, SpeedMeasurement, SpeedViolation

logger = logging.getLogger(__name__)

class AnalysisMode(Enum):
    """Speed analysis operating modes."""
    REALTIME = "realtime"      # Real-time processing
    BATCH = "batch"            # Batch processing of video
    CALIBRATION = "calibration"  # Calibration mode

@dataclass
class ViolationEvent:
    """Complete violation event with all evidence."""
    event_id: str
    timestamp: float
    vehicle_id: int
    violation: SpeedViolation
    speed_measurement: SpeedMeasurement
    detection_box: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    vehicle_crop: np.ndarray
    full_frame: np.ndarray
    license_plate: Optional[str] = None
    plate_confidence: Optional[float] = None
    tracking_quality: float = 0.0

@dataclass
class AnalysisResult:
    """Complete analysis result for a frame."""
    frame_id: int
    timestamp: float
    detections: List[Detection]
    tracked_vehicles: List[TrackedVehicle]
    speed_measurements: List[SpeedMeasurement]
    violations: List[ViolationEvent]
    processing_time: float
    fps: float

class SpeedAnalyzer:
    """
    Comprehensive speed analyzer for traffic violation detection.
    
    Features:
    - End-to-end speed violation detection
    - Real-time and batch processing modes
    - Evidence collection and storage
    - Performance monitoring
    - Configurable violation thresholds
    - Multi-zone speed enforcement
    """
    
    def __init__(self, detector: YOLOv8VehicleDetector, tracker: VehicleTracker, 
                 calibrator: CameraCalibrator, mode: AnalysisMode = AnalysisMode.REALTIME):
        """
        Initialize speed analyzer.
        
        Args:
            detector: Vehicle detector instance
            tracker: Vehicle tracker instance
            calibrator: Camera calibrator instance
            mode: Analysis mode
        """
        self.detector = detector
        self.tracker = tracker
        self.calibrator = calibrator
        self.mode = mode
        
        self.speed_calculator = SpeedCalculator(calibrator)
        self.trajectory_manager = TrajectoryManager()
        
        # Analysis state
        self.frame_count = 0
        self.start_time = time.time()
        self.violation_events: List[ViolationEvent] = []
        self.processing_times: List[float] = []
        
        # Configuration
        self.min_tracking_frames = 10    # Minimum frames for speed calculation
        self.violation_cooldown = 30.0   # Seconds between violations for same vehicle
        self.save_evidence = True        # Save violation evidence
        self.evidence_dir = Path("evidence")
        
        # Performance tracking
        self.performance_stats = {
            "total_frames": 0,
            "total_detections": 0,
            "total_tracks": 0,
            "total_violations": 0,
            "average_fps": 0.0,
            "average_processing_time": 0.0
        }
        
        # Create evidence directory
        if self.save_evidence:
            self.evidence_dir.mkdir(exist_ok=True)
        
        logger.info(f"SpeedAnalyzer initialized in {mode.value} mode")
    
    def analyze_frame(self, frame: np.ndarray, timestamp: Optional[float] = None) -> AnalysisResult:
        """
        Analyze a single frame for speed violations.
        
        Args:
            frame: Input frame
            timestamp: Frame timestamp (current time if None)
            
        Returns:
            Analysis result
        """
        if timestamp is None:
            timestamp = time.time()
        
        start_time = time.time()
        
        try:
            # Step 1: Detect vehicles
            detections = self.detector.detect(frame)
            
            # Step 2: Update tracking
            tracked_vehicles = self.tracker.update(detections, timestamp)
            
            # Step 3: Update trajectories
            for vehicle in tracked_vehicles:
                trajectory = self.trajectory_manager.get_trajectory(vehicle.track_id)
                if trajectory:
                    self.trajectory_manager.add_position(
                        vehicle.track_id, 
                        (int(vehicle.center_x), int(vehicle.center_y)), 
                        timestamp
                    )
            
            # Step 4: Calculate speeds for stable tracks
            speed_measurements = []
            for vehicle in tracked_vehicles:
                if vehicle.consecutive_frames >= self.min_tracking_frames:
                    trajectory = self.trajectory_manager.get_trajectory(vehicle.track_id)
                    if trajectory and len(trajectory.positions) >= 5:
                        measurement = self.speed_calculator.calculate_speed_from_trajectory(trajectory)
                        if measurement:
                            speed_measurements.append(measurement)
            
            # Step 5: Detect violations
            violations = []
            for measurement in speed_measurements:
                violation = self.speed_calculator.detect_speed_violation(measurement)
                if violation and self._should_process_violation(violation):
                    # Create violation event
                    vehicle = next((v for v in tracked_vehicles if v.track_id == violation.vehicle_id), None)
                    if vehicle:
                        event = self._create_violation_event(violation, measurement, vehicle, frame, timestamp)
                        violations.append(event)
                        self.violation_events.append(event)
            
            # Step 6: Calculate performance metrics
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)
            
            # Keep only recent processing times for FPS calculation
            if len(self.processing_times) > 30:
                self.processing_times = self.processing_times[-30:]
            
            fps = 1.0 / processing_time if processing_time > 0 else 0.0
            
            # Update statistics
            self._update_performance_stats(detections, tracked_vehicles, violations, processing_time, fps)
            
            result = AnalysisResult(
                frame_id=self.frame_count,
                timestamp=timestamp,
                detections=detections,
                tracked_vehicles=tracked_vehicles,
                speed_measurements=speed_measurements,
                violations=violations,
                processing_time=processing_time,
                fps=fps
            )
            
            self.frame_count += 1
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze frame: {e}")
            return AnalysisResult(
                frame_id=self.frame_count,
                timestamp=timestamp,
                detections=[],
                tracked_vehicles=[],
                speed_measurements=[],
                violations=[],
                processing_time=time.time() - start_time,
                fps=0.0
            )
    
    def _should_process_violation(self, violation: SpeedViolation) -> bool:
        """Check if violation should be processed (not duplicate)."""
        current_time = time.time()
        
        # Check for recent violations from the same vehicle
        for event in self.violation_events:
            if (event.vehicle_id == violation.vehicle_id and 
                (current_time - event.timestamp) < self.violation_cooldown):
                return False
        
        return True
    
    def _create_violation_event(self, violation: SpeedViolation, measurement: SpeedMeasurement, 
                               vehicle: TrackedVehicle, frame: np.ndarray, timestamp: float) -> ViolationEvent:
        """Create a complete violation event with evidence."""
        event_id = f"violation_{int(timestamp)}_{violation.vehicle_id}"
        
        # Extract vehicle crop
        x1, y1, x2, y2 = vehicle.bbox
        vehicle_crop = frame[y1:y2, x1:x2].copy()
        
        # Create violation event
        event = ViolationEvent(
            event_id=event_id,
            timestamp=timestamp,
            vehicle_id=violation.vehicle_id,
            violation=violation,
            speed_measurement=measurement,
            detection_box=(x1, y1, x2, y2),
            vehicle_crop=vehicle_crop,
            full_frame=frame.copy(),
            tracking_quality=vehicle.confidence
        )
        
        # Save evidence if enabled
        if self.save_evidence:
            self._save_violation_evidence(event)
        
        logger.warning(f"Violation event created: {event_id} - "
                      f"{violation.measured_speed:.1f} km/h in {violation.speed_limit} km/h zone")
        
        return event
    
    def _save_violation_evidence(self, event: ViolationEvent):
        """Save violation evidence to disk."""
        try:
            event_dir = self.evidence_dir / event.event_id
            event_dir.mkdir(exist_ok=True)
            
            # Save full frame
            full_frame_path = event_dir / "full_frame.jpg"
            cv2.imwrite(str(full_frame_path), event.full_frame)
            
            # Save vehicle crop
            vehicle_crop_path = event_dir / "vehicle_crop.jpg"
            cv2.imwrite(str(vehicle_crop_path), event.vehicle_crop)
            
            # Save annotated frame
            annotated_frame = self._create_annotated_frame(event)
            annotated_path = event_dir / "annotated_frame.jpg"
            cv2.imwrite(str(annotated_path), annotated_frame)
            
            # Save event metadata
            metadata = {
                "event_id": event.event_id,
                "timestamp": event.timestamp,
                "vehicle_id": event.vehicle_id,
                "violation": asdict(event.violation),
                "speed_measurement": asdict(event.speed_measurement),
                "detection_box": event.detection_box,
                "tracking_quality": event.tracking_quality,
                "license_plate": event.license_plate,
                "plate_confidence": event.plate_confidence
            }
            
            metadata_path = event_dir / "metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            logger.info(f"Violation evidence saved to {event_dir}")
            
        except Exception as e:
            logger.error(f"Failed to save violation evidence: {e}")
    
    def _create_annotated_frame(self, event: ViolationEvent) -> np.ndarray:
        """Create annotated frame showing violation details."""
        frame = event.full_frame.copy()
        
        # Draw detection box
        x1, y1, x2, y2 = event.detection_box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
        
        # Add violation information
        violation_text = [
            f"VIOLATION: Vehicle {event.vehicle_id}",
            f"Speed: {event.violation.measured_speed:.1f} km/h",
            f"Limit: {event.violation.speed_limit:.1f} km/h",
            f"Over by: {event.violation.violation_amount:.1f} km/h",
            f"Zone: {event.violation.measurement_zone}",
            f"Confidence: {event.violation.confidence:.2f}"
        ]
        
        # Draw text background
        text_y = y1 - 10
        for i, text in enumerate(violation_text):
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(frame, (x1, text_y - text_size[1] - 5), 
                         (x1 + text_size[0] + 10, text_y + 5), (0, 0, 0), -1)
            cv2.putText(frame, text, (x1 + 5, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            text_y -= (text_size[1] + 10)
        
        # Draw trajectory if available
        trajectory = self.trajectory_manager.get_trajectory(event.vehicle_id)
        if trajectory and len(trajectory.positions) > 1:
            points = np.array(trajectory.positions[-20:], dtype=np.int32)  # Last 20 points
            cv2.polylines(frame, [points], False, (255, 255, 0), 2)
            
            # Mark entry and exit points
            if len(event.speed_measurement.pixel_trajectory) >= 2:
                entry = event.speed_measurement.pixel_trajectory[0]
                exit_point = event.speed_measurement.pixel_trajectory[-1]
                cv2.circle(frame, entry, 8, (0, 255, 0), -1)  # Green for entry
                cv2.circle(frame, exit_point, 8, (0, 0, 255), -1)  # Red for exit
        
        # Add timestamp
        timestamp_text = f"Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event.timestamp))}"
        cv2.putText(frame, timestamp_text, (10, frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame
    
    def _update_performance_stats(self, detections: List[Detection], tracked_vehicles: List[TrackedVehicle],
                                 violations: List[ViolationEvent], processing_time: float, fps: float):
        """Update performance statistics."""
        self.performance_stats["total_frames"] += 1
        self.performance_stats["total_detections"] += len(detections)
        self.performance_stats["total_tracks"] += len(tracked_vehicles)
        self.performance_stats["total_violations"] += len(violations)
        
        # Update running averages
        total_frames = self.performance_stats["total_frames"]
        self.performance_stats["average_fps"] = (
            (self.performance_stats["average_fps"] * (total_frames - 1) + fps) / total_frames
        )
        self.performance_stats["average_processing_time"] = (
            (self.performance_stats["average_processing_time"] * (total_frames - 1) + processing_time) / total_frames
        )
    
    def get_recent_violations(self, minutes: int = 60) -> List[ViolationEvent]:
        """Get violations from the last N minutes."""
        current_time = time.time()
        cutoff_time = current_time - (minutes * 60)
        
        return [event for event in self.violation_events if event.timestamp >= cutoff_time]
    
    def get_zone_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics by calibration zone."""
        zone_stats = {}
        
        for zone_id, zone in self.calibrator.calibration_zones.items():
            zone_violations = [
                event for event in self.violation_events 
                if event.violation.measurement_zone == zone_id
            ]
            
            if zone_violations:
                speeds = [event.violation.measured_speed for event in zone_violations]
                zone_stats[zone_id] = {
                    "zone_name": zone.name,
                    "speed_limit": zone.speed_limit,
                    "total_violations": len(zone_violations),
                    "average_violation_speed": np.mean(speeds),
                    "max_violation_speed": max(speeds),
                    "average_over_limit": np.mean([event.violation.violation_amount for event in zone_violations])
                }
            else:
                zone_stats[zone_id] = {
                    "zone_name": zone.name,
                    "speed_limit": zone.speed_limit,
                    "total_violations": 0,
                    "average_violation_speed": 0.0,
                    "max_violation_speed": 0.0,
                    "average_over_limit": 0.0
                }
        
        return zone_stats
    
    def export_violations_report(self, filepath: str) -> bool:
        """Export violations report to JSON file."""
        try:
            report = {
                "generation_time": time.time(),
                "analysis_period": {
                    "start_time": self.start_time,
                    "end_time": time.time(),
                    "duration_hours": (time.time() - self.start_time) / 3600
                },
                "performance_stats": self.performance_stats,
                "zone_statistics": self.get_zone_statistics(),
                "violations": [
                    {
                        "event_id": event.event_id,
                        "timestamp": event.timestamp,
                        "vehicle_id": event.vehicle_id,
                        "measured_speed": event.violation.measured_speed,
                        "speed_limit": event.violation.speed_limit,
                        "violation_amount": event.violation.violation_amount,
                        "measurement_zone": event.violation.measurement_zone,
                        "confidence": event.violation.confidence,
                        "license_plate": event.license_plate
                    }
                    for event in self.violation_events
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Violations report exported to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export violations report: {e}")
            return False
    
    def reset_analysis(self):
        """Reset analysis state (clear violations and statistics)."""
        self.violation_events.clear()
        self.processing_times.clear()
        self.frame_count = 0
        self.start_time = time.time()
        
        self.performance_stats = {
            "total_frames": 0,
            "total_detections": 0,
            "total_tracks": 0,
            "total_violations": 0,
            "average_fps": 0.0,
            "average_processing_time": 0.0
        }
        
        # Clear old measurements
        self.speed_calculator.clear_old_measurements(max_age=0)
        
        logger.info("Analysis state reset")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        current_time = time.time()
        session_duration = current_time - self.start_time
        
        return {
            "session_duration_minutes": session_duration / 60,
            "total_frames_processed": self.frame_count,
            "performance_stats": self.performance_stats,
            "recent_fps": 1.0 / np.mean(self.processing_times[-10:]) if len(self.processing_times) >= 10 else 0.0,
            "memory_usage": {
                "violation_events": len(self.violation_events),
                "tracked_trajectories": len(self.trajectory_manager.trajectories),
                "speed_measurements": sum(len(measurements) for measurements in self.speed_calculator.speed_measurements.values())
            },
            "calibration_status": {
                "is_calibrated": self.calibrator.is_calibrated,
                "calibration_error": self.calibrator.calibration_error,
                "confidence_score": self.calibrator.confidence_score,
                "num_zones": len(self.calibrator.calibration_zones)
            }
        }