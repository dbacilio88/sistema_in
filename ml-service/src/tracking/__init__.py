"""
Tracking module for vehicle multi-object tracking.

This module provides classes and utilities for tracking vehicles across frames
using DeepSORT algorithm with optimized performance for traffic monitoring.
"""

from .vehicle_tracker import VehicleTracker
from .trajectory import Trajectory, TrajectoryManager

__all__ = ["VehicleTracker", "Trajectory", "TrajectoryManager"]