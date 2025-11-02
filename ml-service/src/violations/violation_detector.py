"""
Traffic Violation Detector.

This module provides comprehensive traffic violation detection including
speed violations, lane violations, wrong-way driving, and other traffic infractions.
"""

import logging
import time
import numpy as np
import cv2
from typing import List, Dict, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from pathlib import Path

from ..speed.speed_analyzer import SpeedViolation, ViolationEvent as SpeedViolationEvent
from ..tracking.vehicle_tracker import TrackedVehicle
from ..detection.vehicle_detector import Detection

logger = logging.getLogger(__name__)

class ViolationType(Enum):
    """Types of traffic violations."""
    SPEED_VIOLATION = "speed_violation"
    LANE_VIOLATION = "lane_violation"
    WRONG_WAY = "wrong_way"
    RED_LIGHT = "red_light"
    STOP_SIGN = "stop_sign"
    ILLEGAL_TURN = "illegal_turn"
    PARKING_VIOLATION = "parking_violation"
    FOLLOWING_DISTANCE = "following_distance"

class ViolationSeverity(Enum):
    """Severity levels for violations."""
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"

@dataclass
class ViolationLocation:
    """Location information for a violation."""
    zone_id: str
    zone_name: str
    coordinates: Tuple[float, float]  # lat, lon or x, y
    address: Optional[str] = None
    landmark: Optional[str] = None

@dataclass
class TrafficViolation:
    """Complete traffic violation record."""
    violation_id: str
    timestamp: float
    violation_type: ViolationType
    severity: ViolationSeverity
    vehicle_id: int
    description: str
    confidence: float
    
    # Location and context
    location: ViolationLocation
    speed_limit: Optional[float] = None
    measured_speed: Optional[float] = None
    
    # Evidence
    evidence_frame: Optional[np.ndarray] = None
    vehicle_crop: Optional[np.ndarray] = None
    license_plate: Optional[str] = None
    plate_confidence: Optional[float] = None
    
    # Technical details
    detection_confidence: float = 0.0
    tracking_quality: float = 0.0
    weather_conditions: Optional[str] = None
    lighting_conditions: Optional[str] = None
    
    # Metadata
    camera_id: Optional[str] = None
    processed_by: str = "automated_system"
    reviewed: bool = False
    false_positive: bool = False

@dataclass
class ViolationRule:
    """Rule definition for violation detection."""
    rule_id: str
    violation_type: ViolationType
    enabled: bool
    parameters: Dict[str, Any]
    zones: List[str]  # Zone IDs where rule applies
    time_restrictions: Optional[Dict[str, Any]] = None
    vehicle_types: Optional[List[str]] = None

