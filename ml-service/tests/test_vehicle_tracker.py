"""
Comprehensive tests for VehicleTracker module.

Tests cover tracking functionality, trajectory management, and performance.
"""

import pytest
import numpy as np
import cv2
import time
from unittest.mock import Mock, patch, MagicMock
from typing import List

from src.tracking.vehicle_tracker import VehicleTracker, Detection, TrackedVehicle
from src.tracking.trajectory import Trajectory, TrajectoryManager, TrajectoryPoint

class TestDetection:
    """Test Detection dataclass."""
    
    def test_detection_creation(self):
        """Test Detection object creation."""
        detection = Detection(
            bbox=(100, 200, 300, 400),
            confidence=0.85,
            class_id=2,
            class_name="car"
        )
        
        assert detection.bbox == (100, 200, 300, 400)
        assert detection.confidence == 0.85
        assert detection.class_id == 2
        assert detection.class_name == "car"

class TestTrackedVehicle:
    """Test TrackedVehicle dataclass."""
    
    def test_tracked_vehicle_creation(self):
        """Test TrackedVehicle object creation."""
        vehicle = TrackedVehicle(
            track_id=1,
            bbox=(100, 200, 300, 400),
            confidence=0.9,
            class_name="car",
            center=(200, 300),
            trajectory=[(200, 300)],
            first_seen=time.time(),
            last_seen=time.time(),
            frame_count=1
        )
        
        assert vehicle.track_id == 1
        assert vehicle.bbox == (100, 200, 300, 400)
        assert vehicle.confidence == 0.9
        assert vehicle.class_name == "car"
        assert vehicle.center == (200, 300)
        assert len(vehicle.trajectory) == 1

class TestTrajectoryPoint:
    """Test TrajectoryPoint dataclass."""
    
    def test_trajectory_point_creation(self):
        """Test TrajectoryPoint creation."""
        timestamp = time.time()
        point = TrajectoryPoint(x=100, y=200, timestamp=timestamp, frame_number=1)
        
        assert point.x == 100
        assert point.y == 200
        assert point.timestamp == timestamp
        assert point.frame_number == 1

class TestTrajectory:
    """Test Trajectory class."""
    
    def test_trajectory_creation(self):
        """Test Trajectory object creation."""
        trajectory = Trajectory(track_id=1)
        
        assert trajectory.track_id == 1
        assert len(trajectory.points) == 0
        assert trajectory.total_distance == 0.0
        assert trajectory.avg_speed == 0.0
        assert trajectory.is_active is True
    
    def test_add_point(self):
        """Test adding points to trajectory."""
        trajectory = Trajectory(track_id=1)
        timestamp = time.time()
        
        trajectory.add_point(100, 200, timestamp, 1)
        
        assert len(trajectory.points) == 1
        assert trajectory.points[0].x == 100
        assert trajectory.points[0].y == 200
        assert trajectory.points[0].timestamp == timestamp
        assert trajectory.points[0].frame_number == 1
    
    def test_trajectory_metrics_calculation(self):
        """Test trajectory metrics calculation."""
        trajectory = Trajectory(track_id=1)
        base_time = time.time()
        
        # Add multiple points to test metrics
        trajectory.add_point(0, 0, base_time, 1)
        trajectory.add_point(100, 0, base_time + 1, 2)  # 100 pixels right in 1 second
        trajectory.add_point(200, 0, base_time + 2, 3)  # Another 100 pixels right in 1 second
        
        # Should have calculated distance and speed
        assert trajectory.total_distance == 200.0  # 100 + 100
        assert trajectory.avg_speed == 100.0  # 200 pixels / 2 seconds
        assert abs(trajectory.direction_vector[0] - 1.0) < 0.001  # Moving right
        assert abs(trajectory.direction_vector[1]) < 0.001  # No vertical movement
    
    def test_get_smoothed_trajectory(self):
        """Test trajectory smoothing."""
        trajectory = Trajectory(track_id=1)
        
        # Add some noisy points
        for i in range(10):
            x = i * 10 + np.random.randint(-2, 3)  # Add noise
            y = 100 + np.random.randint(-2, 3)
            trajectory.add_point(x, y)
        
        smoothed = trajectory.get_smoothed_trajectory(window_size=3)
        
        assert len(smoothed) == 10
        assert isinstance(smoothed[0], tuple)
        assert len(smoothed[0]) == 2
    
    def test_predict_next_position(self):
        """Test position prediction."""
        trajectory = Trajectory(track_id=1)
        base_time = time.time()
        
        # Add points moving right at 100 pixels/second
        trajectory.add_point(0, 100, base_time, 1)
        trajectory.add_point(100, 100, base_time + 1, 2)
        
        # Predict position 0.5 seconds ahead
        pred_x, pred_y = trajectory.predict_next_position(0.5)
        
        # Should predict around (150, 100) given the velocity
        assert abs(pred_x - 150) < 10
        assert abs(pred_y - 100) < 10
    
    def test_get_bounding_box(self):
        """Test trajectory bounding box calculation."""
        trajectory = Trajectory(track_id=1)
        
        trajectory.add_point(50, 100)
        trajectory.add_point(200, 50)
        trajectory.add_point(150, 300)
        
        x_min, y_min, x_max, y_max = trajectory.get_bounding_box()
        
        assert x_min == 50
        assert x_max == 200
        assert y_min == 50
        assert y_max == 300

