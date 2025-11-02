#!/usr/bin/env python3
"""
Initialize and test the tracking system.

This script initializes the tracking components and runs basic tests
to ensure everything is working correctly.
"""

import sys
import os
import logging
import time
import numpy as np
import cv2
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tracking.vehicle_tracker import VehicleTracker, Detection
from tracking.trajectory import TrajectoryManager, Trajectory
from config import get_ml_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_trajectory_components():
    """Test trajectory management components."""
    logger.info("Testing trajectory components...")
    
    # Test Trajectory class
    trajectory = Trajectory(track_id=1)
    
    # Add some points
    base_time = time.time()
    trajectory.add_point(100, 200, base_time, 1)
    trajectory.add_point(110, 205, base_time + 0.1, 2)
    trajectory.add_point(120, 210, base_time + 0.2, 3)
    
    assert len(trajectory.points) == 3
    assert trajectory.total_distance > 0
    assert trajectory.avg_speed > 0
    
    # Test smoothing
    smoothed = trajectory.get_smoothed_trajectory()
    assert len(smoothed) == 3
    
    # Test prediction
    pred_x, pred_y = trajectory.predict_next_position(0.1)
    assert pred_x > 120  # Should predict further movement
    
    logger.info("✓ Trajectory class working correctly")
    
    # Test TrajectoryManager
    manager = TrajectoryManager()
    
    # Add trajectories
    manager.update_trajectory(1, (100, 200), base_time, 1)
    manager.update_trajectory(1, (110, 205), base_time + 0.1, 2)
    manager.update_trajectory(2, (300, 400), base_time, 1)
    
    assert len(manager.trajectories) == 2
    assert 1 in manager.trajectories
    assert 2 in manager.trajectories
    
    # Test statistics
    stats = manager.get_trajectory_statistics()
    assert stats["total_trajectories"] == 2
    assert stats["active_trajectories"] > 0
    
    logger.info("✓ TrajectoryManager working correctly")

def test_vehicle_tracker():
    """Test vehicle tracking functionality."""
    logger.info("Testing vehicle tracker...")
    
    # Initialize tracker
    tracker = VehicleTracker()
    
    # Create test detections
    detections = [
        Detection(bbox=(100, 200, 300, 400), confidence=0.9, class_id=2, class_name="car"),
        Detection(bbox=(500, 100, 700, 300), confidence=0.8, class_id=2, class_name="truck")
    ]
    
    # Create test frame
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Process detections
    tracked_vehicles = tracker.update(detections, frame)
    
    # Should have some tracked vehicles (exact count depends on DeepSORT initialization)
    logger.info(f"Tracked {len(tracked_vehicles)} vehicles")
    
    # Test multiple frames to build trajectories
    for i in range(5):
        # Simulate moving vehicles
        moved_detections = []
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            # Move slightly
            new_bbox = (x1 + i*2, y1 + i*2, x2 + i*2, y2 + i*2)
            moved_detections.append(Detection(
                bbox=new_bbox,
                confidence=det.confidence,
                class_id=det.class_id,
                class_name=det.class_name
            ))
        
        tracked_vehicles = tracker.update(moved_detections, frame)
        logger.info(f"Frame {i+1}: {len(tracked_vehicles)} tracked vehicles")
    
    # Test statistics
    stats = tracker.get_tracking_stats()
    logger.info(f"Tracking stats: {stats}")
    
    # Test visualization
    vis_frame = tracker.visualize_tracks(frame, tracked_vehicles)
    assert vis_frame.shape == frame.shape
    
    logger.info("✓ Vehicle tracker working correctly")

