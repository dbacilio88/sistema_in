"""
Test tracking integration with YOLOv8 detector.

Integration tests combining detection and tracking components.
"""

import pytest
import numpy as np
import cv2
import time
from unittest.mock import Mock, patch
from typing import List

from src.detection.vehicle_detector import YOLOv8VehicleDetector
from src.tracking.vehicle_tracker import VehicleTracker, Detection
from src.tracking.trajectory import TrajectoryManager

class TestTrackingIntegration:
    """Integration tests for detection + tracking pipeline."""
    
    @patch('src.detection.vehicle_detector.ort.InferenceSession')
    @patch('src.tracking.vehicle_tracker.DeepSort')
    def test_detection_tracking_pipeline(self, mock_deepsort, mock_ort):
        """Test complete detection -> tracking pipeline."""
        # Mock ONNX Runtime
        mock_session = Mock()
        mock_session.run.return_value = [
            # Mock YOLOv8 output: boxes, scores, class_ids
            np.array([[[100, 200, 300, 400, 0.9, 2]]]),  # One car detection
        ]
        mock_ort.return_value = mock_session
        
        # Mock DeepSORT
        mock_track = Mock()
        mock_track.is_confirmed.return_value = True
        mock_track.track_id = 1
        mock_track.to_ltrb.return_value = np.array([100, 200, 300, 400])
        mock_track.confidence = 0.9
        mock_track.get_class = Mock(return_value="car")
        
        mock_tracker_instance = Mock()
        mock_tracker_instance.update_tracks.return_value = [mock_track]
        mock_deepsort.return_value = mock_tracker_instance
        
        # Create components
        detector = YOLOv8VehicleDetector()
        tracker = VehicleTracker()
        
        # Create test frame
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Run detection
        detection_results = detector.detect(frame)
        
        # Convert to Detection objects for tracker
        detections = []
        for result in detection_results:
            detections.append(Detection(
                bbox=result["bbox"],
                confidence=result["confidence"],
                class_id=result["class_id"],
                class_name=result["class_name"]
            ))
        
        # Run tracking
        tracked_vehicles = tracker.update(detections, frame)
        
        # Verify pipeline
        assert len(tracked_vehicles) == 1
        assert tracked_vehicles[0].track_id == 1
        assert tracked_vehicles[0].class_name == "car"
        assert tracked_vehicles[0].confidence == 0.9
    
    @patch('src.detection.vehicle_detector.ort.InferenceSession')
    @patch('src.tracking.vehicle_tracker.DeepSort')
    def test_multi_frame_tracking(self, mock_deepsort, mock_ort):
        """Test tracking across multiple frames."""
        # Mock ONNX Runtime - simulate moving vehicle
        def mock_inference(input_data):
            frame_num = getattr(mock_inference, 'frame_num', 0)
            mock_inference.frame_num = frame_num + 1
            
            # Simulate vehicle moving right
            x_offset = frame_num * 10
            return [np.array([[[100 + x_offset, 200, 300 + x_offset, 400, 0.9, 2]]])]
        
        mock_session = Mock()
        mock_session.run.side_effect = mock_inference
        mock_ort.return_value = mock_session
        
        # Mock DeepSORT - maintain same track ID
        def mock_update_tracks(detections, frame=None):
            if detections:
                mock_track = Mock()
                mock_track.is_confirmed.return_value = True
                mock_track.track_id = 1  # Same ID across frames
                # Use detection bbox for position
                bbox = detections[0][:4]
                mock_track.to_ltrb.return_value = np.array(bbox)
                mock_track.confidence = 0.9
                mock_track.get_class = Mock(return_value="car")
                return [mock_track]
            return []
        
        mock_tracker_instance = Mock()
        mock_tracker_instance.update_tracks.side_effect = mock_update_tracks
        mock_deepsort.return_value = mock_tracker_instance
        
        # Create components
        detector = YOLOv8VehicleDetector()
        tracker = VehicleTracker()
        
        # Process multiple frames
        for frame_idx in range(5):
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            # Detection
            detection_results = detector.detect(frame)
            detections = [
                Detection(
                    bbox=result["bbox"],
                    confidence=result["confidence"],
                    class_id=result["class_id"],
                    class_name=result["class_name"]
                )
                for result in detection_results
            ]
            
            # Tracking
            tracked_vehicles = tracker.update(detections, frame)
            
            # Verify continuous tracking
            assert len(tracked_vehicles) == 1
            assert tracked_vehicles[0].track_id == 1
            assert tracked_vehicles[0].frame_count == frame_idx + 1
        
        # Check trajectory was built
        trajectories = tracker.trajectory_manager.get_all_trajectories()
        assert 1 in trajectories
        assert len(trajectories[1].points) == 5
    
    def test_trajectory_analysis(self):
        """Test trajectory analysis capabilities."""
        manager = TrajectoryManager()
        
        # Simulate vehicle moving in a pattern
        base_time = time.time()
        positions = [
            (100, 200), (110, 205), (120, 210), (130, 215), (140, 220)
        ]
        
        for i, (x, y) in enumerate(positions):
            manager.update_trajectory(1, (x, y), base_time + i * 0.1, i + 1)
        
        trajectory = manager.get_trajectory(1)
        
        # Test trajectory metrics
        assert trajectory.total_distance > 0
        assert trajectory.avg_speed > 0
        assert len(trajectory.direction_vector) == 2
        
        # Test smoothing
        smoothed = trajectory.get_smoothed_trajectory()
        assert len(smoothed) == len(positions)
        
        # Test prediction
        pred_x, pred_y = trajectory.predict_next_position(0.1)
        assert pred_x > 140  # Should predict further right
        assert pred_y > 220  # Should predict further down
    
    def test_zone_based_analysis(self):
        """Test zone-based trajectory analysis."""
        manager = TrajectoryManager()
        
        # Create trajectories passing through different zones
        # Vehicle 1: passes through zone (100, 100, 200, 200)
        for i in range(5):
            x = 50 + i * 30  # 50, 80, 110, 140, 170
            y = 150
            manager.update_trajectory(1, (x, y), time.time() + i * 0.1)
        
        # Vehicle 2: doesn't pass through zone
        for i in range(5):
            x = 300 + i * 10
            y = 300
            manager.update_trajectory(2, (x, y), time.time() + i * 0.1)
        
        # Test zone intersection
        zone = (100, 100, 200, 200)
        trajectories_in_zone = manager.get_trajectories_in_zone(zone)
        
        assert len(trajectories_in_zone) == 1
        assert trajectories_in_zone[0].track_id == 1
    
    @patch('src.tracking.vehicle_tracker.DeepSort')
    def test_performance_metrics(self, mock_deepsort):
        """Test tracking performance metrics."""
        # Mock DeepSORT
        mock_tracker_instance = Mock()
        mock_tracker_instance.update_tracks.return_value = []
        mock_deepsort.return_value = mock_tracker_instance
        
        tracker = VehicleTracker()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Simulate processing frames
        for _ in range(10):
            tracker.update([], frame)
            time.sleep(0.001)  # Small delay to simulate processing time
        
        stats = tracker.get_tracking_stats()
        
        assert stats["total_frames"] == 10
        assert stats["avg_processing_time_ms"] > 0
        assert stats["fps"] > 0
        assert stats["active_vehicles"] == 0
    
    def test_visualization_integration(self):
        """Test visualization with tracking data."""
        # Create mock tracked vehicles
        vehicles = [
            Mock(
                track_id=1,
                bbox=(100, 200, 300, 400),
                center=(200, 300),
                trajectory=[(190, 290), (195, 295), (200, 300)]
            ),
            Mock(
                track_id=2,
                bbox=(400, 100, 600, 300),
                center=(500, 200),
                trajectory=[(490, 190), (495, 195), (500, 200)]
            )
        ]
        
        # Create tracker and visualize
        with patch('src.tracking.vehicle_tracker.DeepSort'):
            tracker = VehicleTracker()
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            vis_frame = tracker.visualize_tracks(frame, vehicles)
            
            # Verify frame was modified
            assert not np.array_equal(frame, vis_frame)
            assert vis_frame.shape == (480, 640, 3)
    
    def test_memory_management(self):
        """Test memory management with long-running tracking."""
        manager = TrajectoryManager(max_trajectories=5)
        
        # Add more trajectories than max
        for track_id in range(10):
            for i in range(10):
                manager.update_trajectory(track_id, (i * 10, 100), time.time() + i)
        
        # Should have limited to max_trajectories
        assert len(manager.trajectories) <= 5
        
        # Test cleanup of old trajectories
        old_time = time.time() - 400  # Very old timestamp
        manager.update_trajectory(999, (0, 0), old_time)
        
        # Trigger cleanup
        manager._cleanup_old_trajectories()
        
        # Old trajectory should be removed
        assert 999 not in manager.trajectories

if __name__ == "__main__":
    pytest.main([__file__, "-v"])