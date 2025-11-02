"""
Trajectory management for vehicle tracking.

This module handles trajectory storage, analysis, and management
for tracked vehicles in the traffic monitoring system.
"""

import time
import logging
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass, field
import numpy as np
import math

logger = logging.getLogger(__name__)

@dataclass
class TrajectoryPoint:
    """Single point in a vehicle trajectory."""
    x: int
    y: int
    timestamp: float
    frame_number: Optional[int] = None

@dataclass
class Trajectory:
    """Complete trajectory for a tracked vehicle."""
    track_id: int
    points: List[TrajectoryPoint] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    total_distance: float = 0.0
    avg_speed: float = 0.0
    direction_vector: Tuple[float, float] = (0.0, 0.0)
    is_active: bool = True
    
    def add_point(self, x: int, y: int, timestamp: Optional[float] = None, frame_number: Optional[int] = None):
        """Add a new point to the trajectory."""
        if timestamp is None:
            timestamp = time.time()
        
        point = TrajectoryPoint(x, y, timestamp, frame_number)
        self.points.append(point)
        self.last_updated = timestamp
        
        # Update trajectory metrics
        self._update_metrics()
    
    def _update_metrics(self):
        """Update trajectory metrics (distance, speed, direction)."""
        if len(self.points) < 2:
            return
        
        # Calculate total distance
        total_dist = 0.0
        for i in range(1, len(self.points)):
            p1, p2 = self.points[i-1], self.points[i]
            dist = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
            total_dist += dist
        
        self.total_distance = total_dist
        
        # Calculate average speed (pixels per second)
        if len(self.points) >= 2:
            time_diff = self.points[-1].timestamp - self.points[0].timestamp
            if time_diff > 0:
                self.avg_speed = total_dist / time_diff
        
        # Calculate direction vector (last 5 points for stability)
        if len(self.points) >= 3:
            recent_points = self.points[-min(5, len(self.points)):]
            start_point = recent_points[0]
            end_point = recent_points[-1]
            
            dx = end_point.x - start_point.x
            dy = end_point.y - start_point.y
            length = math.sqrt(dx**2 + dy**2)
            
            if length > 0:
                self.direction_vector = (dx / length, dy / length)
    
    def get_smoothed_trajectory(self, window_size: int = 5) -> List[Tuple[int, int]]:
        """
        Get smoothed trajectory using moving average.
        
        Args:
            window_size: Size of smoothing window
            
        Returns:
            List of smoothed (x, y) coordinates
        """
        if len(self.points) < window_size:
            return [(p.x, p.y) for p in self.points]
        
        smoothed = []
        for i in range(len(self.points)):
            start_idx = max(0, i - window_size // 2)
            end_idx = min(len(self.points), i + window_size // 2 + 1)
            
            window_points = self.points[start_idx:end_idx]
            avg_x = sum(p.x for p in window_points) / len(window_points)
            avg_y = sum(p.y for p in window_points) / len(window_points)
            
            smoothed.append((int(avg_x), int(avg_y)))
        
        return smoothed
    
    def predict_next_position(self, time_ahead: float = 0.033) -> Tuple[int, int]:
        """
        Predict next position based on current trajectory.
        
        Args:
            time_ahead: Time to predict ahead (seconds)
            
        Returns:
            Predicted (x, y) position
        """
        if len(self.points) < 2:
            return (0, 0) if not self.points else (self.points[-1].x, self.points[-1].y)
        
        last_point = self.points[-1]
        velocity_x = self.direction_vector[0] * self.avg_speed
        velocity_y = self.direction_vector[1] * self.avg_speed
        
        pred_x = int(last_point.x + velocity_x * time_ahead)
        pred_y = int(last_point.y + velocity_y * time_ahead)
        
        return (pred_x, pred_y)
    
    def get_duration(self) -> float:
        """Get trajectory duration in seconds."""
        if len(self.points) < 2:
            return 0.0
        return self.points[-1].timestamp - self.points[0].timestamp
    
    def get_bounding_box(self) -> Tuple[int, int, int, int]:
        """Get trajectory bounding box (x_min, y_min, x_max, y_max)."""
        if not self.points:
            return (0, 0, 0, 0)
        
        x_coords = [p.x for p in self.points]
        y_coords = [p.y for p in self.points]
        
        return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))

