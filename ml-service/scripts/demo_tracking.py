#!/usr/bin/env python3
"""
Demo script showing tracking system integration.

This script demonstrates the complete vehicle tracking pipeline
with synthetic data and visualization.
"""

import numpy as np
import cv2
import time
import logging
import sys
import os
from typing import List, Tuple

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tracking.vehicle_tracker import VehicleTracker, Detection
from tracking.trajectory import TrajectoryManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_demo_detections(frame_idx: int) -> List[Detection]:
    """Create demo vehicle detections for testing."""
    detections = []
    
    # Vehicle 1: Moving right
    x1 = 50 + frame_idx * 3
    y1 = 200
    if x1 < 500:
        detections.append(Detection(
            bbox=(x1, y1, x1 + 100, y1 + 60),
            confidence=0.9,
            class_id=2,
            class_name="car"
        ))
    
    # Vehicle 2: Moving down
    x2 = 300
    y2 = 50 + frame_idx * 2
    if y2 < 400:
        detections.append(Detection(
            bbox=(x2, y2, x2 + 80, y2 + 50),
            confidence=0.85,
            class_id=2,
            class_name="truck"
        ))
    
    # Vehicle 3: Moving diagonally (appears later)
    if frame_idx > 20:
        x3 = 100 + (frame_idx - 20) * 4
        y3 = 100 + (frame_idx - 20) * 3
        if x3 < 500 and y3 < 350:
            detections.append(Detection(
                bbox=(x3, y3, x3 + 90, y3 + 55),
                confidence=0.88,
                class_id=2,
                class_name="bus"
            ))
    
    return detections

def main():
    """Run tracking demo."""
    logger.info("Starting Vehicle Tracking Demo")
    
    try:
        # Initialize tracker
        tracker = VehicleTracker()
        
        # Demo parameters
        frame_width, frame_height = 640, 480
        total_frames = 100
        
        logger.info(f"Running demo with {total_frames} frames")
        
        # Process frames
        for frame_idx in range(total_frames):
            # Create synthetic frame
            frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
            frame.fill(50)  # Dark gray background
            
            # Generate detections
            detections = create_demo_detections(frame_idx)
            
            # Update tracker
            tracked_vehicles = tracker.update(detections, frame)
            
            # Log progress
            if frame_idx % 10 == 0:
                logger.info(f"Frame {frame_idx}: {len(detections)} detections, {len(tracked_vehicles)} tracks")
                
                # Show tracking details
                for vehicle in tracked_vehicles:
                    logger.info(f"  Track {vehicle.track_id}: {vehicle.class_name} at {vehicle.center}, "
                               f"trajectory length: {len(vehicle.trajectory)}")
        
        # Final statistics
        stats = tracker.get_tracking_stats()
        logger.info("\n=== Final Tracking Statistics ===")
        logger.info(f"Total frames processed: {stats['total_frames']}")
        logger.info(f"Average processing time: {stats['avg_processing_time_ms']:.2f}ms")
        logger.info(f"Average FPS: {stats['fps']:.1f}")
        logger.info(f"Active vehicles: {stats['active_vehicles']}")
        
        # Trajectory statistics
        trajectory_stats = tracker.trajectory_manager.get_trajectory_statistics()
        logger.info(f"Total trajectories: {trajectory_stats['total_trajectories']}")
        logger.info(f"Average trajectory length: {trajectory_stats['avg_trajectory_length']:.1f}")
        logger.info(f"Total distance covered: {trajectory_stats['total_distance_covered']:.1f} pixels")
        
        logger.info("\n✅ Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)