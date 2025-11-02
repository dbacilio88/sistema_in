"""
Lane Detection and Violation Detection.

This module provides lane detection capabilities for identifying
lane boundaries and detecting lane violation infractions.
"""

import logging
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import time
import math

logger = logging.getLogger(__name__)

class LaneType(Enum):
    """Types of lane markings."""
    SOLID = "solid"
    DASHED = "dashed"
    DOUBLE_SOLID = "double_solid"
    SOLID_DASHED = "solid_dashed"
    NO_PASSING = "no_passing"

@dataclass
class LaneMarking:
    """Individual lane marking detection."""
    points: List[Tuple[int, int]]  # Lane points in pixel coordinates
    lane_type: LaneType
    confidence: float
    side: str  # "left" or "right"
    polynomial_coeffs: Optional[np.ndarray] = None  # Polynomial fit coefficients

@dataclass
class LaneGeometry:
    """Lane geometry information."""
    left_lane: Optional[LaneMarking]
    right_lane: Optional[LaneMarking]
    center_line: Optional[List[Tuple[int, int]]]
    lane_width: Optional[float]  # in meters if calibrated
    curve_radius: Optional[float]  # in meters
    lane_departure_offset: float = 0.0  # offset from center

@dataclass
class LaneViolation:
    """Lane violation detection result."""
    vehicle_id: int
    timestamp: float
    violation_type: str  # "lane_departure", "improper_lane_change", "shoulder_driving"
    severity: str
    lane_position: float  # -1 to 1, where 0 is center
    crossed_marking: Optional[LaneType] = None
    confidence: float = 0.0