class TrajectoryManager:
    """
    Manager for all vehicle trajectories.
    
    Handles trajectory storage, analysis, and cleanup for the tracking system.
    """
    
    def __init__(self, max_trajectories: int = 1000, cleanup_interval: float = 60.0):
        """
        Initialize trajectory manager.
        
        Args:
            max_trajectories: Maximum number of trajectories to keep
            cleanup_interval: Interval for cleaning old trajectories (seconds)
        """
        self.trajectories: Dict[int, Trajectory] = {}
        self.max_trajectories = max_trajectories
        self.cleanup_interval = cleanup_interval
        self.last_cleanup = time.time()
        
        logger.info(f"TrajectoryManager initialized with max {max_trajectories} trajectories")
    
    def update_trajectory(self, track_id: int, position: Tuple[int, int], timestamp: Optional[float] = None, frame_number: Optional[int] = None):
        """
        Update trajectory for a tracked vehicle.
        
        Args:
            track_id: Vehicle track ID
            position: Current (x, y) position
            timestamp: Current timestamp
            frame_number: Current frame number
        """
        x, y = position
        
        if track_id not in self.trajectories:
            self.trajectories[track_id] = Trajectory(track_id)
            logger.debug(f"Created new trajectory for track {track_id}")
        
        self.trajectories[track_id].add_point(x, y, timestamp, frame_number)
        
        # Periodic cleanup
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_trajectories()
            self.last_cleanup = current_time
    
    def get_trajectory(self, track_id: int) -> Optional[Trajectory]:
        """Get trajectory for a specific track ID."""
        return self.trajectories.get(track_id)
    
    def get_all_trajectories(self) -> Dict[int, Trajectory]:
        """Get all trajectories."""
        return self.trajectories.copy()
    
    def get_active_trajectories(self, max_age: float = 30.0) -> Dict[int, Trajectory]:
        """
        Get trajectories that have been updated recently.
        
        Args:
            max_age: Maximum age in seconds for active trajectories
            
        Returns:
            Dictionary of active trajectories
        """
        current_time = time.time()
        active = {}
        
        for track_id, trajectory in self.trajectories.items():
            if current_time - trajectory.last_updated <= max_age:
                active[track_id] = trajectory
        
        return active
    
    def remove_trajectory(self, track_id: int) -> bool:
        """
        Remove trajectory for a specific track ID.
        
        Args:
            track_id: Track ID to remove
            
        Returns:
            True if trajectory was removed, False if not found
        """
        if track_id in self.trajectories:
            self.trajectories[track_id].is_active = False
            del self.trajectories[track_id]
            logger.debug(f"Removed trajectory for track {track_id}")
            return True
        return False
    
    def _cleanup_old_trajectories(self):
        """Remove old inactive trajectories."""
        current_time = time.time()
        max_age = 300.0  # 5 minutes
        
        tracks_to_remove = []
        for track_id, trajectory in self.trajectories.items():
            if current_time - trajectory.last_updated > max_age:
                tracks_to_remove.append(track_id)
        
        for track_id in tracks_to_remove:
            del self.trajectories[track_id]
        
        # Also limit total number of trajectories
        if len(self.trajectories) > self.max_trajectories:
            # Remove oldest trajectories
            sorted_trajectories = sorted(
                self.trajectories.items(),
                key=lambda x: x[1].last_updated
            )
            
            to_remove = len(self.trajectories) - self.max_trajectories
            for track_id, _ in sorted_trajectories[:to_remove]:
                del self.trajectories[track_id]
        
        if tracks_to_remove:
            logger.info(f"Cleaned up {len(tracks_to_remove)} old trajectories")
    
    def get_trajectory_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about all trajectories.
        
        Returns:
            Dictionary with trajectory statistics
        """
        if not self.trajectories:
            return {
                "total_trajectories": 0,
                "active_trajectories": 0,
                "avg_trajectory_length": 0,
                "avg_trajectory_duration": 0,
                "total_distance_covered": 0
            }
        
        current_time = time.time()
        active_count = 0
        total_points = 0
        total_duration = 0
        total_distance = 0
        
        for trajectory in self.trajectories.values():
            if current_time - trajectory.last_updated <= 30.0:  # Active if updated in last 30s
                active_count += 1
            
            total_points += len(trajectory.points)
            total_duration += trajectory.get_duration()
            total_distance += trajectory.total_distance
        
        return {
            "total_trajectories": len(self.trajectories),
            "active_trajectories": active_count,
            "avg_trajectory_length": total_points / len(self.trajectories),
            "avg_trajectory_duration": total_duration / len(self.trajectories),
            "total_distance_covered": total_distance
        }
    
    def get_trajectories_in_zone(self, zone: Tuple[int, int, int, int]) -> List[Trajectory]:
        """
        Get trajectories that pass through a specific zone.
        
        Args:
            zone: Zone coordinates (x_min, y_min, x_max, y_max)
            
        Returns:
            List of trajectories that intersect with the zone
        """
        x_min, y_min, x_max, y_max = zone
        intersecting = []
        
        for trajectory in self.trajectories.values():
            for point in trajectory.points:
                if x_min <= point.x <= x_max and y_min <= point.y <= y_max:
                    intersecting.append(trajectory)
                    break
        
        return intersecting
    
    def export_trajectories(self, track_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Export trajectories to JSON-serializable format.
        
        Args:
            track_ids: Optional list of specific track IDs to export
            
        Returns:
            Dictionary with trajectory data
        """
        export_data = {
            "timestamp": time.time(),
            "trajectories": {}
        }
        
        trajectories_to_export = self.trajectories
        if track_ids:
            trajectories_to_export = {
                tid: traj for tid, traj in self.trajectories.items() 
                if tid in track_ids
            }
        
        for track_id, trajectory in trajectories_to_export.items():
            export_data["trajectories"][track_id] = {
                "track_id": trajectory.track_id,
                "created_at": trajectory.created_at,
                "last_updated": trajectory.last_updated,
                "total_distance": trajectory.total_distance,
                "avg_speed": trajectory.avg_speed,
                "direction_vector": trajectory.direction_vector,
                "duration": trajectory.get_duration(),
                "points": [
                    {
                        "x": p.x,
                        "y": p.y,
                        "timestamp": p.timestamp,
                        "frame_number": p.frame_number
                    }
                    for p in trajectory.points
                ]
            }
        
        return export_data
    
    def clear_all(self):
        """Clear all trajectories."""
        self.trajectories.clear()
        logger.info("All trajectories cleared")