def test_integration():
    """Test integration between components."""
    logger.info("Testing component integration...")
    
    tracker = VehicleTracker()
    
    # Simulate a complete tracking scenario
    vehicle_paths = [
        [(100 + i*5, 200 + i*2) for i in range(10)],  # Vehicle 1 path
        [(300 + i*3, 150 + i*4) for i in range(10)]   # Vehicle 2 path
    ]
    
    for frame_idx in range(10):
        detections = []
        
        # Create detections based on vehicle paths
        for path_idx, path in enumerate(vehicle_paths):
            if frame_idx < len(path):
                x, y = path[frame_idx]
                detections.append(Detection(
                    bbox=(x, y, x+100, y+60),
                    confidence=0.9,
                    class_id=2,
                    class_name="car"
                ))
        
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        tracked_vehicles = tracker.update(detections, frame)
        
        logger.info(f"Frame {frame_idx}: {len(detections)} detections → {len(tracked_vehicles)} tracks")
    
    # Check that trajectories were built
    trajectories = tracker.trajectory_manager.get_all_trajectories()
    logger.info(f"Total trajectories created: {len(trajectories)}")
    
    for track_id, trajectory in trajectories.items():
        logger.info(f"Track {track_id}: {len(trajectory.points)} points, "
                   f"distance: {trajectory.total_distance:.1f}, "
                   f"speed: {trajectory.avg_speed:.1f}")
    
    logger.info("✓ Integration test completed successfully")

def test_performance():
    """Test basic performance characteristics."""
    logger.info("Testing performance...")
    
    tracker = VehicleTracker()
    
    # Create larger test scenario
    frame_count = 50
    detections_per_frame = 8
    
    processing_times = []
    
    for frame_idx in range(frame_count):
        # Generate random detections
        detections = []
        for i in range(detections_per_frame):
            x = np.random.randint(50, 550)
            y = np.random.randint(50, 350)
            detections.append(Detection(
                bbox=(x, y, x+80, y+50),
                confidence=np.random.uniform(0.7, 0.95),
                class_id=2,
                class_name="car"
            ))
        
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Time the processing
        start_time = time.time()
        tracked_vehicles = tracker.update(detections, frame)
        processing_time = time.time() - start_time
        
        processing_times.append(processing_time)
        
        if frame_idx % 10 == 0:
            logger.info(f"Frame {frame_idx}: {processing_time*1000:.2f}ms, "
                       f"{len(tracked_vehicles)} tracks")
    
    # Calculate performance metrics
    avg_time = np.mean(processing_times)
    max_time = np.max(processing_times)
    fps = 1.0 / avg_time
    
    logger.info(f"Performance results:")
    logger.info(f"  Average processing time: {avg_time*1000:.2f}ms")
    logger.info(f"  Maximum processing time: {max_time*1000:.2f}ms")
    logger.info(f"  Average FPS: {fps:.1f}")
    
    # Performance assertions
    assert avg_time < 0.1, f"Average processing time too high: {avg_time*1000:.2f}ms"
    assert fps > 10, f"FPS too low: {fps:.1f}"
    
    logger.info("✓ Performance test passed")

def test_configuration():
    """Test configuration loading."""
    logger.info("Testing configuration...")
    
    settings = get_ml_settings()
    
    logger.info(f"GPU enabled: {settings.gpu_enabled}")
    logger.info(f"Model directory: {settings.model_dir}")
    logger.info(f"ONNX providers: {settings.onnx_providers}")
    
    # Verify required directories exist
    model_dir = Path(settings.model_dir)
    if not model_dir.exists():
        logger.warning(f"Model directory doesn't exist: {model_dir}")
        model_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created model directory: {model_dir}")
    
    logger.info("✓ Configuration test completed")

def run_all_tests():
    """Run all initialization tests."""
    logger.info("Starting tracking system initialization tests...")
    
    try:
        test_configuration()
        test_trajectory_components()
        test_vehicle_tracker()
        test_integration()
        test_performance()
        
        logger.info("🎉 All tests passed! Tracking system is ready.")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main initialization function."""
    logger.info("Initializing ML Service Tracking System")
    
    # Check dependencies
    try:
        import deep_sort_realtime
        logger.info("✓ DeepSORT dependency available")
    except ImportError:
        logger.error("❌ DeepSORT not installed. Run: pip install deep-sort-realtime")
        return False
    
    try:
        import cv2
        logger.info("✓ OpenCV dependency available")
    except ImportError:
        logger.error("❌ OpenCV not installed. Run: pip install opencv-python")
        return False
    
    # Run tests
    success = run_all_tests()
    
    if success:
        logger.info("✅ Tracking system initialization completed successfully")
        logger.info("Ready to process video streams with vehicle tracking")
    else:
        logger.error("❌ Tracking system initialization failed")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)