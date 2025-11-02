"""
Camera Calibrator for speed measurement.

This module handles camera calibration to convert pixel coordinates
to real-world distances for accurate speed calculation.
"""

import logging
import json
import numpy as np
import cv2
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import time

logger = logging.getLogger(__name__)

@dataclass
class CalibrationPoint:
    """Single calibration point with pixel and real-world coordinates."""
    pixel_x: int
    pixel_y: int
    real_x: float  # meters
    real_y: float  # meters
    description: str = ""

@dataclass
class CalibrationZone:
    """Calibration zone for speed measurement."""
    zone_id: str
    name: str
    pixel_points: List[Tuple[int, int]]  # Zone boundary in pixels
    real_world_points: List[Tuple[float, float]]  # Zone boundary in meters
    speed_limit: float  # km/h
    measurement_distance: float  # meters (distance covered for speed calc)
    entry_line: Tuple[Tuple[int, int], Tuple[int, int]]  # Entry line (pixel coords)
    exit_line: Tuple[Tuple[int, int], Tuple[int, int]]   # Exit line (pixel coords)
    direction: str = "any"  # "forward", "backward", "any"

class CameraCalibrator:
    """
    Camera calibrator for converting pixel coordinates to real-world distances.
    
    Features:
    - Homography-based calibration
    - Multiple calibration zones
    - Perspective correction
    - Distance measurement validation
    - Real-time calibration updates
    """
    
    def __init__(self):
        """Initialize camera calibrator."""
        self.homography_matrix = None
        self.inverse_homography = None
        self.calibration_points: List[CalibrationPoint] = []
        self.calibration_zones: Dict[str, CalibrationZone] = {}
        self.pixels_per_meter = None
        self.is_calibrated = False
        
        # Calibration quality metrics
        self.calibration_error = None
        self.confidence_score = 0.0
        
        logger.info("CameraCalibrator initialized")
    
    def add_calibration_point(self, pixel_x: int, pixel_y: int, real_x: float, real_y: float, description: str = "") -> bool:
        """
        Add a calibration point.
        
        Args:
            pixel_x, pixel_y: Pixel coordinates
            real_x, real_y: Real-world coordinates in meters
            description: Optional description
            
        Returns:
            True if point was added successfully
        """
        try:
            point = CalibrationPoint(pixel_x, pixel_y, real_x, real_y, description)
            self.calibration_points.append(point)
            
            logger.info(f"Added calibration point: ({pixel_x}, {pixel_y}) -> ({real_x:.2f}m, {real_y:.2f}m)")
            
            # Try to compute homography if we have enough points
            if len(self.calibration_points) >= 4:
                return self._compute_homography()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add calibration point: {e}")
            return False
    
    def _compute_homography(self) -> bool:
        """Compute homography matrix from calibration points."""
        try:
            if len(self.calibration_points) < 4:
                logger.warning("Need at least 4 calibration points for homography")
                return False
            
            # Extract pixel and real-world coordinates
            pixel_coords = np.array([[p.pixel_x, p.pixel_y] for p in self.calibration_points], dtype=np.float32)
            real_coords = np.array([[p.real_x, p.real_y] for p in self.calibration_points], dtype=np.float32)
            
            # Compute homography using RANSAC for robustness
            self.homography_matrix, mask = cv2.findHomography(
                pixel_coords, real_coords,
                method=cv2.RANSAC,
                ransacReprojThreshold=5.0,
                confidence=0.99
            )
            
            if self.homography_matrix is None:
                logger.error("Failed to compute homography matrix")
                return False
            
            # Compute inverse homography for pixel->real conversion
            self.inverse_homography = np.linalg.inv(self.homography_matrix)
            
            # Calculate calibration error
            self._calculate_calibration_error()
            
            # Mark as calibrated if error is acceptable
            if self.calibration_error < 0.5:  # 50cm error threshold
                self.is_calibrated = True
                self.confidence_score = max(0.0, 1.0 - self.calibration_error)
                logger.info(f"Camera calibrated successfully. Error: {self.calibration_error:.3f}m")
            else:
                logger.warning(f"Calibration error too high: {self.calibration_error:.3f}m")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to compute homography: {e}")
            return False
    
    def _calculate_calibration_error(self):
        """Calculate calibration error using leave-one-out validation."""
        if len(self.calibration_points) < 4:
            return
        
        errors = []
        
        for i in range(len(self.calibration_points)):
            # Use all points except one for calibration
            test_point = self.calibration_points[i]
            train_points = self.calibration_points[:i] + self.calibration_points[i+1:]
            
            if len(train_points) < 4:
                continue
            
            # Compute homography with training points
            pixel_coords = np.array([[p.pixel_x, p.pixel_y] for p in train_points], dtype=np.float32)
            real_coords = np.array([[p.real_x, p.real_y] for p in train_points], dtype=np.float32)
            
            H, _ = cv2.findHomography(pixel_coords, real_coords, method=cv2.RANSAC)
            
            if H is not None:
                # Project test point and calculate error
                pixel_point = np.array([[[test_point.pixel_x, test_point.pixel_y]]], dtype=np.float32)
                projected_real = cv2.perspectiveTransform(pixel_point, H)[0][0]
                
                actual_real = np.array([test_point.real_x, test_point.real_y])
                error = np.linalg.norm(projected_real - actual_real)
                errors.append(error)
        
        self.calibration_error = np.mean(errors) if errors else float('inf')
    
    def pixel_to_real(self, pixel_x: int, pixel_y: int) -> Optional[Tuple[float, float]]:
        """
        Convert pixel coordinates to real-world coordinates.
        
        Args:
            pixel_x, pixel_y: Pixel coordinates
            
        Returns:
            (real_x, real_y) in meters or None if not calibrated
        """
        if not self.is_calibrated:
            return None
        
        try:
            pixel_point = np.array([[[pixel_x, pixel_y]]], dtype=np.float32)
            real_point = cv2.perspectiveTransform(pixel_point, self.homography_matrix)[0][0]
            return float(real_point[0]), float(real_point[1])
        except Exception as e:
            logger.error(f"Failed to convert pixel to real coordinates: {e}")
            return None
    
    def real_to_pixel(self, real_x: float, real_y: float) -> Optional[Tuple[int, int]]:
        """
        Convert real-world coordinates to pixel coordinates.
        
        Args:
            real_x, real_y: Real-world coordinates in meters
            
        Returns:
            (pixel_x, pixel_y) or None if not calibrated
        """
        if not self.is_calibrated:
            return None
        
        try:
            real_point = np.array([[[real_x, real_y]]], dtype=np.float32)
            pixel_point = cv2.perspectiveTransform(real_point, self.inverse_homography)[0][0]
            return int(pixel_point[0]), int(pixel_point[1])
        except Exception as e:
            logger.error(f"Failed to convert real to pixel coordinates: {e}")
            return None
    
    def calculate_distance(self, point1: Tuple[int, int], point2: Tuple[int, int]) -> Optional[float]:
        """
        Calculate real-world distance between two pixel points.
        
        Args:
            point1, point2: Pixel coordinates
            
        Returns:
            Distance in meters or None if not calibrated
        """
        if not self.is_calibrated:
            return None
        
        real1 = self.pixel_to_real(point1[0], point1[1])
        real2 = self.pixel_to_real(point2[0], point2[1])
        
        if real1 is None or real2 is None:
            return None
        
        distance = np.sqrt((real2[0] - real1[0])**2 + (real2[1] - real1[1])**2)
        return float(distance)
    
    def add_calibration_zone(self, zone: CalibrationZone):
        """Add a calibration zone for speed measurement."""
        self.calibration_zones[zone.zone_id] = zone
        logger.info(f"Added calibration zone: {zone.name} (limit: {zone.speed_limit} km/h)")
    
    def get_zone_for_point(self, pixel_x: int, pixel_y: int) -> Optional[CalibrationZone]:
        """Get the calibration zone containing the given pixel point."""
        for zone in self.calibration_zones.values():
            if self._point_in_polygon((pixel_x, pixel_y), zone.pixel_points):
                return zone
        return None
    
    def _point_in_polygon(self, point: Tuple[int, int], polygon: List[Tuple[int, int]]) -> bool:
        """Check if point is inside polygon using ray casting algorithm."""
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def validate_calibration(self) -> Dict[str, Any]:
        """
        Validate current calibration quality.
        
        Returns:
            Validation metrics dictionary
        """
        if not self.is_calibrated:
            return {
                "is_valid": False,
                "error": "Not calibrated",
                "calibration_error": None,
                "confidence_score": 0.0
            }
        
        # Test calibration with known distances
        validation_results = {
            "is_valid": self.calibration_error < 0.5,
            "calibration_error": self.calibration_error,
            "confidence_score": self.confidence_score,
            "num_calibration_points": len(self.calibration_points),
            "num_zones": len(self.calibration_zones)
        }
        
        # Test distance calculation accuracy
        if len(self.calibration_points) >= 2:
            # Calculate distance between first two calibration points
            p1 = self.calibration_points[0]
            p2 = self.calibration_points[1]
            
            # Actual distance
            actual_distance = np.sqrt((p2.real_x - p1.real_x)**2 + (p2.real_y - p1.real_y)**2)
            
            # Calculated distance via pixel conversion
            calculated_distance = self.calculate_distance((p1.pixel_x, p1.pixel_y), (p2.pixel_x, p2.pixel_y))
            
            if calculated_distance is not None:
                distance_error = abs(calculated_distance - actual_distance)
                validation_results["distance_test_error"] = distance_error
                validation_results["distance_test_passed"] = distance_error < 0.2  # 20cm threshold
        
        return validation_results
    
    def save_calibration(self, filepath: str) -> bool:
        """Save calibration to file."""
        try:
            calibration_data = {
                "homography_matrix": self.homography_matrix.tolist() if self.homography_matrix is not None else None,
                "calibration_points": [asdict(p) for p in self.calibration_points],
                "calibration_zones": {k: asdict(v) for k, v in self.calibration_zones.items()},
                "calibration_error": self.calibration_error,
                "confidence_score": self.confidence_score,
                "is_calibrated": self.is_calibrated,
                "timestamp": time.time()
            }
            
            with open(filepath, 'w') as f:
                json.dump(calibration_data, f, indent=2)
            
            logger.info(f"Calibration saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save calibration: {e}")
            return False
    
    def load_calibration(self, filepath: str) -> bool:
        """Load calibration from file."""
        try:
            with open(filepath, 'r') as f:
                calibration_data = json.load(f)
            
            # Load homography matrix
            if calibration_data.get("homography_matrix"):
                self.homography_matrix = np.array(calibration_data["homography_matrix"])
                self.inverse_homography = np.linalg.inv(self.homography_matrix)
            
            # Load calibration points
            self.calibration_points = [
                CalibrationPoint(**point_data) 
                for point_data in calibration_data.get("calibration_points", [])
            ]
            
            # Load calibration zones
            self.calibration_zones = {}
            for zone_id, zone_data in calibration_data.get("calibration_zones", {}).items():
                self.calibration_zones[zone_id] = CalibrationZone(**zone_data)
            
            # Load metrics
            self.calibration_error = calibration_data.get("calibration_error")
            self.confidence_score = calibration_data.get("confidence_score", 0.0)
            self.is_calibrated = calibration_data.get("is_calibrated", False)
            
            logger.info(f"Calibration loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load calibration: {e}")
            return False
    
    def create_default_highway_calibration(self, image_width: int, image_height: int) -> bool:
        """
        Create a default calibration for highway monitoring.
        
        Args:
            image_width, image_height: Image dimensions
            
        Returns:
            True if calibration was created successfully
        """
        logger.info("Creating default highway calibration")
        
        # Clear existing calibration
        self.calibration_points.clear()
        self.calibration_zones.clear()
        
        # Define highway lanes (assumption: 3.5m lane width, 50m visible distance)
        lane_width = 3.5  # meters
        visible_distance = 50.0  # meters
        
        # Add calibration points for perspective view
        # Points represent lane markers and road boundaries
        calibration_points = [
            # Near edge (bottom of image)
            (image_width * 0.2, image_height * 0.9, -lane_width, 5.0),   # Left lane marker
            (image_width * 0.5, image_height * 0.9, 0.0, 5.0),          # Center line
            (image_width * 0.8, image_height * 0.9, lane_width, 5.0),   # Right lane marker
            
            # Far edge (horizon)
            (image_width * 0.4, image_height * 0.3, -lane_width/2, visible_distance),  # Left vanishing
            (image_width * 0.5, image_height * 0.3, 0.0, visible_distance),           # Center vanishing
            (image_width * 0.6, image_height * 0.3, lane_width/2, visible_distance),  # Right vanishing
        ]
        
        # Add calibration points
        for i, (px, py, rx, ry) in enumerate(calibration_points):
            self.add_calibration_point(int(px), int(py), rx, ry, f"Highway point {i+1}")
        
        # Create speed measurement zone
        zone = CalibrationZone(
            zone_id="highway_main",
            name="Main Highway Zone",
            pixel_points=[
                (int(image_width * 0.1), int(image_height * 0.9)),
                (int(image_width * 0.9), int(image_height * 0.9)),
                (int(image_width * 0.7), int(image_height * 0.3)),
                (int(image_width * 0.3), int(image_height * 0.3))
            ],
            real_world_points=[
                (-lane_width * 1.5, 5.0),
                (lane_width * 1.5, 5.0),
                (lane_width * 0.5, visible_distance),
                (-lane_width * 0.5, visible_distance)
            ],
            speed_limit=100.0,  # 100 km/h
            measurement_distance=20.0,  # 20 meter measurement zone
            entry_line=((int(image_width * 0.2), int(image_height * 0.8)), 
                       (int(image_width * 0.8), int(image_height * 0.8))),
            exit_line=((int(image_width * 0.3), int(image_height * 0.4)), 
                      (int(image_width * 0.7), int(image_height * 0.4))),
            direction="forward"
        )
        
        self.add_calibration_zone(zone)
        
        return self.is_calibrated
    
    def visualize_calibration(self, image: np.ndarray) -> np.ndarray:
        """
        Visualize calibration on image.
        
        Args:
            image: Input image
            
        Returns:
            Image with calibration visualization
        """
        vis_image = image.copy()
        
        # Draw calibration points
        for i, point in enumerate(self.calibration_points):
            cv2.circle(vis_image, (point.pixel_x, point.pixel_y), 5, (0, 255, 0), -1)
            cv2.putText(vis_image, f"P{i+1}", (point.pixel_x + 10, point.pixel_y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw calibration zones
        for zone in self.calibration_zones.values():
            # Draw zone boundary
            points = np.array(zone.pixel_points, dtype=np.int32)
            cv2.polylines(vis_image, [points], True, (255, 0, 0), 2)
            
            # Draw entry and exit lines
            cv2.line(vis_image, zone.entry_line[0], zone.entry_line[1], (0, 255, 255), 3)
            cv2.line(vis_image, zone.exit_line[0], zone.exit_line[1], (255, 0, 255), 3)
            
            # Zone label
            centroid = np.mean(points, axis=0).astype(int)
            cv2.putText(vis_image, f"{zone.name}\n{zone.speed_limit} km/h", 
                       tuple(centroid), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # Draw calibration status
        status_text = f"Calibrated: {self.is_calibrated}"
        if self.is_calibrated:
            status_text += f" (Error: {self.calibration_error:.3f}m)"
        
        cv2.putText(vis_image, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return vis_image