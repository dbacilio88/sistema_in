"""
Test suite for speed analysis module.

Tests camera calibration, speed calculation, and violation detection.
"""

import pytest
import numpy as np
import cv2
import time
from unittest.mock import Mock, patch, MagicMock
from typing import List, Tuple

from ..camera_calibrator import CameraCalibrator, CalibrationPoint, CalibrationZone
from ..speed_calculator import SpeedCalculator, SpeedMeasurement, SpeedViolation, SpeedUnit
from ..speed_analyzer import SpeedAnalyzer, AnalysisMode, ViolationEvent
from ...tracking.trajectory import Trajectory
from ...detection.vehicle_detector import Detection
from ...tracking.vehicle_tracker import TrackedVehicle

class TestCameraCalibrator:
    """Test camera calibration functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.calibrator = CameraCalibrator()
    
    def test_initialization(self):
        """Test calibrator initialization."""
        assert not self.calibrator.is_calibrated
        assert len(self.calibrator.calibration_points) == 0
        assert len(self.calibrator.calibration_zones) == 0
        assert self.calibrator.homography_matrix is None
    
    def test_add_calibration_point(self):
        """Test adding calibration points."""
        result = self.calibrator.add_calibration_point(100, 200, 5.0, 10.0, "test point")
        assert result is True
        assert len(self.calibrator.calibration_points) == 1
        
        point = self.calibrator.calibration_points[0]
        assert point.pixel_x == 100
        assert point.pixel_y == 200
        assert point.real_x == 5.0
        assert point.real_y == 10.0
        assert point.description == "test point"
    
    def test_homography_computation(self):
        """Test homography matrix computation."""
        # Add four calibration points for homography
        points = [
            (100, 400, 0, 0),    # Bottom left
            (500, 400, 10, 0),   # Bottom right
            (200, 200, 0, 20),   # Top left
            (400, 200, 10, 20)   # Top right
        ]
        
        for px, py, rx, ry in points:
            self.calibrator.add_calibration_point(px, py, rx, ry)
        
        assert self.calibrator.is_calibrated
        assert self.calibrator.homography_matrix is not None
        assert self.calibrator.inverse_homography is not None
    
    def test_pixel_to_real_conversion(self):
        """Test pixel to real-world coordinate conversion."""
        # Setup calibration
        points = [
            (100, 400, 0, 0),
            (500, 400, 10, 0),
            (200, 200, 0, 20),
            (400, 200, 10, 20)
        ]
        
        for px, py, rx, ry in points:
            self.calibrator.add_calibration_point(px, py, rx, ry)
        
        # Test conversion
        result = self.calibrator.pixel_to_real(300, 300)
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_distance_calculation(self):
        """Test real-world distance calculation."""
        # Setup calibration
        points = [
            (100, 400, 0, 0),
            (500, 400, 10, 0),
            (200, 200, 0, 20),
            (400, 200, 10, 20)
        ]
        
        for px, py, rx, ry in points:
            self.calibrator.add_calibration_point(px, py, rx, ry)
        
        # Calculate distance between two pixel points
        distance = self.calibrator.calculate_distance((100, 400), (500, 400))
        assert distance is not None
        assert distance > 0
    
    def test_calibration_zone(self):
        """Test calibration zone functionality."""
        zone = CalibrationZone(
            zone_id="test_zone",
            name="Test Zone",
            pixel_points=[(100, 100), (200, 100), (200, 200), (100, 200)],
            real_world_points=[(0, 0), (10, 0), (10, 10), (0, 10)],
            speed_limit=60.0,
            measurement_distance=20.0,
            entry_line=((100, 150), (200, 150)),
            exit_line=((100, 120), (200, 120))
        )
        
        self.calibrator.add_calibration_zone(zone)
        assert len(self.calibrator.calibration_zones) == 1
        assert "test_zone" in self.calibrator.calibration_zones
    
    def test_point_in_polygon(self):
        """Test point in polygon detection."""
        polygon = [(100, 100), (200, 100), (200, 200), (100, 200)]
        
        # Point inside
        assert self.calibrator._point_in_polygon((150, 150), polygon) is True
        
        # Point outside
        assert self.calibrator._point_in_polygon((50, 50), polygon) is False
    
    def test_default_highway_calibration(self):
        """Test default highway calibration creation."""
        result = self.calibrator.create_default_highway_calibration(800, 600)
        
        assert len(self.calibrator.calibration_points) > 0
        assert len(self.calibrator.calibration_zones) > 0
        assert "highway_main" in self.calibrator.calibration_zones
    
    def test_calibration_validation(self):
        """Test calibration validation."""
        # Test uncalibrated state
        validation = self.calibrator.validate_calibration()
        assert validation["is_valid"] is False
        
        # Add calibration and test
        points = [
            (100, 400, 0, 0),
            (500, 400, 10, 0),
            (200, 200, 0, 20),
            (400, 200, 10, 20)
        ]
        
        for px, py, rx, ry in points:
            self.calibrator.add_calibration_point(px, py, rx, ry)
        
        validation = self.calibrator.validate_calibration()
        assert "is_valid" in validation
        assert "calibration_error" in validation
        assert "confidence_score" in validation
    
    def test_save_load_calibration(self, tmp_path):
        """Test calibration save and load."""
        # Setup calibration
        points = [
            (100, 400, 0, 0),
            (500, 400, 10, 0),
            (200, 200, 0, 20),
            (400, 200, 10, 20)
        ]
        
        for px, py, rx, ry in points:
            self.calibrator.add_calibration_point(px, py, rx, ry)
        
        # Save calibration
        save_path = tmp_path / "test_calibration.json"
        result = self.calibrator.save_calibration(str(save_path))
        assert result is True
        assert save_path.exists()
        
        # Load calibration into new instance
        new_calibrator = CameraCalibrator()
        result = new_calibrator.load_calibration(str(save_path))
        assert result is True
        assert new_calibrator.is_calibrated == self.calibrator.is_calibrated
        assert len(new_calibrator.calibration_points) == len(self.calibrator.calibration_points)


class TestSpeedCalculator:
    """Test speed calculation functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.calibrator = CameraCalibrator()
        # Setup basic calibration
        points = [
            (100, 400, 0, 0),
            (500, 400, 10, 0),
            (200, 200, 0, 20),
            (400, 200, 10, 20)
        ]
        
        for px, py, rx, ry in points:
            self.calibrator.add_calibration_point(px, py, rx, ry)
        
        self.calculator = SpeedCalculator(self.calibrator)
    
    def create_test_trajectory(self) -> Trajectory:
        """Create a test trajectory."""
        trajectory = Trajectory(vehicle_id=1, max_history=100)
        
        # Add positions simulating vehicle movement
        base_time = time.time()
        positions = [
            (100, 300, base_time),
            (150, 280, base_time + 0.5),
            (200, 260, base_time + 1.0),
            (250, 240, base_time + 1.5),
            (300, 220, base_time + 2.0),
        ]
        
        for x, y, t in positions:
            trajectory.add_position((x, y), t)
        
        return trajectory
    
    def test_initialization(self):
        """Test calculator initialization."""
        assert self.calculator.calibrator == self.calibrator
        assert len(self.calculator.speed_measurements) == 0
        assert self.calculator.violation_threshold == 5.0
    
    def test_speed_calculation_from_trajectory(self):
        """Test speed calculation from trajectory."""
        trajectory = self.create_test_trajectory()
        
        measurement = self.calculator.calculate_speed_from_trajectory(trajectory)
        
        assert measurement is not None
        assert measurement.vehicle_id == 1
        assert measurement.speed_kmh > 0
        assert measurement.speed_mps > 0
        assert measurement.distance_traveled > 0
        assert measurement.time_elapsed > 0
        assert 0.0 <= measurement.confidence <= 1.0
    
    def test_instantaneous_speed_calculation(self):
        """Test instantaneous speed calculation."""
        trajectory = self.create_test_trajectory()
        
        speeds = self.calculator.calculate_instantaneous_speed(trajectory, window_size=3)
        
        assert len(speeds) > 0
        assert all(speed >= 0 for speed in speeds)
    
    def test_violation_detection(self):
        """Test speed violation detection."""
        # Create measurement with high speed
        measurement = SpeedMeasurement(
            vehicle_id=1,
            timestamp=time.time(),
            speed_kmh=120.0,  # High speed
            speed_mps=33.33,
            distance_traveled=20.0,
            time_elapsed=2.0,
            measurement_zone="test_zone",
            confidence=0.9,
            entry_point=(0, 0),
            exit_point=(20, 0),
            entry_time=time.time() - 2,
            exit_time=time.time(),
            pixel_trajectory=[(100, 300), (300, 220)],
            real_trajectory=[(0, 0), (20, 0)]
        )
        
        # Add zone with lower speed limit
        zone = CalibrationZone(
            zone_id="test_zone",
            name="Test Zone",
            pixel_points=[(100, 100), (200, 100), (200, 200), (100, 200)],
            real_world_points=[(0, 0), (10, 0), (10, 10), (0, 10)],
            speed_limit=80.0,  # Lower than measured speed
            measurement_distance=20.0,
            entry_line=((100, 150), (200, 150)),
            exit_line=((100, 120), (200, 120))
        )
        
        self.calibrator.add_calibration_zone(zone)
        
        violation = self.calculator.detect_speed_violation(measurement)
        
        assert violation is not None
        assert violation.vehicle_id == 1
        assert violation.measured_speed == 120.0
        assert violation.speed_limit == 80.0
        assert violation.violation_amount == 40.0
    
    def test_speed_smoothing(self):
        """Test speed smoothing for vehicles."""
        trajectory = self.create_test_trajectory()
        
        # Calculate multiple measurements
        for i in range(3):
            measurement = self.calculator.calculate_speed_from_trajectory(trajectory)
            if measurement:
                # Modify trajectory for next measurement
                trajectory.add_position((350 + i * 10, 200 - i * 5), time.time())
        
        smoothed_speed = self.calculator.get_smoothed_speed(1)
        assert smoothed_speed is not None
        assert smoothed_speed > 0
    
    def test_speed_unit_conversion(self):
        """Test speed unit conversion."""
        # Test KMH to MPS
        mps = self.calculator.convert_speed(36.0, SpeedUnit.KMH, SpeedUnit.MPS)
        assert abs(mps - 10.0) < 0.01
        
        # Test MPS to KMH
        kmh = self.calculator.convert_speed(10.0, SpeedUnit.MPS, SpeedUnit.KMH)
        assert abs(kmh - 36.0) < 0.01
        
        # Test KMH to MPH
        mph = self.calculator.convert_speed(100.0, SpeedUnit.KMH, SpeedUnit.MPH)
        assert mph > 0
    
    def test_statistics(self):
        """Test statistics calculation."""
        trajectory = self.create_test_trajectory()
        self.calculator.calculate_speed_from_trajectory(trajectory)
        
        stats = self.calculator.get_statistics()
        
        assert "total_measurements" in stats
        assert "vehicles_tracked" in stats
        assert "average_speed" in stats
        assert "speed_range" in stats
        assert "average_confidence" in stats
    
    def test_old_measurements_cleanup(self):
        """Test cleanup of old measurements."""
        trajectory = self.create_test_trajectory()
        measurement = self.calculator.calculate_speed_from_trajectory(trajectory)
        
        assert len(self.calculator.speed_measurements) > 0
        
        # Clear with very short max age
        self.calculator.clear_old_measurements(max_age=0.001)
        time.sleep(0.01)  # Wait to ensure measurements are old
        
        self.calculator.clear_old_measurements(max_age=0.001)
        # Should still have recent measurements, but this tests the cleanup logic


