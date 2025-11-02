"""
Speed Calculator for traffic violation detection.

This module calculates vehicle speeds from tracking data using
camera calibration and trajectory analysis.
"""

import logging
import numpy as np
import cv2
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import time
import math

from ..tracking.trajectory import Trajectory
from .camera_calibrator import CameraCalibrator, CalibrationZone

logger = logging.getLogger(__name__)

class SpeedUnit(Enum):
    """Speed measurement units."""
    KMH = "km/h"
    MPH = "mph"
    MPS = "m/s"

@dataclass
class SpeedMeasurement:
    """Single speed measurement result."""
    vehicle_id: int
    timestamp: float
    speed_kmh: float
    speed_mps: float
    distance_traveled: float  # meters
    time_elapsed: float  # seconds
    measurement_zone: str
    confidence: float
    entry_point: Tuple[float, float]  # real-world coordinates
    exit_point: Tuple[float, float]   # real-world coordinates
    entry_time: float
    exit_time: float
    pixel_trajectory: List[Tuple[int, int]]  # pixel coordinates path
    real_trajectory: List[Tuple[float, float]]  # real-world coordinates path

@dataclass
class SpeedViolation:
    """Speed violation detection result."""
    vehicle_id: int
    timestamp: float
    measured_speed: float  # km/h
    speed_limit: float     # km/h
    violation_amount: float  # km/h over limit
    violation_percentage: float  # percentage over limit
    measurement_zone: str
    confidence: float
    evidence_image: Optional[np.ndarray] = None
    license_plate: Optional[str] = None

