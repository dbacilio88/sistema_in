"""
Vehicle Tracker using DeepSORT algorithm.

This module implements multi-object tracking for vehicles using DeepSORT
with optimizations for traffic monitoring scenarios.
"""

import logging
import time
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
import cv2
from dataclasses import dataclass
from deep_sort_realtime import DeepSort

from ..config import get_ml_settings
from .trajectory import Trajectory, TrajectoryManager

logger = logging.getLogger(__name__)

@dataclass
class Detection:
    """Vehicle detection with bounding box and confidence."""
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float
    class_id: int
    class_name: str

@dataclass
class TrackedVehicle:
    """Tracked vehicle with ID and trajectory."""
    track_id: int
    bbox: Tuple[int, int, int, int]
    confidence: float
    class_name: str
    center: Tuple[int, int]
    trajectory: List[Tuple[int, int]]
    first_seen: float
    last_seen: float
    frame_count: int

class VehicleTracker:
    """
    Multi-object tracker for vehicles using DeepSORT.
    
    Features:
    - Persistent tracking across frames
    - Trajectory management
    - Occlusion handling
    - Performance optimization for real-time processing
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize vehicle tracker.
        
        Args:
            config_path: Optional path to custom tracker configuration
        """
        self.settings = get_ml_settings()
        self.tracker = self._initialize_tracker()
        self.trajectory_manager = TrajectoryManager()
        self.tracked_vehicles: Dict[int, TrackedVehicle] = {}
        self.frame_count = 0
        
        # Performance metrics
        self.total_processing_time = 0.0
        self.total_frames = 0
        
        logger.info("VehicleTracker initialized with DeepSORT")
    
    def _initialize_tracker(self) -> DeepSort:
        """Initialize DeepSORT tracker with optimized parameters."""
        return DeepSort(
            max_age=30,              # Maximum frames to keep track without detection
            n_init=3,                # Number of consecutive detections before confirmed
            nms_max_overlap=0.7,     # Non-maximum suppression threshold
            max_cosine_distance=0.2, # Maximum cosine distance for matching
            nn_budget=100,           # Maximum size of appearance descriptors gallery
            override_track_class=None,
            embedder="mobilenet",    # Use MobileNet for feature extraction
            half=True,               # Use half precision for speed
            bgr=True,                # Input format is BGR
            embedder_gpu=self.settings.gpu_enabled,
            embedder_model_name="mobilenetv2_x1_0",
            embedder_wts=None,
            polygon=False,
            today=None
        )
    
    def update(self, detections: List[Detection], frame: np.ndarray) -> List[TrackedVehicle]:
        """
        Update tracker with new detections.
        
        Args:
            detections: List of vehicle detections from YOLOv8
            frame: Current frame for visual tracking
            
        Returns:
            List of tracked vehicles with updated positions
        """
        start_time = time.time()
        
        # Convert detections to DeepSORT format
        det_list = self._prepare_detections(detections)
        
        # Update tracker
        tracks = self.tracker.update_tracks(det_list, frame=frame)
        
        # Process tracked vehicles
        tracked_vehicles = self._process_tracks(tracks)
        
        # Update performance metrics
        processing_time = time.time() - start_time
        self.total_processing_time += processing_time
        self.total_frames += 1
        self.frame_count += 1
        
        if self.frame_count % 100 == 0:
            avg_time = self.total_processing_time / self.total_frames
            logger.info(f"Tracking performance: {avg_time*1000:.2f}ms avg, frame {self.frame_count}")
        
        return tracked_vehicles
    
    def _prepare_detections(self, detections: List[Detection]) -> List[List]:
        """
        Convert YOLOv8 detections to DeepSORT format.
        
        Args:
            detections: List of Detection objects
            
        Returns:
            List of detections in DeepSORT format: [x1, y1, x2, y2, confidence, class_name]
        """
        det_list = []
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            # DeepSORT expects [x1, y1, x2, y2, confidence, class_name]
            det_list.append([x1, y1, x2, y2, det.confidence, det.class_name])
        
        return det_list
    
    def _process_tracks(self, tracks) -> List[TrackedVehicle]:
        """
        Process DeepSORT tracks into TrackedVehicle objects.
        
        Args:
            tracks: DeepSORT track objects
            
        Returns:
            List of TrackedVehicle objects
        """
        tracked_vehicles = []
        current_time = time.time()
        active_track_ids = set()
        
        for track in tracks:
            if not track.is_confirmed():
                continue
                
            track_id = track.track_id
            active_track_ids.add(track_id)
            
            # Get bounding box
            x1, y1, x2, y2 = track.to_ltrb().astype(int)
            bbox = (x1, y1, x2, y2)
            
            # Calculate center
            center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
            
            # Get or create tracked vehicle
            if track_id in self.tracked_vehicles:
                vehicle = self.tracked_vehicles[track_id]
                vehicle.bbox = bbox
                vehicle.center = center
                vehicle.last_seen = current_time
                vehicle.frame_count += 1
                vehicle.trajectory.append(center)
                
                # Limit trajectory length for memory efficiency
                if len(vehicle.trajectory) > 100:
                    vehicle.trajectory = vehicle.trajectory[-100:]
            else:
                # New track
                vehicle = TrackedVehicle(
                    track_id=track_id,
                    bbox=bbox,
                    confidence=getattr(track, 'confidence', 0.0),
                    class_name=getattr(track, 'get_class', lambda: 'vehicle')(),
                    center=center,
                    trajectory=[center],
                    first_seen=current_time,
                    last_seen=current_time,
                    frame_count=1
                )
                self.tracked_vehicles[track_id] = vehicle
                logger.debug(f"New vehicle track created: ID {track_id}")
            
            # Update trajectory manager
            self.trajectory_manager.update_trajectory(track_id, center, current_time)
            
            tracked_vehicles.append(vehicle)
        
        # Clean up old tracks
        self._cleanup_old_tracks(active_track_ids, current_time)
        
        return tracked_vehicles
    
    def _cleanup_old_tracks(self, active_track_ids: set, current_time: float):
        """
        Remove tracks that haven't been seen for too long.
        
        Args:
            active_track_ids: Set of currently active track IDs
            current_time: Current timestamp
        """
        max_age_seconds = 5.0  # Remove tracks after 5 seconds without detection
        
        tracks_to_remove = []
        for track_id, vehicle in self.tracked_vehicles.items():
            if (track_id not in active_track_ids and 
                current_time - vehicle.last_seen > max_age_seconds):
                tracks_to_remove.append(track_id)
        
        for track_id in tracks_to_remove:
            del self.tracked_vehicles[track_id]
            self.trajectory_manager.remove_trajectory(track_id)
            logger.debug(f"Removed old track: ID {track_id}")
    
    def get_vehicle_trajectories(self) -> Dict[int, List[Tuple[int, int]]]:
        """
        Get all vehicle trajectories.
        
        Returns:
            Dictionary mapping track ID to list of (x, y) coordinates
        """
        return {
            track_id: vehicle.trajectory 
            for track_id, vehicle in self.tracked_vehicles.items()
        }
    
    def get_active_vehicle_count(self) -> int:
        """Get number of currently tracked vehicles."""
        return len(self.tracked_vehicles)
    
    def get_tracking_stats(self) -> Dict[str, Any]:
        """
        Get tracking performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        avg_processing_time = (
            self.total_processing_time / max(self.total_frames, 1)
        )
        
        return {
            "total_frames": self.total_frames,
            "active_vehicles": len(self.tracked_vehicles),
            "avg_processing_time_ms": avg_processing_time * 1000,
            "fps": 1.0 / max(avg_processing_time, 0.001),
            "total_tracks_created": len(self.trajectory_manager.trajectories),
        }
    
    def reset(self):
        """Reset tracker state."""
        self.tracker = self._initialize_tracker()
        self.trajectory_manager = TrajectoryManager()
        self.tracked_vehicles.clear()
        self.frame_count = 0
        self.total_processing_time = 0.0
        self.total_frames = 0
        logger.info("VehicleTracker reset")
    
    def visualize_tracks(self, frame: np.ndarray, tracked_vehicles: List[TrackedVehicle]) -> np.ndarray:
        """
        Draw tracking visualization on frame.
        
        Args:
            frame: Input frame
            tracked_vehicles: List of tracked vehicles
            
        Returns:
            Frame with tracking visualization
        """
        vis_frame = frame.copy()
        
        for vehicle in tracked_vehicles:
            x1, y1, x2, y2 = vehicle.bbox
            track_id = vehicle.track_id
            
            # Draw bounding box
            color = self._get_track_color(track_id)
            cv2.rectangle(vis_frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw track ID
            label = f"ID: {track_id}"
            cv2.putText(vis_frame, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Draw trajectory
            if len(vehicle.trajectory) > 1:
                points = np.array(vehicle.trajectory, dtype=np.int32)
                cv2.polylines(vis_frame, [points], False, color, 2)
                
                # Draw direction arrow
                if len(points) >= 2:
                    pt1 = tuple(points[-2])
                    pt2 = tuple(points[-1])
                    cv2.arrowedLine(vis_frame, pt1, pt2, color, 2, tipLength=0.3)
        
        return vis_frame
    
    def _get_track_color(self, track_id: int) -> Tuple[int, int, int]:
        """Get consistent color for track ID."""
        # Generate consistent color based on track ID
        np.random.seed(track_id)
        color = tuple(np.random.randint(0, 255, 3).tolist())
        return color