class TestSpeedAnalyzer:
    """Test complete speed analysis functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.detector = Mock()
        self.tracker = Mock()
        self.calibrator = CameraCalibrator()
        
        # Setup basic calibration
        points = [
            (100, 400, 0, 0),
            (500, 400, 10, 0),
            (200, 200, 0, 20),
            (400, 200, 10, 20)
        ]
        
        for px, py, rx, ry in points:
            self.calibrator.add_calibration_point(px, py, rx, ry)
        
        self.analyzer = SpeedAnalyzer(
            self.detector, self.tracker, self.calibrator, AnalysisMode.REALTIME
        )
    
    def test_initialization(self):
        """Test analyzer initialization."""
        assert self.analyzer.detector == self.detector
        assert self.analyzer.tracker == self.tracker
        assert self.analyzer.calibrator == self.calibrator
        assert self.analyzer.mode == AnalysisMode.REALTIME
        assert len(self.analyzer.violation_events) == 0
    
    def test_frame_analysis(self):
        """Test single frame analysis."""
        # Mock frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Mock detector response
        detection = Detection(
            class_id=0,
            class_name="car",
            confidence=0.9,
            bbox=(100, 100, 200, 200)
        )
        self.detector.detect.return_value = [detection]
        
        # Mock tracker response
        tracked_vehicle = TrackedVehicle(
            track_id=1,
            class_name="car",
            confidence=0.9,
            bbox=(100, 100, 200, 200),
            center_x=150,
            center_y=150,
            consecutive_frames=15  # Above minimum threshold
        )
        self.tracker.update.return_value = [tracked_vehicle]
        
        # Analyze frame
        result = self.analyzer.analyze_frame(frame)
        
        assert result.frame_id == 0
        assert len(result.detections) == 1
        assert len(result.tracked_vehicles) == 1
        assert result.processing_time > 0
        assert result.fps > 0
    
    def test_violation_event_creation(self):
        """Test violation event creation."""
        # Create mock violation and measurement
        violation = SpeedViolation(
            vehicle_id=1,
            timestamp=time.time(),
            measured_speed=120.0,
            speed_limit=80.0,
            violation_amount=40.0,
            violation_percentage=50.0,
            measurement_zone="test_zone",
            confidence=0.9
        )
        
        measurement = SpeedMeasurement(
            vehicle_id=1,
            timestamp=time.time(),
            speed_kmh=120.0,
            speed_mps=33.33,
            distance_traveled=20.0,
            time_elapsed=2.0,
            measurement_zone="test_zone",
            confidence=0.9,
            entry_point=(0, 0),
            exit_point=(20, 0),
            entry_time=time.time() - 2,
            exit_time=time.time(),
            pixel_trajectory=[(100, 300), (300, 220)],
            real_trajectory=[(0, 0), (20, 0)]
        )
        
        vehicle = TrackedVehicle(
            track_id=1,
            class_name="car",
            confidence=0.9,
            bbox=(100, 100, 200, 200),
            center_x=150,
            center_y=150,
            consecutive_frames=15
        )
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        event = self.analyzer._create_violation_event(violation, measurement, vehicle, frame, time.time())
        
        assert event.vehicle_id == 1
        assert event.violation == violation
        assert event.speed_measurement == measurement
        assert event.detection_box == (100, 100, 200, 200)
        assert event.vehicle_crop.shape == (100, 100, 3)
    
    def test_violation_cooldown(self):
        """Test violation cooldown mechanism."""
        violation = SpeedViolation(
            vehicle_id=1,
            timestamp=time.time(),
            measured_speed=120.0,
            speed_limit=80.0,
            violation_amount=40.0,
            violation_percentage=50.0,
            measurement_zone="test_zone",
            confidence=0.9
        )
        
        # First violation should be processed
        assert self.analyzer._should_process_violation(violation) is True
        
        # Add violation event
        self.analyzer.violation_events.append(Mock(vehicle_id=1, timestamp=time.time()))
        
        # Second violation for same vehicle should be rejected (cooldown)
        assert self.analyzer._should_process_violation(violation) is False
    
    def test_performance_statistics(self):
        """Test performance statistics tracking."""
        # Simulate some processing
        self.analyzer._update_performance_stats([], [], [], 0.05, 20.0)
        
        stats = self.analyzer.performance_stats
        assert stats["total_frames"] == 1
        assert stats["average_fps"] == 20.0
        assert stats["average_processing_time"] == 0.05
    
    def test_zone_statistics(self):
        """Test zone-based statistics."""
        # Add calibration zone
        zone = CalibrationZone(
            zone_id="test_zone",
            name="Test Zone",
            pixel_points=[(100, 100), (200, 100), (200, 200), (100, 200)],
            real_world_points=[(0, 0), (10, 0), (10, 10), (0, 10)],
            speed_limit=80.0,
            measurement_distance=20.0,
            entry_line=((100, 150), (200, 150)),
            exit_line=((100, 120), (200, 120))
        )
        
        self.analyzer.calibrator.add_calibration_zone(zone)
        
        zone_stats = self.analyzer.get_zone_statistics()
        
        assert "test_zone" in zone_stats
        assert zone_stats["test_zone"]["zone_name"] == "Test Zone"
        assert zone_stats["test_zone"]["speed_limit"] == 80.0
        assert zone_stats["test_zone"]["total_violations"] == 0
    
    def test_analysis_reset(self):
        """Test analysis state reset."""
        # Add some data
        self.analyzer.violation_events.append(Mock())
        self.analyzer.processing_times.append(0.05)
        self.analyzer.frame_count = 10
        
        # Reset
        self.analyzer.reset_analysis()
        
        assert len(self.analyzer.violation_events) == 0
        assert len(self.analyzer.processing_times) == 0
        assert self.analyzer.frame_count == 0
    
    def test_performance_summary(self):
        """Test performance summary generation."""
        summary = self.analyzer.get_performance_summary()
        
        assert "session_duration_minutes" in summary
        assert "total_frames_processed" in summary
        assert "performance_stats" in summary
        assert "memory_usage" in summary
        assert "calibration_status" in summary
    
    def test_violations_report_export(self, tmp_path):
        """Test violations report export."""
        report_path = tmp_path / "violations_report.json"
        
        result = self.analyzer.export_violations_report(str(report_path))
        
        assert result is True
        assert report_path.exists()
        
        # Verify report content
        import json
        with open(report_path) as f:
            report = json.load(f)
        
        assert "generation_time" in report
        assert "performance_stats" in report
        assert "violations" in report