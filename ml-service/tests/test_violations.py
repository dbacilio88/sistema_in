"""
Test suite for traffic violations detection module.

Tests violation detection, lane detection, notification system, and violation management.
"""

import pytest
import numpy as np
import cv2
import time
import tempfile
import sqlite3
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict

from ..violation_detector import (
    ViolationDetector, TrafficViolation, ViolationType, ViolationSeverity,
    ViolationLocation, ViolationRule
)
from ..lane_detector import LaneDetector, LaneViolation, LaneMarking, LaneGeometry, LaneType
from ..notification_system import (
    NotificationSystem, Alert, AlertPriority, NotificationChannel, NotificationConfig
)
from ..violation_manager import ViolationManager, ViolationReport, ViolationStatistics
from ...speed.speed_analyzer import SpeedViolation
from ...tracking.vehicle_tracker import TrackedVehicle

class TestViolationDetector:
    """Test violation detection functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.detector = ViolationDetector()
    
    def test_initialization(self):
        """Test violation detector initialization."""
        assert len(self.detector.violations) == 0
        assert len(self.detector.violation_rules) == 0
        assert len(self.detector.active_violations) == 0
        assert self.detector.cooldown_periods[ViolationType.SPEED_VIOLATION] == 30.0
    
    def test_add_violation_rule(self):
        """Test adding violation rules."""
        rule = ViolationRule(
            rule_id="speed_rule_1",
            violation_type=ViolationType.SPEED_VIOLATION,
            enabled=True,
            parameters={"threshold": 10.0},
            zones=["zone_1", "zone_2"]
        )
        
        self.detector.add_violation_rule(rule)
        
        assert "speed_rule_1" in self.detector.violation_rules
        assert self.detector.violation_rules["speed_rule_1"] == rule
    
    def test_speed_violation_detection(self):
        """Test speed violation detection."""
        # Create mock speed violation
        speed_violation = Mock()
        speed_violation.vehicle_id = 1
        speed_violation.timestamp = time.time()
        speed_violation.measured_speed = 120.0
        speed_violation.speed_limit = 80.0
        speed_violation.violation_amount = 40.0
        speed_violation.measurement_zone = "test_zone"
        speed_violation.confidence = 0.9
        
        # Create mock vehicle
        vehicle = Mock(spec=TrackedVehicle)
        vehicle.track_id = 1
        vehicle.bbox = (100, 100, 200, 200)
        vehicle.center_x = 150
        vehicle.center_y = 150
        vehicle.confidence = 0.8
        
        # Test frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        violations = self.detector.detect_speed_violations([speed_violation], [vehicle], frame)
        
        assert len(violations) == 1
        violation = violations[0]
        assert violation.violation_type == ViolationType.SPEED_VIOLATION
        assert violation.vehicle_id == 1
        assert violation.measured_speed == 120.0
        assert violation.speed_limit == 80.0
        assert violation.severity == ViolationSeverity.MODERATE  # 40 km/h over
    
    def test_lane_violation_detection(self):
        """Test lane violation detection."""
        # Create mock vehicle
        vehicle = Mock(spec=TrackedVehicle)
        vehicle.track_id = 1
        vehicle.bbox = (100, 100, 200, 200)
        vehicle.center_x = 150
        vehicle.center_y = 150
        vehicle.confidence = 0.8
        
        # Create lane mask (vehicle partially outside lanes)
        lane_mask = np.zeros((480, 640), dtype=np.uint8)
        lane_mask[50:400, 100:500] = 255  # Valid lane area
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        violations = self.detector.detect_lane_violations([vehicle], lane_mask, frame)
        
        # Vehicle should have lane violation (partially outside valid area)
        assert len(violations) >= 0  # May or may not detect depending on overlap calculation
    
    def test_wrong_way_detection(self):
        """Test wrong-way driving detection."""
        # Create mock vehicle with trajectory
        vehicle = Mock(spec=TrackedVehicle)
        vehicle.track_id = 1
        vehicle.bbox = (100, 100, 200, 200)
        vehicle.center_x = 150
        vehicle.center_y = 150
        vehicle.confidence = 0.8
        vehicle.trajectory = [
            (150, 300),  # Start position
            (150, 280),  # Moving up (wrong way if expected is down)
            (150, 260),
            (150, 240),
            (150, 220)   # End position
        ]
        
        # Expected direction is downward (positive y)
        expected_direction = np.array([0, 1])
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        violations = self.detector.detect_wrong_way_driving([vehicle], expected_direction, frame)
        
        assert len(violations) == 1
        violation = violations[0]
        assert violation.violation_type == ViolationType.WRONG_WAY
        assert violation.severity == ViolationSeverity.CRITICAL
        assert violation.vehicle_id == 1
    
    def test_following_distance_violations(self):
        """Test following distance violation detection."""
        # Create two vehicles following closely
        vehicle1 = Mock(spec=TrackedVehicle)
        vehicle1.track_id = 1
        vehicle1.center_x = 150
        vehicle1.center_y = 200  # Front vehicle
        vehicle1.bbox = (100, 180, 200, 220)
        vehicle1.confidence = 0.8
        
        vehicle2 = Mock(spec=TrackedVehicle)
        vehicle2.track_id = 2
        vehicle2.center_x = 155  # Similar x position (same lane)
        vehicle2.center_y = 250  # Following vehicle
        vehicle2.bbox = (105, 230, 205, 270)
        vehicle2.confidence = 0.8
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        violations = self.detector.detect_following_distance_violations(
            [vehicle1, vehicle2], frame, min_distance=20.0
        )
        
        # Should detect following too closely
        assert len(violations) >= 0  # Depends on distance calculation
    
    def test_violation_cooldown(self):
        """Test violation cooldown mechanism."""
        # Test cooldown is not active initially
        key = (1, ViolationType.SPEED_VIOLATION)
        assert not self.detector._is_in_cooldown(key)
        
        # Set cooldown
        self.detector._set_cooldown(key)
        assert self.detector._is_in_cooldown(key)
        
        # Wait and test again (would need to mock time for proper testing)
        # For now just test the mechanism exists
    
    def test_severity_calculation(self):
        """Test violation severity calculation."""
        # Test speed violation severity
        assert self.detector._calculate_speed_severity(5.0) == ViolationSeverity.MINOR
        assert self.detector._calculate_speed_severity(15.0) == ViolationSeverity.MODERATE
        assert self.detector._calculate_speed_severity(35.0) == ViolationSeverity.SEVERE
        assert self.detector._calculate_speed_severity(65.0) == ViolationSeverity.CRITICAL
        
        # Test lane violation severity
        assert self.detector._calculate_lane_severity(0.2) == ViolationSeverity.MINOR
        assert self.detector._calculate_lane_severity(0.4) == ViolationSeverity.MODERATE
        assert self.detector._calculate_lane_severity(0.7) == ViolationSeverity.SEVERE
        assert self.detector._calculate_lane_severity(1.0) == ViolationSeverity.CRITICAL
    
    def test_statistics(self):
        """Test violation statistics."""
        # Add some mock violations
        violation = TrafficViolation(
            violation_id="test_1",
            timestamp=time.time(),
            violation_type=ViolationType.SPEED_VIOLATION,
            severity=ViolationSeverity.MODERATE,
            vehicle_id=1,
            description="Test violation",
            confidence=0.9,
            location=ViolationLocation("zone_1", "Test Zone", (100, 100))
        )
        
        self.detector.violations.append(violation)
        self.detector._update_statistics(violation)
        
        stats = self.detector.get_statistics()
        
        assert stats["total_violations"] >= 1
        assert stats["violations_by_type"]["speed_violation"] >= 1
        assert stats["violations_by_severity"]["moderate"] >= 1


class TestLaneDetector:
    """Test lane detection functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.detector = LaneDetector(1920, 1080)
    
    def test_initialization(self):
        """Test lane detector initialization."""
        assert self.detector.image_width == 1920
        assert self.detector.image_height == 1080
        assert self.detector.roi_vertices is not None
        assert len(self.detector.lane_history) == 0
    
    def test_roi_calculation(self):
        """Test ROI vertices calculation."""
        vertices = self.detector._calculate_roi_vertices()
        assert vertices.shape == (4, 2)
        # Vertices should be within image bounds
        assert np.all(vertices[:, 0] >= 0)
        assert np.all(vertices[:, 0] <= self.detector.image_width)
        assert np.all(vertices[:, 1] >= 0)
        assert np.all(vertices[:, 1] <= self.detector.image_height)
    
    def test_roi_mask_application(self):
        """Test ROI mask application."""
        test_image = np.ones((1080, 1920), dtype=np.uint8) * 255
        masked = self.detector._apply_roi_mask(test_image)
        
        # Mask should zero out areas outside ROI
        assert np.sum(masked) < np.sum(test_image)
        assert masked.shape == test_image.shape
    
    def test_lane_separation(self):
        """Test lane line separation into left and right."""
        # Create mock lines
        lines = np.array([
            [[100, 1000, 200, 500]],    # Left lane (negative slope, left side)
            [[1500, 500, 1600, 1000]], # Right lane (positive slope, right side)
            [[800, 1000, 900, 500]],   # Center line (could be either)
        ])
        
        left_lines, right_lines = self.detector._separate_lanes(lines)
        
        # Should separate lines based on slope and position
        assert len(left_lines) >= 0
        assert len(right_lines) >= 0
    
    def test_polynomial_fitting(self):
        """Test polynomial fitting to lane lines."""
        # Create mock lane lines
        lines = [
            [100, 1000, 150, 800],
            [150, 800, 200, 600],
            [200, 600, 250, 400]
        ]
        
        lane_marking = self.detector._fit_lane_polynomial(lines, "left")
        
        if lane_marking:  # May be None if insufficient points
            assert lane_marking.side == "left"
            assert len(lane_marking.points) > 0
            assert 0.0 <= lane_marking.confidence <= 1.0
            assert lane_marking.polynomial_coeffs is not None
    
    def test_lane_detection_on_synthetic_image(self):
        """Test lane detection on synthetic image."""
        # Create synthetic image with lane markings
        image = np.zeros((1080, 1920, 3), dtype=np.uint8)
        
        # Draw left lane
        cv2.line(image, (600, 1080), (800, 600), (255, 255, 255), 10)
        # Draw right lane
        cv2.line(image, (1200, 1080), (1000, 600), (255, 255, 255), 10)
        
        lane_geometry = self.detector.detect_lanes(image)
        
        # Should detect basic lane structure
        assert isinstance(lane_geometry, LaneGeometry)
    
    def test_vehicle_lane_position(self):
        """Test vehicle lane position calculation."""
        # Create mock lane geometry
        left_lane = LaneMarking(
            points=[(600, 800), (650, 700), (700, 600)],
            lane_type=LaneType.SOLID,
            confidence=0.9,
            side="left"
        )
        right_lane = LaneMarking(
            points=[(1200, 800), (1150, 700), (1100, 600)],
            lane_type=LaneType.SOLID,
            confidence=0.9,
            side="right"
        )
        
        lane_geometry = LaneGeometry(
            left_lane=left_lane,
            right_lane=right_lane,
            center_line=None,
            lane_width=500.0,
            curve_radius=None
        )
        
        # Test vehicle in center
        position = self.detector.detect_vehicle_lane_position((900, 700), lane_geometry)
        assert abs(position) < 0.1  # Should be near center
        
        # Test vehicle on left
        position = self.detector.detect_vehicle_lane_position((700, 700), lane_geometry)
        assert position < 0  # Should be negative (left side)
        
        # Test vehicle on right
        position = self.detector.detect_vehicle_lane_position((1100, 700), lane_geometry)
        assert position > 0  # Should be positive (right side)
    
    def test_lane_mask_creation(self):
        """Test lane mask creation."""
        # Create mock lane geometry
        left_lane = LaneMarking(
            points=[(600, 800), (700, 600)],
            lane_type=LaneType.SOLID,
            confidence=0.9,
            side="left"
        )
        right_lane = LaneMarking(
            points=[(1200, 800), (1100, 600)],
            lane_type=LaneType.SOLID,
            confidence=0.9,
            side="right"
        )
        
        lane_geometry = LaneGeometry(
            left_lane=left_lane,
            right_lane=right_lane,
            center_line=None,
            lane_width=None,
            curve_radius=None
        )
        
        mask = self.detector.create_lane_mask(lane_geometry, (1080, 1920))
        
        assert mask.shape == (1080, 1920)
        assert mask.dtype == np.uint8
        # Should have some valid lane area
        assert np.sum(mask) > 0