class LaneDetector:
    """
    Lane detection system for traffic monitoring.
    
    Features:
    - Canny edge detection with Hough transform
    - Polynomial lane fitting
    - Lane tracking between frames
    - Real-time lane violation detection
    - Support for various lane marking types
    """
    
    def __init__(self, image_width: int = 1920, image_height: int = 1080):
        """
        Initialize lane detector.
        
        Args:
            image_width: Input image width
            image_height: Input image height
        """
        self.image_width = image_width
        self.image_height = image_height
        
        # Lane detection parameters
        self.roi_vertices = self._calculate_roi_vertices()
        self.gaussian_blur_kernel = 5
        self.canny_low_threshold = 50
        self.canny_high_threshold = 150
        
        # Hough transform parameters
        self.hough_rho = 2
        self.hough_theta = np.pi / 180
        self.hough_threshold = 50
        self.hough_min_line_length = 100
        self.hough_max_line_gap = 160
        
        # Lane tracking
        self.previous_lanes: Optional[LaneGeometry] = None
        self.lane_history: List[LaneGeometry] = []
        self.max_history = 10
        
        # Violation detection parameters
        self.violation_threshold = 0.3  # 30% of lane width
        self.min_violation_duration = 2.0  # seconds
        
        logger.info(f"LaneDetector initialized for {image_width}x{image_height}")
    
    def _calculate_roi_vertices(self) -> np.ndarray:
        """Calculate region of interest vertices for lane detection."""
        # Define ROI as trapezoid focusing on road area
        bottom_width = self.image_width * 0.8
        top_width = self.image_width * 0.4
        height_start = self.image_height * 0.6
        
        vertices = np.array([
            [self.image_width * 0.1, self.image_height],  # Bottom left
            [self.image_width * 0.9, self.image_height],  # Bottom right
            [self.image_width * 0.5 + top_width/2, height_start],  # Top right
            [self.image_width * 0.5 - top_width/2, height_start]   # Top left
        ], dtype=np.int32)
        
        return vertices
    
    def detect_lanes(self, image: np.ndarray) -> LaneGeometry:
        """
        Detect lane markings in the image.
        
        Args:
            image: Input image
            
        Returns:
            Lane geometry information
        """
        try:
            # Preprocessing
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (self.gaussian_blur_kernel, self.gaussian_blur_kernel), 0)
            
            # Edge detection
            edges = cv2.Canny(blurred, self.canny_low_threshold, self.canny_high_threshold)
            
            # Apply ROI mask
            masked_edges = self._apply_roi_mask(edges)
            
            # Hough line detection
            lines = cv2.HoughLinesP(
                masked_edges,
                self.hough_rho,
                self.hough_theta,
                self.hough_threshold,
                minLineLength=self.hough_min_line_length,
                maxLineGap=self.hough_max_line_gap
            )
            
            if lines is None:
                return self._get_default_lane_geometry()
            
            # Separate left and right lanes
            left_lines, right_lines = self._separate_lanes(lines)
            
            # Fit polynomials to lane lines
            left_lane = self._fit_lane_polynomial(left_lines, "left") if left_lines else None
            right_lane = self._fit_lane_polynomial(right_lines, "right") if right_lines else None
            
            # Calculate lane geometry
            lane_geometry = self._calculate_lane_geometry(left_lane, right_lane, image.shape)
            
            # Update lane history
            self._update_lane_history(lane_geometry)
            
            return lane_geometry
            
        except Exception as e:
            logger.error(f"Failed to detect lanes: {e}")
            return self._get_default_lane_geometry()
    
    def _apply_roi_mask(self, image: np.ndarray) -> np.ndarray:
        """Apply region of interest mask to image."""
        mask = np.zeros_like(image)
        cv2.fillPoly(mask, [self.roi_vertices], 255)
        return cv2.bitwise_and(image, mask)
    
    def _separate_lanes(self, lines: np.ndarray) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """Separate detected lines into left and right lanes."""
        left_lines = []
        right_lines = []
        
        image_center = self.image_width // 2
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Calculate slope
            if x2 - x1 == 0:  # Vertical line
                continue
            
            slope = (y2 - y1) / (x2 - x1)
            
            # Filter by slope and position
            if slope < -0.5 and x1 < image_center and x2 < image_center:
                # Left lane (negative slope, left side)
                left_lines.append(line[0])
            elif slope > 0.5 and x1 > image_center and x2 > image_center:
                # Right lane (positive slope, right side)
                right_lines.append(line[0])
        
        return left_lines, right_lines
    
    def _fit_lane_polynomial(self, lines: List[np.ndarray], side: str) -> Optional[LaneMarking]:
        """Fit polynomial to lane lines."""
        if not lines:
            return None
        
        # Extract all points from lines
        x_coords = []
        y_coords = []
        
        for line in lines:
            x1, y1, x2, y2 = line
            x_coords.extend([x1, x2])
            y_coords.extend([y1, y2])
        
        if len(x_coords) < 4:  # Need at least 4 points
            return None
        
        try:
            # Fit 2nd degree polynomial
            x_coords = np.array(x_coords)
            y_coords = np.array(y_coords)
            
            # Sort by y coordinate
            sort_indices = np.argsort(y_coords)
            x_sorted = x_coords[sort_indices]
            y_sorted = y_coords[sort_indices]
            
            # Fit polynomial (x as function of y for better stability)
            poly_coeffs = np.polyfit(y_sorted, x_sorted, 2)
            
            # Generate smooth lane points
            y_points = np.linspace(y_sorted[0], y_sorted[-1], 50)
            x_points = np.polyval(poly_coeffs, y_points)
            
            # Create lane points
            lane_points = [(int(x), int(y)) for x, y in zip(x_points, y_points)]
            
            # Calculate confidence based on fit quality
            predicted_x = np.polyval(poly_coeffs, y_sorted)
            mse = np.mean((x_sorted - predicted_x) ** 2)
            confidence = max(0.0, 1.0 - mse / 10000)  # Normalize MSE
            
            return LaneMarking(
                points=lane_points,
                lane_type=LaneType.DASHED,  # Default assumption
                confidence=confidence,
                side=side,
                polynomial_coeffs=poly_coeffs
            )
            
        except Exception as e:
            logger.error(f"Failed to fit polynomial for {side} lane: {e}")
            return None
    
    def _calculate_lane_geometry(self, left_lane: Optional[LaneMarking], 
                               right_lane: Optional[LaneMarking], 
                               image_shape: Tuple[int, int, int]) -> LaneGeometry:
        """Calculate comprehensive lane geometry."""
        height, width = image_shape[:2]
        
        # Calculate center line
        center_line = None
        if left_lane and right_lane:
            center_line = self._calculate_center_line(left_lane, right_lane)
        
        # Calculate lane width (in pixels)
        lane_width = None
        if left_lane and right_lane:
            # Use bottom of image for width calculation
            left_bottom = left_lane.points[-1] if left_lane.points else (width//4, height)
            right_bottom = right_lane.points[-1] if right_lane.points else (3*width//4, height)
            lane_width = abs(right_bottom[0] - left_bottom[0])
        
        # Calculate curve radius
        curve_radius = None
        if left_lane and left_lane.polynomial_coeffs is not None:
            # Calculate curvature at bottom of image
            y_eval = height
            curve_radius = self._calculate_curve_radius(left_lane.polynomial_coeffs, y_eval)
        elif right_lane and right_lane.polynomial_coeffs is not None:
            y_eval = height
            curve_radius = self._calculate_curve_radius(right_lane.polynomial_coeffs, y_eval)
        
        return LaneGeometry(
            left_lane=left_lane,
            right_lane=right_lane,
            center_line=center_line,
            lane_width=lane_width,
            curve_radius=curve_radius
        )
    
    def _calculate_center_line(self, left_lane: LaneMarking, right_lane: LaneMarking) -> List[Tuple[int, int]]:
        """Calculate center line between left and right lanes."""
        center_points = []
        
        # Find common y coordinates
        left_y_coords = [p[1] for p in left_lane.points]
        right_y_coords = [p[1] for p in right_lane.points]
        
        min_y = max(min(left_y_coords), min(right_y_coords))
        max_y = min(max(left_y_coords), max(right_y_coords))
        
        if min_y >= max_y:
            return center_points
        
        # Interpolate center points
        y_coords = np.linspace(min_y, max_y, 30)
        
        for y in y_coords:
            # Find corresponding x coordinates
            left_x = self._interpolate_x_for_y(left_lane.points, y)
            right_x = self._interpolate_x_for_y(right_lane.points, y)
            
            if left_x is not None and right_x is not None:
                center_x = (left_x + right_x) // 2
                center_points.append((int(center_x), int(y)))
        
        return center_points
    
    def _interpolate_x_for_y(self, points: List[Tuple[int, int]], target_y: float) -> Optional[int]:
        """Interpolate x coordinate for given y coordinate."""
        if len(points) < 2:
            return None
        
        # Find surrounding points
        for i in range(len(points) - 1):
            y1 = points[i][1]
            y2 = points[i + 1][1]
            
            if min(y1, y2) <= target_y <= max(y1, y2):
                x1 = points[i][0]
                x2 = points[i + 1][0]
                
                # Linear interpolation
                if y2 != y1:
                    x = x1 + (x2 - x1) * (target_y - y1) / (y2 - y1)
                    return int(x)
        
        return None
    
    def _calculate_curve_radius(self, poly_coeffs: np.ndarray, y_eval: float) -> float:
        """Calculate curve radius from polynomial coefficients."""
        try:
            # Polynomial: x = A*y^2 + B*y + C
            A, B, C = poly_coeffs
            
            # First derivative: dx/dy = 2*A*y + B
            dx_dy = 2 * A * y_eval + B
            
            # Second derivative: d2x/dy2 = 2*A
            d2x_dy2 = 2 * A
            
            # Curvature formula: k = |d2x/dy2| / (1 + (dx/dy)^2)^(3/2)
            curvature = abs(d2x_dy2) / (1 + dx_dy**2)**(3/2)
            
            # Radius of curvature
            if curvature > 0:
                radius = 1 / curvature
                return radius
            else:
                return float('inf')  # Straight line
                
        except Exception:
            return float('inf')
    
    def _update_lane_history(self, lane_geometry: LaneGeometry):
        """Update lane detection history for temporal consistency."""
        self.lane_history.append(lane_geometry)
        
        if len(self.lane_history) > self.max_history:
            self.lane_history.pop(0)
        
        self.previous_lanes = lane_geometry
    
    def _get_default_lane_geometry(self) -> LaneGeometry:
        """Return default lane geometry when detection fails."""
        return LaneGeometry(
            left_lane=None,
            right_lane=None,
            center_line=None,
            lane_width=None,
            curve_radius=None
        )
    
    def detect_vehicle_lane_position(self, vehicle_center: Tuple[int, int], 
                                   lane_geometry: LaneGeometry) -> float:
        """
        Calculate vehicle position relative to lane center.
        
        Args:
            vehicle_center: Vehicle center coordinates (x, y)
            lane_geometry: Current lane geometry
            
        Returns:
            Position relative to lane center (-1 to 1, where 0 is center)
        """
        if not lane_geometry.left_lane or not lane_geometry.right_lane:
            return 0.0  # Cannot determine position
        
        vehicle_x, vehicle_y = vehicle_center
        
        # Find lane boundaries at vehicle's y position
        left_x = self._interpolate_x_for_y(lane_geometry.left_lane.points, vehicle_y)
        right_x = self._interpolate_x_for_y(lane_geometry.right_lane.points, vehicle_y)
        
        if left_x is None or right_x is None:
            return 0.0
        
        # Calculate relative position
        lane_center = (left_x + right_x) / 2
        lane_width = abs(right_x - left_x)
        
        if lane_width > 0:
            # Normalize to [-1, 1]
            relative_position = (vehicle_x - lane_center) / (lane_width / 2)
            return np.clip(relative_position, -1.0, 1.0)
        
        return 0.0
    
    def detect_lane_violations(self, vehicles: List[Dict], lane_geometry: LaneGeometry) -> List[LaneViolation]:
        """
        Detect lane violations for tracked vehicles.
        
        Args:
            vehicles: List of vehicle tracking information
            lane_geometry: Current lane geometry
            
        Returns:
            List of detected lane violations
        """
        violations = []
        current_time = time.time()
        
        for vehicle in vehicles:
            vehicle_id = vehicle.get('track_id', 0)
            center_x = vehicle.get('center_x', 0)
            center_y = vehicle.get('center_y', 0)
            
            # Calculate lane position
            lane_position = self.detect_vehicle_lane_position((center_x, center_y), lane_geometry)
            
            # Check for lane departure
            if abs(lane_position) > self.violation_threshold:
                severity = "minor"
                if abs(lane_position) > 0.6:
                    severity = "moderate"
                if abs(lane_position) > 0.8:
                    severity = "severe"
                
                violation_type = "lane_departure"
                if lane_position < -0.8:
                    violation_type = "left_lane_departure"
                elif lane_position > 0.8:
                    violation_type = "right_lane_departure"
                
                violation = LaneViolation(
                    vehicle_id=vehicle_id,
                    timestamp=current_time,
                    violation_type=violation_type,
                    severity=severity,
                    lane_position=lane_position,
                    confidence=0.8
                )
                
                violations.append(violation)
        
        return violations
    
    def create_lane_mask(self, lane_geometry: LaneGeometry, image_shape: Tuple[int, int]) -> np.ndarray:
        """
        Create binary mask of valid lane areas.
        
        Args:
            lane_geometry: Lane geometry information
            image_shape: Image dimensions (height, width)
            
        Returns:
            Binary mask where 255 indicates valid lane area
        """
        height, width = image_shape
        mask = np.zeros((height, width), dtype=np.uint8)
        
        if not lane_geometry.left_lane or not lane_geometry.right_lane:
            return mask
        
        # Create polygon from lane boundaries
        left_points = lane_geometry.left_lane.points
        right_points = lane_geometry.right_lane.points
        
        if not left_points or not right_points:
            return mask
        
        # Combine points to form lane polygon
        lane_polygon = np.array(left_points + right_points[::-1], dtype=np.int32)
        
        # Fill the lane area
        cv2.fillPoly(mask, [lane_polygon], 255)
        
        return mask
    
    def visualize_lanes(self, image: np.ndarray, lane_geometry: LaneGeometry) -> np.ndarray:
        """
        Visualize detected lanes on image.
        
        Args:
            image: Input image
            lane_geometry: Lane geometry to visualize
            
        Returns:
            Image with lane visualization
        """
        vis_image = image.copy()
        
        # Draw left lane
        if lane_geometry.left_lane and lane_geometry.left_lane.points:
            points = np.array(lane_geometry.left_lane.points, dtype=np.int32)
            cv2.polylines(vis_image, [points], False, (255, 0, 0), 3)  # Blue
        
        # Draw right lane
        if lane_geometry.right_lane and lane_geometry.right_lane.points:
            points = np.array(lane_geometry.right_lane.points, dtype=np.int32)
            cv2.polylines(vis_image, [points], False, (0, 255, 0), 3)  # Green
        
        # Draw center line
        if lane_geometry.center_line:
            points = np.array(lane_geometry.center_line, dtype=np.int32)
            cv2.polylines(vis_image, [points], False, (0, 255, 255), 2)  # Yellow
        
        # Draw ROI
        cv2.polylines(vis_image, [self.roi_vertices], True, (255, 255, 255), 2)
        
        # Add lane information text
        info_text = []
        if lane_geometry.lane_width:
            info_text.append(f"Lane Width: {lane_geometry.lane_width:.0f} px")
        if lane_geometry.curve_radius and lane_geometry.curve_radius != float('inf'):
            info_text.append(f"Curve Radius: {lane_geometry.curve_radius:.0f} px")
        
        for i, text in enumerate(info_text):
            cv2.putText(vis_image, text, (10, 30 + i * 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return vis_image