class TestTrajectoryManager:
    """Test TrajectoryManager class."""
    
    def test_trajectory_manager_creation(self):
        """Test TrajectoryManager creation."""
        manager = TrajectoryManager(max_trajectories=100)
        
        assert len(manager.trajectories) == 0
        assert manager.max_trajectories == 100
    
    def test_update_trajectory(self):
        """Test trajectory updates."""
        manager = TrajectoryManager()
        
        # Update trajectory for new track
        manager.update_trajectory(1, (100, 200), time.time(), 1)
        
        assert 1 in manager.trajectories
        assert len(manager.trajectories[1].points) == 1
        assert manager.trajectories[1].points[0].x == 100
        assert manager.trajectories[1].points[0].y == 200
    
    def test_get_active_trajectories(self):
        """Test getting active trajectories."""
        manager = TrajectoryManager()
        current_time = time.time()
        
        # Add recent trajectory
        manager.update_trajectory(1, (100, 200), current_time)
        
        # Add old trajectory
        manager.update_trajectory(2, (300, 400), current_time - 60)
        
        active = manager.get_active_trajectories(max_age=30.0)
        
        assert 1 in active
        assert 2 not in active
    
    def test_remove_trajectory(self):
        """Test trajectory removal."""
        manager = TrajectoryManager()
        
        manager.update_trajectory(1, (100, 200))
        assert 1 in manager.trajectories
        
        removed = manager.remove_trajectory(1)
        assert removed is True
        assert 1 not in manager.trajectories
        
        # Try to remove non-existent trajectory
        removed = manager.remove_trajectory(999)
        assert removed is False
    
    def test_get_trajectory_statistics(self):
        """Test trajectory statistics calculation."""
        manager = TrajectoryManager()
        
        # Add some trajectories
        current_time = time.time()
        for track_id in range(3):
            for i in range(5):
                manager.update_trajectory(track_id, (i * 10, 100), current_time)
        
        stats = manager.get_trajectory_statistics()
        
        assert stats["total_trajectories"] == 3
        assert stats["active_trajectories"] == 3
        assert stats["avg_trajectory_length"] == 5.0
    
    def test_export_trajectories(self):
        """Test trajectory export functionality."""
        manager = TrajectoryManager()
        
        # Add test trajectory
        manager.update_trajectory(1, (100, 200), time.time(), 1)
        manager.update_trajectory(1, (110, 210), time.time(), 2)
        
        export_data = manager.export_trajectories()
        
        assert "timestamp" in export_data
        assert "trajectories" in export_data
        assert 1 in export_data["trajectories"]
        assert len(export_data["trajectories"][1]["points"]) == 2