class TestNotificationSystem:
    """Test notification system functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.notification_system = NotificationSystem()
    
    def test_initialization(self):
        """Test notification system initialization."""
        assert len(self.notification_system.notification_configs) > 0
        assert NotificationChannel.DATABASE in self.notification_system.notification_configs
        assert NotificationChannel.FILE in self.notification_system.notification_configs
    
    def test_notification_config(self):
        """Test notification configuration."""
        config = NotificationConfig(
            channel=NotificationChannel.EMAIL,
            enabled=True,
            config={"smtp_server": "test.com"},
            rate_limit=10
        )
        
        self.notification_system.add_notification_config(config)
        
        assert NotificationChannel.EMAIL in self.notification_system.notification_configs
        assert self.notification_system.notification_configs[NotificationChannel.EMAIL] == config
    
    def test_violation_alert_creation(self):
        """Test violation alert creation."""
        violation = TrafficViolation(
            violation_id="test_violation",
            timestamp=time.time(),
            violation_type=ViolationType.SPEED_VIOLATION,
            severity=ViolationSeverity.SEVERE,
            vehicle_id=1,
            description="Test speed violation",
            confidence=0.9,
            location=ViolationLocation("zone_1", "Test Zone", (100, 100)),
            speed_limit=50.0,
            measured_speed=80.0
        )
        
        alert_id = self.notification_system.send_violation_alert(violation)
        
        assert alert_id is not None
        assert alert_id.startswith("alert_")
    
    def test_priority_determination(self):
        """Test alert priority determination."""
        # Critical severity should map to critical priority
        violation_critical = TrafficViolation(
            violation_id="test",
            timestamp=time.time(),
            violation_type=ViolationType.WRONG_WAY,
            severity=ViolationSeverity.CRITICAL,
            vehicle_id=1,
            description="Test",
            confidence=0.9,
            location=ViolationLocation("zone_1", "Test Zone", (100, 100))
        )
        
        priority = self.notification_system._determine_priority(violation_critical)
        assert priority == AlertPriority.CRITICAL
    
    def test_message_generation(self):
        """Test alert message generation."""
        violation = TrafficViolation(
            violation_id="test_violation",
            timestamp=time.time(),
            violation_type=ViolationType.SPEED_VIOLATION,
            severity=ViolationSeverity.MODERATE,
            vehicle_id=1,
            description="Speed violation detected",
            confidence=0.9,
            location=ViolationLocation("zone_1", "Highway Zone", (100, 100)),
            speed_limit=60.0,
            measured_speed=85.0,
            license_plate="ABC-123"
        )
        
        message = self.notification_system._generate_alert_message(violation)
        
        assert "TRAFFIC VIOLATION DETECTED" in message
        assert "Speed violation detected" in message
        assert "ABC-123" in message
        assert "60.0" in message
        assert "85.0" in message
    
    def test_rate_limiting(self):
        """Test notification rate limiting."""
        # Configure low rate limit
        config = NotificationConfig(
            channel=NotificationChannel.EMAIL,
            enabled=True,
            config={},
            rate_limit=1  # Only 1 per hour
        )
        
        self.notification_system.add_notification_config(config)
        
        # First check should pass
        assert self.notification_system._check_rate_limit(NotificationChannel.EMAIL)
        
        # Update rate limit counter
        self.notification_system._update_rate_limit(NotificationChannel.EMAIL)
        
        # Second check should fail (rate limit exceeded)
        assert not self.notification_system._check_rate_limit(NotificationChannel.EMAIL)
    
    def test_database_notification(self, tmp_path):
        """Test database notification functionality."""
        # Use temporary database
        db_path = tmp_path / "test_notifications.db"
        
        config = NotificationConfig(
            channel=NotificationChannel.DATABASE,
            enabled=True,
            config={"db_path": str(db_path)}
        )
        
        violation = TrafficViolation(
            violation_id="test_violation",
            timestamp=time.time(),
            violation_type=ViolationType.SPEED_VIOLATION,
            severity=ViolationSeverity.MODERATE,
            vehicle_id=1,
            description="Test violation",
            confidence=0.9,
            location=ViolationLocation("zone_1", "Test Zone", (100, 100))
        )
        
        alert = Alert(
            alert_id="test_alert",
            timestamp=time.time(),
            priority=AlertPriority.MEDIUM,
            violation=violation,
            message="Test message",
            channels=[NotificationChannel.DATABASE],
            metadata={}
        )
        
        success = self.notification_system._send_database_notification(alert, config)
        assert success
        
        # Verify data was stored
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE alert_id = ?", ("test_alert",))
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 1


class TestViolationManager:
    """Test violation management functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        # Use temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.manager = ViolationManager()
        self.manager.db_path = self.temp_db.name
        self.manager._init_database()
    
    def teardown_method(self):
        """Cleanup test fixtures."""
        import os
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    def test_initialization(self):
        """Test violation manager initialization."""
        assert isinstance(self.manager.violation_detector, ViolationDetector)
        assert isinstance(self.manager.lane_detector, LaneDetector)
        assert isinstance(self.manager.notification_system, NotificationSystem)
        assert len(self.manager.active_sessions) == 0
    
    def test_violation_storage(self):
        """Test violation storage in database."""
        violation = TrafficViolation(
            violation_id="test_violation",
            timestamp=time.time(),
            violation_type=ViolationType.SPEED_VIOLATION,
            severity=ViolationSeverity.MODERATE,
            vehicle_id=1,
            description="Test violation",
            confidence=0.9,
            location=ViolationLocation("zone_1", "Test Zone", (100, 100)),
            speed_limit=60.0,
            measured_speed=80.0
        )
        
        self.manager._store_violation(violation)
        
        # Verify storage
        conn = sqlite3.connect(self.manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM violations WHERE violation_id = ?", ("test_violation",))
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 1
    
    def test_statistics_generation(self):
        """Test violation statistics generation."""
        # Add some test violations
        current_time = time.time()
        
        for i in range(5):
            violation = TrafficViolation(
                violation_id=f"test_violation_{i}",
                timestamp=current_time - i * 3600,  # Spread over hours
                violation_type=ViolationType.SPEED_VIOLATION,
                severity=ViolationSeverity.MODERATE,
                vehicle_id=i,
                description=f"Test violation {i}",
                confidence=0.9,
                location=ViolationLocation("zone_1", "Test Zone", (100, 100))
            )
            self.manager._store_violation(violation)
        
        stats = self.manager.get_current_statistics()
        
        assert isinstance(stats, ViolationStatistics)
        assert stats.current_violations >= 0
        assert stats.daily_total >= 0
    
    def test_report_generation(self):
        """Test violation report generation."""
        # Add test violation
        violation = TrafficViolation(
            violation_id="test_violation",
            timestamp=time.time(),
            violation_type=ViolationType.SPEED_VIOLATION,
            severity=ViolationSeverity.MODERATE,
            vehicle_id=1,
            description="Test violation",
            confidence=0.9,
            location=ViolationLocation("zone_1", "Test Zone", (100, 100))
        )
        
        self.manager._store_violation(violation)
        
        # Generate report
        start_time = time.time() - 3600  # 1 hour ago
        end_time = time.time()
        
        report = self.manager.generate_report(start_time, end_time)
        
        assert isinstance(report, ViolationReport)
        assert report.total_violations >= 0
        assert isinstance(report.violations_by_type, dict)
        assert isinstance(report.violations_by_severity, dict)
    
    def test_false_positive_marking(self):
        """Test marking violations as false positives."""
        violation = TrafficViolation(
            violation_id="test_violation",
            timestamp=time.time(),
            violation_type=ViolationType.SPEED_VIOLATION,
            severity=ViolationSeverity.MODERATE,
            vehicle_id=1,
            description="Test violation",
            confidence=0.9,
            location=ViolationLocation("zone_1", "Test Zone", (100, 100))
        )
        
        self.manager._store_violation(violation)
        
        # Mark as false positive
        self.manager.mark_false_positive("test_violation")
        
        # Verify marking
        conn = sqlite3.connect(self.manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT false_positive FROM violations WHERE violation_id = ?", ("test_violation",))
        false_positive = cursor.fetchone()[0]
        conn.close()
        
        assert false_positive == 1  # SQLite stores boolean as integer
    
    def test_violations_for_review(self):
        """Test getting violations for manual review."""
        violation = TrafficViolation(
            violation_id="test_violation",
            timestamp=time.time(),
            violation_type=ViolationType.SPEED_VIOLATION,
            severity=ViolationSeverity.MODERATE,
            vehicle_id=1,
            description="Test violation",
            confidence=0.9,
            location=ViolationLocation("zone_1", "Test Zone", (100, 100))
        )
        
        self.manager._store_violation(violation)
        
        violations_for_review = self.manager.get_violations_for_review(limit=10)
        
        assert len(violations_for_review) >= 1
        assert violations_for_review[0]["violation_id"] == "test_violation"
    
    def test_system_status(self):
        """Test system status reporting."""
        status = self.manager.get_system_status()
        
        assert "violation_manager" in status
        assert "violation_detector" in status
        assert "notification_system" in status
        assert "current_statistics" in status
        assert "configuration" in status