class SpeedCalculator:
    """
    Speed calculator using trajectory analysis and camera calibration.
    
    Features:
    - Real-world speed calculation from pixel tracking
    - Multiple measurement methods (distance/time, instantaneous)
    - Speed smoothing and filtering
    - Violation detection with confidence scoring
    - Support for multiple measurement zones
    """
    
    def __init__(self, calibrator: CameraCalibrator):
        """
        Initialize speed calculator.
        
        Args:
            calibrator: Camera calibrator instance
        """
        self.calibrator = calibrator
        self.speed_measurements: Dict[int, List[SpeedMeasurement]] = {}
        self.violation_threshold = 5.0  # km/h tolerance before violation
        self.min_measurement_distance = 5.0  # minimum distance for reliable measurement (meters)
        self.min_measurement_time = 0.5     # minimum time for reliable measurement (seconds)
        self.smoothing_window = 5           # number of measurements for smoothing
        
        logger.info("SpeedCalculator initialized")
    
    def calculate_speed_from_trajectory(self, trajectory: Trajectory, zone_id: Optional[str] = None) -> Optional[SpeedMeasurement]:
        """
        Calculate speed from complete trajectory data.
        
        Args:
            trajectory: Vehicle trajectory
            zone_id: Optional specific zone for measurement
            
        Returns:
            Speed measurement or None if calculation failed
        """
        if not self.calibrator.is_calibrated:
            logger.warning("Camera not calibrated, cannot calculate speed")
            return None
        
        if len(trajectory.positions) < 2:
            logger.warning(f"Insufficient trajectory data for vehicle {trajectory.vehicle_id}")
            return None
        
        try:
            # Convert pixel trajectory to real-world coordinates
            real_positions = []
            valid_timestamps = []
            
            for i, (pixel_x, pixel_y) in enumerate(trajectory.positions):
                real_coords = self.calibrator.pixel_to_real(pixel_x, pixel_y)
                if real_coords is not None:
                    real_positions.append(real_coords)
                    valid_timestamps.append(trajectory.timestamps[i])
            
            if len(real_positions) < 2:
                logger.warning(f"Insufficient valid real-world positions for vehicle {trajectory.vehicle_id}")
                return None
            
            # Determine measurement zone
            measurement_zone = "default"
            if zone_id:
                if zone_id in self.calibrator.calibration_zones:
                    measurement_zone = zone_id
            else:
                # Auto-detect zone from trajectory
                center_pixel = trajectory.positions[len(trajectory.positions) // 2]
                zone = self.calibrator.get_zone_for_point(center_pixel[0], center_pixel[1])
                if zone:
                    measurement_zone = zone.zone_id
            
            # Calculate distance and time
            start_pos = real_positions[0]
            end_pos = real_positions[-1]
            start_time = valid_timestamps[0]
            end_time = valid_timestamps[-1]
            
            distance_traveled = math.sqrt(
                (end_pos[0] - start_pos[0])**2 + 
                (end_pos[1] - start_pos[1])**2
            )
            
            time_elapsed = end_time - start_time
            
            # Validate measurement parameters
            if distance_traveled < self.min_measurement_distance:
                logger.warning(f"Measurement distance too short: {distance_traveled:.2f}m")
                return None
            
            if time_elapsed < self.min_measurement_time:
                logger.warning(f"Measurement time too short: {time_elapsed:.2f}s")
                return None
            
            # Calculate speed
            speed_mps = distance_traveled / time_elapsed
            speed_kmh = speed_mps * 3.6
            
            # Calculate confidence based on trajectory quality
            confidence = self._calculate_speed_confidence(
                trajectory, real_positions, distance_traveled, time_elapsed
            )
            
            measurement = SpeedMeasurement(
                vehicle_id=trajectory.vehicle_id,
                timestamp=end_time,
                speed_kmh=speed_kmh,
                speed_mps=speed_mps,
                distance_traveled=distance_traveled,
                time_elapsed=time_elapsed,
                measurement_zone=measurement_zone,
                confidence=confidence,
                entry_point=start_pos,
                exit_point=end_pos,
                entry_time=start_time,
                exit_time=end_time,
                pixel_trajectory=trajectory.positions.copy(),
                real_trajectory=real_positions
            )
            
            # Store measurement
            if trajectory.vehicle_id not in self.speed_measurements:
                self.speed_measurements[trajectory.vehicle_id] = []
            self.speed_measurements[trajectory.vehicle_id].append(measurement)
            
            logger.info(f"Speed calculated for vehicle {trajectory.vehicle_id}: {speed_kmh:.2f} km/h")
            return measurement
            
        except Exception as e:
            logger.error(f"Failed to calculate speed from trajectory: {e}")
            return None
    
    def calculate_instantaneous_speed(self, trajectory: Trajectory, window_size: int = 3) -> List[float]:
        """
        Calculate instantaneous speed at each trajectory point.
        
        Args:
            trajectory: Vehicle trajectory
            window_size: Number of points to use for speed calculation
            
        Returns:
            List of instantaneous speeds in km/h
        """
        if not self.calibrator.is_calibrated or len(trajectory.positions) < window_size:
            return []
        
        speeds = []
        
        for i in range(len(trajectory.positions) - window_size + 1):
            # Get window of positions
            window_positions = trajectory.positions[i:i + window_size]
            window_timestamps = trajectory.timestamps[i:i + window_size]
            
            # Convert to real-world coordinates
            real_positions = []
            valid_timestamps = []
            
            for j, (px, py) in enumerate(window_positions):
                real_coords = self.calibrator.pixel_to_real(px, py)
                if real_coords is not None:
                    real_positions.append(real_coords)
                    valid_timestamps.append(window_timestamps[j])
            
            if len(real_positions) >= 2:
                # Calculate speed over window
                start_pos = real_positions[0]
                end_pos = real_positions[-1]
                start_time = valid_timestamps[0]
                end_time = valid_timestamps[-1]
                
                distance = math.sqrt(
                    (end_pos[0] - start_pos[0])**2 + 
                    (end_pos[1] - start_pos[1])**2
                )
                
                time_diff = end_time - start_time
                if time_diff > 0:
                    speed_mps = distance / time_diff
                    speed_kmh = speed_mps * 3.6
                    speeds.append(speed_kmh)
                else:
                    speeds.append(0.0)
            else:
                speeds.append(0.0)
        
        return speeds
    
    def get_smoothed_speed(self, vehicle_id: int) -> Optional[float]:
        """
        Get smoothed speed for a vehicle using recent measurements.
        
        Args:
            vehicle_id: Vehicle ID
            
        Returns:
            Smoothed speed in km/h or None
        """
        if vehicle_id not in self.speed_measurements:
            return None
        
        measurements = self.speed_measurements[vehicle_id]
        if not measurements:
            return None
        
        # Use recent measurements for smoothing
        recent_measurements = measurements[-self.smoothing_window:]
        
        # Weight measurements by confidence
        weighted_speeds = []
        total_weight = 0.0
        
        for measurement in recent_measurements:
            weight = measurement.confidence
            weighted_speeds.append(measurement.speed_kmh * weight)
            total_weight += weight
        
        if total_weight > 0:
            smoothed_speed = sum(weighted_speeds) / total_weight
            return smoothed_speed
        
        return measurements[-1].speed_kmh
    
    def detect_speed_violation(self, measurement: SpeedMeasurement) -> Optional[SpeedViolation]:
        """
        Detect speed violation from measurement.
        
        Args:
            measurement: Speed measurement
            
        Returns:
            Speed violation or None if no violation
        """
        # Get speed limit for measurement zone
        speed_limit = 60.0  # Default speed limit (km/h)
        
        if measurement.measurement_zone in self.calibrator.calibration_zones:
            zone = self.calibrator.calibration_zones[measurement.measurement_zone]
            speed_limit = zone.speed_limit
        
        # Check for violation with tolerance
        if measurement.speed_kmh > (speed_limit + self.violation_threshold):
            violation_amount = measurement.speed_kmh - speed_limit
            violation_percentage = (violation_amount / speed_limit) * 100
            
            violation = SpeedViolation(
                vehicle_id=measurement.vehicle_id,
                timestamp=measurement.timestamp,
                measured_speed=measurement.speed_kmh,
                speed_limit=speed_limit,
                violation_amount=violation_amount,
                violation_percentage=violation_percentage,
                measurement_zone=measurement.measurement_zone,
                confidence=measurement.confidence
            )
            
            logger.warning(f"Speed violation detected: Vehicle {measurement.vehicle_id} "
                         f"at {measurement.speed_kmh:.1f} km/h (limit: {speed_limit} km/h)")
            
            return violation
        
        return None
    
    def _calculate_speed_confidence(self, trajectory: Trajectory, real_positions: List[Tuple[float, float]], 
                                  distance: float, time_elapsed: float) -> float:
        """Calculate confidence score for speed measurement."""
        confidence = 1.0
        
        # Penalize short distances
        if distance < 10.0:
            confidence *= (distance / 10.0)
        
        # Penalize short time periods
        if time_elapsed < 2.0:
            confidence *= (time_elapsed / 2.0)
        
        # Penalize irregular trajectories
        if len(real_positions) > 2:
            # Calculate trajectory smoothness
            direction_changes = 0
            prev_direction = None
            
            for i in range(1, len(real_positions)):
                dx = real_positions[i][0] - real_positions[i-1][0]
                dy = real_positions[i][1] - real_positions[i-1][1]
                
                if abs(dx) > 0.1 or abs(dy) > 0.1:  # Ignore very small movements
                    current_direction = math.atan2(dy, dx)
                    
                    if prev_direction is not None:
                        angle_diff = abs(current_direction - prev_direction)
                        # Normalize to [0, π]
                        if angle_diff > math.pi:
                            angle_diff = 2 * math.pi - angle_diff
                        
                        # Consider significant direction changes
                        if angle_diff > math.pi / 4:  # 45 degrees
                            direction_changes += 1
                    
                    prev_direction = current_direction
            
            # Penalize excessive direction changes
            if len(real_positions) > 0:
                change_ratio = direction_changes / len(real_positions)
                if change_ratio > 0.2:
                    confidence *= (1.0 - change_ratio)
        
        # Ensure confidence is in [0, 1]
        return max(0.0, min(1.0, confidence))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get speed calculation statistics."""
        total_measurements = sum(len(measurements) for measurements in self.speed_measurements.values())
        
        if total_measurements == 0:
            return {
                "total_measurements": 0,
                "vehicles_tracked": 0,
                "average_speed": 0.0,
                "speed_range": (0.0, 0.0),
                "average_confidence": 0.0
            }
        
        all_measurements = []
        for measurements in self.speed_measurements.values():
            all_measurements.extend(measurements)
        
        speeds = [m.speed_kmh for m in all_measurements]
        confidences = [m.confidence for m in all_measurements]
        
        return {
            "total_measurements": total_measurements,
            "vehicles_tracked": len(self.speed_measurements),
            "average_speed": np.mean(speeds),
            "speed_range": (min(speeds), max(speeds)),
            "average_confidence": np.mean(confidences),
            "measurements_per_vehicle": total_measurements / len(self.speed_measurements)
        }
    
    def clear_old_measurements(self, max_age: float = 300.0):
        """
        Clear old speed measurements to free memory.
        
        Args:
            max_age: Maximum age of measurements to keep (seconds)
        """
        current_time = time.time()
        removed_count = 0
        
        for vehicle_id in list(self.speed_measurements.keys()):
            measurements = self.speed_measurements[vehicle_id]
            
            # Filter out old measurements
            recent_measurements = [
                m for m in measurements 
                if (current_time - m.timestamp) <= max_age
            ]
            
            removed_count += len(measurements) - len(recent_measurements)
            
            if recent_measurements:
                self.speed_measurements[vehicle_id] = recent_measurements
            else:
                del self.speed_measurements[vehicle_id]
        
        if removed_count > 0:
            logger.info(f"Cleared {removed_count} old speed measurements")
    
    def convert_speed(self, speed_value: float, from_unit: SpeedUnit, to_unit: SpeedUnit) -> float:
        """Convert speed between different units."""
        # Convert to m/s first
        if from_unit == SpeedUnit.KMH:
            mps = speed_value / 3.6
        elif from_unit == SpeedUnit.MPH:
            mps = speed_value * 0.44704
        else:  # MPS
            mps = speed_value
        
        # Convert to target unit
        if to_unit == SpeedUnit.KMH:
            return mps * 3.6
        elif to_unit == SpeedUnit.MPH:
            return mps / 0.44704
        else:  # MPS
            return mps