@patch('src.tracking.vehicle_tracker.DeepSort')
class TestVehicleTracker:
    """Test VehicleTracker class with mocked DeepSort."""
    
    def test_vehicle_tracker_initialization(self, mock_deepsort):
        """Test VehicleTracker initialization."""
        tracker = VehicleTracker()
        
        assert tracker is not None
        assert mock_deepsort.called
        assert len(tracker.tracked_vehicles) == 0
        assert tracker.frame_count == 0
    
    def test_prepare_detections(self, mock_deepsort):
        """Test detection preparation for DeepSORT."""
        tracker = VehicleTracker()
        
        detections = [
            Detection(bbox=(100, 200, 300, 400), confidence=0.9, class_id=2, class_name="car"),
            Detection(bbox=(500, 600, 700, 800), confidence=0.8, class_id=2, class_name="truck")
        ]
        
        det_list = tracker._prepare_detections(detections)
        
        assert len(det_list) == 2
        assert det_list[0] == [100, 200, 300, 400, 0.9, "car"]
        assert det_list[1] == [500, 600, 700, 800, 0.8, "truck"]
    
    def test_get_track_color(self, mock_deepsort):
        """Test consistent color generation for tracks."""
        tracker = VehicleTracker()
        
        color1 = tracker._get_track_color(1)
        color2 = tracker._get_track_color(1)  # Same ID
        color3 = tracker._get_track_color(2)  # Different ID
        
        assert color1 == color2  # Same ID should give same color
        assert color1 != color3  # Different IDs should give different colors
        assert len(color1) == 3  # RGB tuple
    
    def test_update_with_empty_detections(self, mock_deepsort):
        """Test tracker update with no detections."""
        # Mock DeepSort instance
        mock_tracker_instance = Mock()
        mock_tracker_instance.update_tracks.return_value = []
        mock_deepsort.return_value = mock_tracker_instance
        
        tracker = VehicleTracker()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        result = tracker.update([], frame)
        
        assert len(result) == 0
        mock_tracker_instance.update_tracks.assert_called_once()
    
    def test_update_with_detections(self, mock_deepsort):
        """Test tracker update with detections."""
        # Mock track object
        mock_track = Mock()
        mock_track.is_confirmed.return_value = True
        mock_track.track_id = 1
        mock_track.to_ltrb.return_value = np.array([100, 200, 300, 400])
        mock_track.confidence = 0.9
        mock_track.get_class = Mock(return_value="car")
        
        # Mock DeepSort instance
        mock_tracker_instance = Mock()
        mock_tracker_instance.update_tracks.return_value = [mock_track]
        mock_deepsort.return_value = mock_tracker_instance
        
        tracker = VehicleTracker()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        detections = [
            Detection(bbox=(100, 200, 300, 400), confidence=0.9, class_id=2, class_name="car")
        ]
        
        result = tracker.update(detections, frame)
        
        assert len(result) == 1
        assert result[0].track_id == 1
        assert result[0].bbox == (100, 200, 300, 400)
        assert result[0].center == (200, 300)
    
    def test_get_tracking_stats(self, mock_deepsort):
        """Test tracking statistics retrieval."""
        tracker = VehicleTracker()
        tracker.total_frames = 100
        tracker.total_processing_time = 5.0  # 5 seconds total
        
        stats = tracker.get_tracking_stats()
        
        assert stats["total_frames"] == 100
        assert stats["avg_processing_time_ms"] == 50.0  # 5000ms / 100 frames
        assert stats["fps"] == 20.0  # 1 / 0.05 seconds
        assert "active_vehicles" in stats
    
    def test_visualize_tracks(self, mock_deepsort):
        """Test track visualization."""
        tracker = VehicleTracker()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Create a tracked vehicle
        vehicle = TrackedVehicle(
            track_id=1,
            bbox=(100, 200, 300, 400),
            confidence=0.9,
            class_name="car",
            center=(200, 300),
            trajectory=[(190, 290), (195, 295), (200, 300)],
            first_seen=time.time(),
            last_seen=time.time(),
            frame_count=3
        )
        
        vis_frame = tracker.visualize_tracks(frame, [vehicle])
        
        # Check that the frame was modified (visualization added)
        assert not np.array_equal(frame, vis_frame)
        assert vis_frame.shape == frame.shape
    
    def test_reset_tracker(self, mock_deepsort):
        """Test tracker reset functionality."""
        tracker = VehicleTracker()
        tracker.frame_count = 100
        tracker.total_frames = 50
        tracker.tracked_vehicles[1] = Mock()
        
        tracker.reset()
        
        assert tracker.frame_count == 0
        assert tracker.total_frames == 0
        assert len(tracker.tracked_vehicles) == 0
        # DeepSort should be reinitialized
        assert mock_deepsort.call_count >= 2  # Once in __init__, once in reset

class TestIntegration:
    """Integration tests for tracking module."""
    
    @patch('src.tracking.vehicle_tracker.DeepSort')
    def test_full_tracking_pipeline(self, mock_deepsort):
        """Test complete tracking pipeline."""
        # Setup mock
        mock_track = Mock()
        mock_track.is_confirmed.return_value = True
        mock_track.track_id = 1
        mock_track.to_ltrb.return_value = np.array([100, 200, 300, 400])
        mock_track.confidence = 0.9
        mock_track.get_class = Mock(return_value="car")
        
        mock_tracker_instance = Mock()
        mock_tracker_instance.update_tracks.return_value = [mock_track]
        mock_deepsort.return_value = mock_tracker_instance
        
        # Create tracker
        tracker = VehicleTracker()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Simulate multiple frames with same vehicle
        for i in range(5):
            detections = [
                Detection(
                    bbox=(100 + i*2, 200 + i*2, 300 + i*2, 400 + i*2),
                    confidence=0.9,
                    class_id=2,
                    class_name="car"
                )
            ]
            
            tracked_vehicles = tracker.update(detections, frame)
            
            assert len(tracked_vehicles) == 1
            assert tracked_vehicles[0].track_id == 1
            assert tracked_vehicles[0].frame_count == i + 1
        
        # Check trajectory manager has data
        trajectories = tracker.trajectory_manager.get_all_trajectories()
        assert 1 in trajectories
        assert len(trajectories[1].points) == 5
        
        # Test statistics
        stats = tracker.get_tracking_stats()
        assert stats["total_frames"] == 5
        assert stats["active_vehicles"] == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])