"""
Traffic Violations Detection Module.

This module provides comprehensive traffic violation detection including
speed violations, lane violations, and automated notification systems.
"""

from .violation_detector import ViolationDetector, ViolationType, ViolationSeverity
from .lane_detector import LaneDetector, LaneViolation
from .notification_system import NotificationSystem, NotificationChannel, Alert
from .violation_manager import ViolationManager, ViolationReport, ViolationStatistics

__version__ = "1.0.0"

__all__ = [
    "ViolationDetector",
    "ViolationType",
    "ViolationSeverity",
    "LaneDetector", 
    "LaneViolation",
    "NotificationSystem",
    "NotificationChannel",
    "Alert",
    "ViolationManager",
    "ViolationReport",
    "ViolationStatistics"
]

# Violation severity thresholds
SEVERITY_THRESHOLDS = {
    "speed_violation": {
        "minor": 10.0,      # 10 km/h over limit
        "moderate": 20.0,   # 20 km/h over limit
        "severe": 40.0,     # 40 km/h over limit
        "critical": 60.0    # 60 km/h over limit
    },
    "lane_violation": {
        "minor": 0.3,       # 30% lane overlap
        "moderate": 0.5,    # 50% lane overlap
        "severe": 0.8,      # 80% lane overlap
        "critical": 1.0     # Complete lane change
    }
}

# Default notification settings
DEFAULT_NOTIFICATION_CONFIG = {
    "immediate_alerts": ["critical", "severe"],
    "batch_reports": ["minor", "moderate"],
    "notification_cooldown": 60.0,  # seconds
    "max_alerts_per_hour": 100,
    "alert_channels": ["database", "api", "file"]
}