class ViolationDetector:
    """
    Comprehensive traffic violation detector.
    
    Features:
    - Multi-type violation detection
    - Configurable rules and thresholds
    - Evidence collection and validation
    - Integration with speed and lane detection
    - Real-time and batch processing
    """
    
    def __init__(self):
        """Initialize violation detector."""
        self.violations: List[TrafficViolation] = []
        self.violation_rules: Dict[str, ViolationRule] = {}
        self.active_violations: Dict[int, List[str]] = {}  # vehicle_id -> violation_ids
        self.violation_cooldowns: Dict[Tuple[int, ViolationType], float] = {}
        
        # Configuration
        self.cooldown_periods = {
            ViolationType.SPEED_VIOLATION: 30.0,      # 30 seconds
            ViolationType.LANE_VIOLATION: 15.0,       # 15 seconds
            ViolationType.WRONG_WAY: 60.0,            # 60 seconds
            ViolationType.RED_LIGHT: 120.0,           # 2 minutes
            ViolationType.STOP_SIGN: 60.0,            # 60 seconds
            ViolationType.ILLEGAL_TURN: 45.0,         # 45 seconds
            ViolationType.PARKING_VIOLATION: 300.0,   # 5 minutes
            ViolationType.FOLLOWING_DISTANCE: 20.0    # 20 seconds
        }
        
        # Severity thresholds
        self.severity_thresholds = {
            ViolationType.SPEED_VIOLATION: {
                ViolationSeverity.MINOR: 10.0,     # 10 km/h over
                ViolationSeverity.MODERATE: 20.0,  # 20 km/h over
                ViolationSeverity.SEVERE: 40.0,    # 40 km/h over
                ViolationSeverity.CRITICAL: 60.0   # 60 km/h over
            },
            ViolationType.LANE_VIOLATION: {
                ViolationSeverity.MINOR: 0.3,      # 30% overlap
                ViolationSeverity.MODERATE: 0.5,   # 50% overlap
                ViolationSeverity.SEVERE: 0.8,     # 80% overlap
                ViolationSeverity.CRITICAL: 1.0    # Complete lane change
            }
        }
        
        # Statistics
        self.stats = {
            "total_violations": 0,
            "violations_by_type": {vt: 0 for vt in ViolationType},
            "violations_by_severity": {vs: 0 for vs in ViolationSeverity},
            "false_positives": 0,
            "processing_times": []
        }
        
        logger.info("ViolationDetector initialized")
    
    def add_violation_rule(self, rule: ViolationRule):
        """Add a violation detection rule."""
        self.violation_rules[rule.rule_id] = rule
        logger.info(f"Added violation rule: {rule.rule_id} for {rule.violation_type.value}")
    
    def remove_violation_rule(self, rule_id: str):
        """Remove a violation detection rule."""
        if rule_id in self.violation_rules:
            del self.violation_rules[rule_id]
            logger.info(f"Removed violation rule: {rule_id}")
    
    def detect_speed_violations(self, speed_violations: List[SpeedViolation], 
                              vehicles: List[TrackedVehicle], frame: np.ndarray) -> List[TrafficViolation]:
        """
        Process speed violations from speed analyzer.
        
        Args:
            speed_violations: Speed violations from speed analyzer
            vehicles: Currently tracked vehicles
            frame: Current frame
            
        Returns:
            List of processed traffic violations
        """
        traffic_violations = []
        
        for speed_violation in speed_violations:
            # Check cooldown
            cooldown_key = (speed_violation.vehicle_id, ViolationType.SPEED_VIOLATION)
            if self._is_in_cooldown(cooldown_key):
                continue
            
            # Find corresponding vehicle
            vehicle = next((v for v in vehicles if v.track_id == speed_violation.vehicle_id), None)
            if not vehicle:
                continue
            
            # Determine severity
            over_limit = speed_violation.violation_amount
            severity = self._calculate_speed_severity(over_limit)
            
            # Create location
            location = ViolationLocation(
                zone_id=speed_violation.measurement_zone,
                zone_name=speed_violation.measurement_zone,
                coordinates=(vehicle.center_x, vehicle.center_y)
            )
            
            # Extract evidence
            x1, y1, x2, y2 = vehicle.bbox
            vehicle_crop = frame[y1:y2, x1:x2].copy()
            
            # Create violation record
            violation = TrafficViolation(
                violation_id=str(uuid.uuid4()),
                timestamp=speed_violation.timestamp,
                violation_type=ViolationType.SPEED_VIOLATION,
                severity=severity,
                vehicle_id=speed_violation.vehicle_id,
                description=f"Speed violation: {speed_violation.measured_speed:.1f} km/h in {speed_violation.speed_limit:.1f} km/h zone",
                confidence=speed_violation.confidence,
                location=location,
                speed_limit=speed_violation.speed_limit,
                measured_speed=speed_violation.measured_speed,
                evidence_frame=frame.copy(),
                vehicle_crop=vehicle_crop,
                detection_confidence=vehicle.confidence,
                tracking_quality=vehicle.confidence
            )
            
            traffic_violations.append(violation)
            self._set_cooldown(cooldown_key)
            
            logger.info(f"Speed violation detected: Vehicle {speed_violation.vehicle_id} "
                       f"at {speed_violation.measured_speed:.1f} km/h")
        
        return traffic_violations
    
    def detect_lane_violations(self, vehicles: List[TrackedVehicle], lane_mask: np.ndarray, 
                             frame: np.ndarray) -> List[TrafficViolation]:
        """
        Detect lane violations using vehicle positions and lane masks.
        
        Args:
            vehicles: Currently tracked vehicles
            lane_mask: Binary mask of valid lanes
            frame: Current frame
            
        Returns:
            List of lane violations
        """
        violations = []
        
        for vehicle in vehicles:
            # Check cooldown
            cooldown_key = (vehicle.track_id, ViolationType.LANE_VIOLATION)
            if self._is_in_cooldown(cooldown_key):
                continue
            
            # Check if vehicle is in valid lane area
            x1, y1, x2, y2 = vehicle.bbox
            vehicle_mask = np.zeros(lane_mask.shape, dtype=np.uint8)
            vehicle_mask[y1:y2, x1:x2] = 255
            
            # Calculate overlap with valid lanes
            overlap = cv2.bitwise_and(vehicle_mask, lane_mask)
            vehicle_area = np.sum(vehicle_mask > 0)
            overlap_area = np.sum(overlap > 0)
            
            if vehicle_area > 0:
                overlap_ratio = overlap_area / vehicle_area
                
                # Check if violation (low overlap with valid lanes)
                if overlap_ratio < 0.7:  # 70% threshold for valid lane position
                    violation_amount = 1.0 - overlap_ratio
                    severity = self._calculate_lane_severity(violation_amount)
                    
                    location = ViolationLocation(
                        zone_id="main_road",
                        zone_name="Main Road",
                        coordinates=(vehicle.center_x, vehicle.center_y)
                    )
                    
                    vehicle_crop = frame[y1:y2, x1:x2].copy()
                    
                    violation = TrafficViolation(
                        violation_id=str(uuid.uuid4()),
                        timestamp=time.time(),
                        violation_type=ViolationType.LANE_VIOLATION,
                        severity=severity,
                        vehicle_id=vehicle.track_id,
                        description=f"Lane violation: {violation_amount*100:.1f}% outside valid lanes",
                        confidence=0.8,  # Lane detection confidence
                        location=location,
                        evidence_frame=frame.copy(),
                        vehicle_crop=vehicle_crop,
                        detection_confidence=vehicle.confidence,
                        tracking_quality=vehicle.confidence
                    )
                    
                    violations.append(violation)
                    self._set_cooldown(cooldown_key)
                    
                    logger.info(f"Lane violation detected: Vehicle {vehicle.track_id}")
        
        return violations
    
    def detect_wrong_way_driving(self, vehicles: List[TrackedVehicle], 
                                expected_direction: np.ndarray, frame: np.ndarray) -> List[TrafficViolation]:
        """
        Detect wrong-way driving using vehicle trajectories.
        
        Args:
            vehicles: Currently tracked vehicles
            expected_direction: Expected traffic direction vector
            frame: Current frame
            
        Returns:
            List of wrong-way violations
        """
        violations = []
        
        for vehicle in vehicles:
            # Skip if not enough trajectory data
            if len(vehicle.trajectory) < 5:
                continue
            
            # Check cooldown
            cooldown_key = (vehicle.track_id, ViolationType.WRONG_WAY)
            if self._is_in_cooldown(cooldown_key):
                continue
            
            # Calculate vehicle direction from recent trajectory
            recent_positions = vehicle.trajectory[-5:]
            if len(recent_positions) >= 2:
                start_pos = recent_positions[0]
                end_pos = recent_positions[-1]
                
                vehicle_direction = np.array([
                    end_pos[0] - start_pos[0],
                    end_pos[1] - start_pos[1]
                ])
                
                # Normalize directions
                if np.linalg.norm(vehicle_direction) > 0:
                    vehicle_direction = vehicle_direction / np.linalg.norm(vehicle_direction)
                    
                    # Calculate angle difference
                    dot_product = np.dot(vehicle_direction, expected_direction)
                    angle_diff = np.arccos(np.clip(dot_product, -1.0, 1.0))
                    
                    # Check if driving in wrong direction (angle > 90 degrees)
                    if angle_diff > np.pi / 2:
                        x1, y1, x2, y2 = vehicle.bbox
                        
                        location = ViolationLocation(
                            zone_id="main_road",
                            zone_name="Main Road",
                            coordinates=(vehicle.center_x, vehicle.center_y)
                        )
                        
                        vehicle_crop = frame[y1:y2, x1:x2].copy()
                        
                        violation = TrafficViolation(
                            violation_id=str(uuid.uuid4()),
                            timestamp=time.time(),
                            violation_type=ViolationType.WRONG_WAY,
                            severity=ViolationSeverity.CRITICAL,  # Wrong way is always critical
                            vehicle_id=vehicle.track_id,
                            description=f"Wrong-way driving detected (angle: {np.degrees(angle_diff):.1f}°)",
                            confidence=0.9,
                            location=location,
                            evidence_frame=frame.copy(),
                            vehicle_crop=vehicle_crop,
                            detection_confidence=vehicle.confidence,
                            tracking_quality=vehicle.confidence
                        )
                        
                        violations.append(violation)
                        self._set_cooldown(cooldown_key)
                        
                        logger.warning(f"Wrong-way driving detected: Vehicle {vehicle.track_id}")
        
        return violations
    
    def detect_following_distance_violations(self, vehicles: List[TrackedVehicle], 
                                           frame: np.ndarray, min_distance: float = 20.0) -> List[TrafficViolation]:
        """
        Detect vehicles following too closely.
        
        Args:
            vehicles: Currently tracked vehicles
            frame: Current frame
            min_distance: Minimum safe following distance in meters
            
        Returns:
            List of following distance violations
        """
        violations = []
        
        # Sort vehicles by position to find following pairs
        vehicles_sorted = sorted(vehicles, key=lambda v: v.center_y, reverse=True)
        
        for i in range(len(vehicles_sorted) - 1):
            vehicle1 = vehicles_sorted[i]
            vehicle2 = vehicles_sorted[i + 1]
            
            # Check if vehicles are in same lane (similar x position)
            x_diff = abs(vehicle1.center_x - vehicle2.center_x)
            if x_diff < 100:  # pixels - adjust based on camera setup
                # Calculate distance between vehicles
                distance = abs(vehicle1.center_y - vehicle2.center_y)
                
                # Convert to real-world distance (approximate)
                # This would need camera calibration for accuracy
                real_distance = distance * 0.1  # rough conversion factor
                
                if real_distance < min_distance:
                    # Check cooldown
                    cooldown_key = (vehicle1.track_id, ViolationType.FOLLOWING_DISTANCE)
                    if self._is_in_cooldown(cooldown_key):
                        continue
                    
                    severity = ViolationSeverity.MODERATE
                    if real_distance < min_distance * 0.5:
                        severity = ViolationSeverity.SEVERE
                    if real_distance < min_distance * 0.3:
                        severity = ViolationSeverity.CRITICAL
                    
                    x1, y1, x2, y2 = vehicle1.bbox
                    
                    location = ViolationLocation(
                        zone_id="main_road",
                        zone_name="Main Road",
                        coordinates=(vehicle1.center_x, vehicle1.center_y)
                    )
                    
                    vehicle_crop = frame[y1:y2, x1:x2].copy()
                    
                    violation = TrafficViolation(
                        violation_id=str(uuid.uuid4()),
                        timestamp=time.time(),
                        violation_type=ViolationType.FOLLOWING_DISTANCE,
                        severity=severity,
                        vehicle_id=vehicle1.track_id,
                        description=f"Following too closely: {real_distance:.1f}m (min: {min_distance:.1f}m)",
                        confidence=0.7,
                        location=location,
                        evidence_frame=frame.copy(),
                        vehicle_crop=vehicle_crop,
                        detection_confidence=vehicle1.confidence,
                        tracking_quality=vehicle1.confidence
                    )
                    
                    violations.append(violation)
                    self._set_cooldown(cooldown_key)
                    
                    logger.info(f"Following distance violation: Vehicle {vehicle1.track_id}")
        
        return violations
    
    def process_violations(self, violations: List[TrafficViolation]):
        """Process and store detected violations."""
        for violation in violations:
            # Add to active violations
            if violation.vehicle_id not in self.active_violations:
                self.active_violations[violation.vehicle_id] = []
            self.active_violations[violation.vehicle_id].append(violation.violation_id)
            
            # Store violation
            self.violations.append(violation)
            
            # Update statistics
            self._update_statistics(violation)
            
            logger.info(f"Processed violation: {violation.violation_id} "
                       f"({violation.violation_type.value}, {violation.severity.value})")
    
    def _calculate_speed_severity(self, over_limit: float) -> ViolationSeverity:
        """Calculate severity for speed violations."""
        thresholds = self.severity_thresholds[ViolationType.SPEED_VIOLATION]
        
        if over_limit >= thresholds[ViolationSeverity.CRITICAL]:
            return ViolationSeverity.CRITICAL
        elif over_limit >= thresholds[ViolationSeverity.SEVERE]:
            return ViolationSeverity.SEVERE
        elif over_limit >= thresholds[ViolationSeverity.MODERATE]:
            return ViolationSeverity.MODERATE
        else:
            return ViolationSeverity.MINOR
    
    def _calculate_lane_severity(self, violation_amount: float) -> ViolationSeverity:
        """Calculate severity for lane violations."""
        thresholds = self.severity_thresholds[ViolationType.LANE_VIOLATION]
        
        if violation_amount >= thresholds[ViolationSeverity.CRITICAL]:
            return ViolationSeverity.CRITICAL
        elif violation_amount >= thresholds[ViolationSeverity.SEVERE]:
            return ViolationSeverity.SEVERE
        elif violation_amount >= thresholds[ViolationSeverity.MODERATE]:
            return ViolationSeverity.MODERATE
        else:
            return ViolationSeverity.MINOR
    
    def _is_in_cooldown(self, key: Tuple[int, ViolationType]) -> bool:
        """Check if violation type is in cooldown for vehicle."""
        if key not in self.violation_cooldowns:
            return False
        
        cooldown_period = self.cooldown_periods[key[1]]
        elapsed = time.time() - self.violation_cooldowns[key]
        
        return elapsed < cooldown_period
    
    def _set_cooldown(self, key: Tuple[int, ViolationType]):
        """Set cooldown for violation type and vehicle."""
        self.violation_cooldowns[key] = time.time()
    
    def _update_statistics(self, violation: TrafficViolation):
        """Update violation statistics."""
        self.stats["total_violations"] += 1
        self.stats["violations_by_type"][violation.violation_type] += 1
        self.stats["violations_by_severity"][violation.severity] += 1
    
    def get_violations_by_vehicle(self, vehicle_id: int) -> List[TrafficViolation]:
        """Get all violations for a specific vehicle."""
        return [v for v in self.violations if v.vehicle_id == vehicle_id]
    
    def get_violations_by_type(self, violation_type: ViolationType) -> List[TrafficViolation]:
        """Get all violations of a specific type."""
        return [v for v in self.violations if v.violation_type == violation_type]
    
    def get_violations_in_timerange(self, start_time: float, end_time: float) -> List[TrafficViolation]:
        """Get violations within a time range."""
        return [v for v in self.violations if start_time <= v.timestamp <= end_time]
    
    def mark_false_positive(self, violation_id: str):
        """Mark a violation as false positive."""
        for violation in self.violations:
            if violation.violation_id == violation_id:
                violation.false_positive = True
                self.stats["false_positives"] += 1
                logger.info(f"Marked violation {violation_id} as false positive")
                break
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive violation statistics."""
        return {
            "total_violations": self.stats["total_violations"],
            "violations_by_type": {vt.value: count for vt, count in self.stats["violations_by_type"].items()},
            "violations_by_severity": {vs.value: count for vs, count in self.stats["violations_by_severity"].items()},
            "false_positive_rate": self.stats["false_positives"] / max(1, self.stats["total_violations"]),
            "active_violations": len(self.active_violations),
            "total_rules": len(self.violation_rules),
            "enabled_rules": len([r for r in self.violation_rules.values() if r.enabled])
        }
    
    def cleanup_old_violations(self, max_age: float = 3600.0):
        """Clean up old violations to free memory."""
        current_time = time.time()
        
        # Remove old violations
        initial_count = len(self.violations)
        self.violations = [v for v in self.violations if (current_time - v.timestamp) <= max_age]
        removed_count = initial_count - len(self.violations)
        
        # Clean up active violations
        for vehicle_id in list(self.active_violations.keys()):
            self.active_violations[vehicle_id] = [
                vid for vid in self.active_violations[vehicle_id]
                if any(v.violation_id == vid and (current_time - v.timestamp) <= max_age 
                      for v in self.violations)
            ]
            if not self.active_violations[vehicle_id]:
                del self.active_violations[vehicle_id]
        
        # Clean up cooldowns
        initial_cooldowns = len(self.violation_cooldowns)
        self.violation_cooldowns = {
            k: v for k, v in self.violation_cooldowns.items()
            if (current_time - v) <= max(self.cooldown_periods.values())
        }
        removed_cooldowns = initial_cooldowns - len(self.violation_cooldowns)
        
        if removed_count > 0 or removed_cooldowns > 0:
            logger.info(f"Cleaned up {removed_count} old violations and {removed_cooldowns} expired cooldowns")