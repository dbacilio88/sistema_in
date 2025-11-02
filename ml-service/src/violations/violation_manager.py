"""
Violation Management System.

This module provides comprehensive violation management including
reporting, statistics, and coordination between detection systems.
"""

import logging
import time
import json
import sqlite3
import numpy as np
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import threading
from collections import defaultdict, Counter

from .violation_detector import ViolationDetector, TrafficViolation, ViolationType, ViolationSeverity
from .lane_detector import LaneDetector, LaneViolation
from .notification_system import NotificationSystem, AlertPriority
from ..speed.speed_analyzer import SpeedAnalyzer, ViolationEvent as SpeedViolationEvent
from ..tracking.vehicle_tracker import TrackedVehicle

logger = logging.getLogger(__name__)

@dataclass
class ViolationReport:
    """Comprehensive violation report."""
    report_id: str
    generation_time: float
    time_period: Tuple[float, float]  # start_time, end_time
    total_violations: int
    violations_by_type: Dict[str, int]
    violations_by_severity: Dict[str, int]
    violations_by_hour: Dict[int, int]
    top_violation_locations: List[Tuple[str, int]]
    repeat_offenders: List[Tuple[int, int]]  # vehicle_id, violation_count
    false_positive_rate: float
    system_performance: Dict[str, Any]

@dataclass
class ViolationStatistics:
    """Real-time violation statistics."""
    current_violations: int
    hourly_rate: float
    daily_total: int
    weekly_total: int
    most_common_violation: str
    highest_severity_count: int
    average_confidence: float
    detection_accuracy: float

class ViolationManager:
    """
    Central violation management system.
    
    Features:
    - Coordination between detection systems
    - Real-time violation processing
    - Statistical analysis and reporting
    - Evidence management
    - Integration with notification system
    - Performance monitoring
    """
    
    def __init__(self, notification_system: Optional[NotificationSystem] = None):
        """
        Initialize violation manager.
        
        Args:
            notification_system: Optional notification system instance
        """
        # Core components
        self.violation_detector = ViolationDetector()
        self.lane_detector = LaneDetector()
        self.notification_system = notification_system or NotificationSystem()
        
        # Data storage
        self.db_path = "violations.db"
        self._init_database()
        
        # Processing state
        self.active_sessions: Dict[str, Dict] = {}
        self.processing_stats = {
            "frames_processed": 0,
            "violations_detected": 0,
            "notifications_sent": 0,
            "false_positives": 0,
            "processing_times": []
        }
        
        # Configuration
        self.config = {
            "auto_notification": True,
            "evidence_retention_days": 30,
            "max_violations_per_vehicle_per_hour": 5,
            "confidence_threshold": 0.7,
            "enable_lane_detection": True,
            "enable_speed_detection": True
        }
        
        # Threading for background tasks
        self.background_thread = None
        self.running = False
        
        logger.info("ViolationManager initialized")
    
    def _init_database(self):
        """Initialize violation management database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Main violations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS violations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    violation_id TEXT UNIQUE,
                    timestamp REAL,
                    violation_type TEXT,
                    severity TEXT,
                    vehicle_id INTEGER,
                    description TEXT,
                    confidence REAL,
                    location_zone_id TEXT,
                    location_zone_name TEXT,
                    location_coordinates TEXT,
                    speed_limit REAL,
                    measured_speed REAL,
                    license_plate TEXT,
                    plate_confidence REAL,
                    detection_confidence REAL,
                    tracking_quality REAL,
                    camera_id TEXT,
                    evidence_path TEXT,
                    reviewed BOOLEAN DEFAULT FALSE,
                    false_positive BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Processing sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE,
                    start_time REAL,
                    end_time REAL,
                    frames_processed INTEGER,
                    violations_detected INTEGER,
                    performance_metrics TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Statistics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS violation_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    hour INTEGER,
                    violation_type TEXT,
                    severity TEXT,
                    count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to initialize violation database: {e}")
    
    def start(self):
        """Start violation management system."""
        if not self.running:
            self.running = True
            
            # Start notification system
            self.notification_system.start()
            
            # Start background processing
            self.background_thread = threading.Thread(target=self._background_processing)
            self.background_thread.daemon = True
            self.background_thread.start()
            
            logger.info("ViolationManager started")
    
    def stop(self):
        """Stop violation management system."""
        self.running = False
        
        # Stop notification system
        self.notification_system.stop()
        
        # Wait for background thread
        if self.background_thread:
            self.background_thread.join(timeout=5.0)
        
        logger.info("ViolationManager stopped")
    
    def process_frame(self, frame: np.ndarray, speed_analyzer: SpeedAnalyzer, 
                     vehicles: List[TrackedVehicle], session_id: str = "default") -> List[TrafficViolation]:
        """
        Process a frame for violations.
        
        Args:
            frame: Input frame
            speed_analyzer: Speed analyzer instance
            vehicles: Currently tracked vehicles
            session_id: Processing session identifier
            
        Returns:
            List of detected violations
        """
        start_time = time.time()
        all_violations = []
        
        try:
            # Update session
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {
                    "start_time": start_time,
                    "frames_processed": 0,
                    "violations_detected": 0
                }
            
            session = self.active_sessions[session_id]
            session["frames_processed"] += 1
            
            # 1. Process speed violations
            if self.config["enable_speed_detection"]:
                speed_result = speed_analyzer.analyze_frame(frame)
                if speed_result.violations:
                    # Convert speed violations to traffic violations
                    for speed_violation_event in speed_result.violations:
                        speed_violations = self.violation_detector.detect_speed_violations(
                            [speed_violation_event.violation], vehicles, frame
                        )
                        all_violations.extend(speed_violations)
            
            # 2. Process lane violations
            if self.config["enable_lane_detection"]:
                lane_geometry = self.lane_detector.detect_lanes(frame)
                lane_mask = self.lane_detector.create_lane_mask(lane_geometry, frame.shape[:2])
                
                lane_violations = self.violation_detector.detect_lane_violations(
                    vehicles, lane_mask, frame
                )
                all_violations.extend(lane_violations)
                
                # Detect wrong-way driving
                expected_direction = np.array([0, -1])  # Assuming downward traffic flow
                wrong_way_violations = self.violation_detector.detect_wrong_way_driving(
                    vehicles, expected_direction, frame
                )
                all_violations.extend(wrong_way_violations)
                
                # Detect following distance violations
                following_violations = self.violation_detector.detect_following_distance_violations(
                    vehicles, frame
                )
                all_violations.extend(following_violations)
            
            # 3. Filter violations by confidence
            filtered_violations = [
                v for v in all_violations 
                if v.confidence >= self.config["confidence_threshold"]
            ]
            
            # 4. Process violations
            self.violation_detector.process_violations(filtered_violations)
            
            # 5. Store in database
            for violation in filtered_violations:
                self._store_violation(violation)
            
            # 6. Send notifications
            if self.config["auto_notification"]:
                for violation in filtered_violations:
                    self.notification_system.send_violation_alert(violation)
            
            # Update session statistics
            session["violations_detected"] += len(filtered_violations)
            self.processing_stats["frames_processed"] += 1
            self.processing_stats["violations_detected"] += len(filtered_violations)
            
            # Track processing time
            processing_time = time.time() - start_time
            self.processing_stats["processing_times"].append(processing_time)
            
            # Keep only recent processing times
            if len(self.processing_stats["processing_times"]) > 100:
                self.processing_stats["processing_times"] = self.processing_stats["processing_times"][-100:]
            
            return filtered_violations
            
        except Exception as e:
            logger.error(f"Failed to process frame for violations: {e}")
            return []
    
    def _store_violation(self, violation: TrafficViolation):
        """Store violation in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO violations (
                    violation_id, timestamp, violation_type, severity, vehicle_id,
                    description, confidence, location_zone_id, location_zone_name,
                    location_coordinates, speed_limit, measured_speed, license_plate,
                    plate_confidence, detection_confidence, tracking_quality, camera_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                violation.violation_id,
                violation.timestamp,
                violation.violation_type.value,
                violation.severity.value,
                violation.vehicle_id,
                violation.description,
                violation.confidence,
                violation.location.zone_id,
                violation.location.zone_name,
                json.dumps(violation.location.coordinates),
                violation.speed_limit,
                violation.measured_speed,
                violation.license_plate,
                violation.plate_confidence,
                violation.detection_confidence,
                violation.tracking_quality,
                violation.camera_id
            ))
            
            conn.commit()
            conn.close()
            
            # Update statistics
            self._update_statistics(violation)
            
        except Exception as e:
            logger.error(f"Failed to store violation: {e}")
    
    def _update_statistics(self, violation: TrafficViolation):
        """Update violation statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get date and hour
            dt = datetime.fromtimestamp(violation.timestamp)
            date_str = dt.strftime("%Y-%m-%d")
            hour = dt.hour
            
            # Update or insert statistics
            cursor.execute("""
                INSERT INTO violation_statistics (date, hour, violation_type, severity, count)
                VALUES (?, ?, ?, ?, 1)
                ON CONFLICT (date, hour, violation_type, severity) DO UPDATE SET
                count = count + 1
            """, (date_str, hour, violation.violation_type.value, violation.severity.value))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update statistics: {e}")
    
    def get_current_statistics(self) -> ViolationStatistics:
        """Get current violation statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = time.time()
            hour_ago = current_time - 3600
            day_ago = current_time - 86400
            week_ago = current_time - 604800
            
            # Current violations (last hour)
            cursor.execute("""
                SELECT COUNT(*) FROM violations 
                WHERE timestamp > ? AND false_positive = FALSE
            """, (hour_ago,))
            current_violations = cursor.fetchone()[0]
            
            # Hourly rate
            hourly_rate = current_violations  # Violations in last hour
            
            # Daily total
            cursor.execute("""
                SELECT COUNT(*) FROM violations 
                WHERE timestamp > ? AND false_positive = FALSE
            """, (day_ago,))
            daily_total = cursor.fetchone()[0]
            
            # Weekly total
            cursor.execute("""
                SELECT COUNT(*) FROM violations 
                WHERE timestamp > ? AND false_positive = FALSE
            """, (week_ago,))
            weekly_total = cursor.fetchone()[0]
            
            # Most common violation
            cursor.execute("""
                SELECT violation_type, COUNT(*) as count FROM violations 
                WHERE timestamp > ? AND false_positive = FALSE
                GROUP BY violation_type ORDER BY count DESC LIMIT 1
            """, (day_ago,))
            most_common_result = cursor.fetchone()
            most_common_violation = most_common_result[0] if most_common_result else "none"
            
            # Highest severity count
            cursor.execute("""
                SELECT COUNT(*) FROM violations 
                WHERE severity = 'critical' AND timestamp > ? AND false_positive = FALSE
            """, (day_ago,))
            highest_severity_count = cursor.fetchone()[0]
            
            # Average confidence
            cursor.execute("""
                SELECT AVG(confidence) FROM violations 
                WHERE timestamp > ? AND false_positive = FALSE
            """, (day_ago,))
            avg_confidence_result = cursor.fetchone()[0]
            average_confidence = avg_confidence_result if avg_confidence_result else 0.0
            
            # Detection accuracy (1 - false positive rate)
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN false_positive = TRUE THEN 1 ELSE 0 END) as false_positives
                FROM violations WHERE timestamp > ?
            """, (day_ago,))
            accuracy_result = cursor.fetchone()
            total, false_positives = accuracy_result
            detection_accuracy = 1.0 - (false_positives / max(1, total))
            
            conn.close()
            
            return ViolationStatistics(
                current_violations=current_violations,
                hourly_rate=hourly_rate,
                daily_total=daily_total,
                weekly_total=weekly_total,
                most_common_violation=most_common_violation,
                highest_severity_count=highest_severity_count,
                average_confidence=average_confidence,
                detection_accuracy=detection_accuracy
            )
            
        except Exception as e:
            logger.error(f"Failed to get current statistics: {e}")
            return ViolationStatistics(0, 0.0, 0, 0, "none", 0, 0.0, 0.0)
    
    def generate_report(self, start_time: float, end_time: float) -> ViolationReport:
        """
        Generate comprehensive violation report for time period.
        
        Args:
            start_time: Report start time (timestamp)
            end_time: Report end time (timestamp)
            
        Returns:
            Comprehensive violation report
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total violations
            cursor.execute("""
                SELECT COUNT(*) FROM violations 
                WHERE timestamp BETWEEN ? AND ? AND false_positive = FALSE
            """, (start_time, end_time))
            total_violations = cursor.fetchone()[0]
            
            # Violations by type
            cursor.execute("""
                SELECT violation_type, COUNT(*) FROM violations 
                WHERE timestamp BETWEEN ? AND ? AND false_positive = FALSE
                GROUP BY violation_type
            """, (start_time, end_time))
            violations_by_type = dict(cursor.fetchall())
            
            # Violations by severity
            cursor.execute("""
                SELECT severity, COUNT(*) FROM violations 
                WHERE timestamp BETWEEN ? AND ? AND false_positive = FALSE
                GROUP BY severity
            """, (start_time, end_time))
            violations_by_severity = dict(cursor.fetchall())
            
            # Violations by hour
            cursor.execute("""
                SELECT strftime('%H', datetime(timestamp, 'unixepoch')) as hour, COUNT(*) 
                FROM violations 
                WHERE timestamp BETWEEN ? AND ? AND false_positive = FALSE
                GROUP BY hour ORDER BY hour
            """, (start_time, end_time))
            violations_by_hour = {int(hour): count for hour, count in cursor.fetchall()}
            
            # Top violation locations
            cursor.execute("""
                SELECT location_zone_name, COUNT(*) as count FROM violations 
                WHERE timestamp BETWEEN ? AND ? AND false_positive = FALSE
                GROUP BY location_zone_name ORDER BY count DESC LIMIT 10
            """, (start_time, end_time))
            top_violation_locations = cursor.fetchall()
            
            # Repeat offenders
            cursor.execute("""
                SELECT vehicle_id, COUNT(*) as count FROM violations 
                WHERE timestamp BETWEEN ? AND ? AND false_positive = FALSE
                GROUP BY vehicle_id HAVING count > 1 ORDER BY count DESC LIMIT 10
            """, (start_time, end_time))
            repeat_offenders = cursor.fetchall()
            
            # False positive rate
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN false_positive = TRUE THEN 1 ELSE 0 END) as false_positives
                FROM violations WHERE timestamp BETWEEN ? AND ?
            """, (start_time, end_time))
            total, false_positives = cursor.fetchone()
            false_positive_rate = false_positives / max(1, total)
            
            conn.close()
            
            # System performance
            system_performance = {
                "average_processing_time": np.mean(self.processing_stats["processing_times"]) if self.processing_stats["processing_times"] else 0.0,
                "frames_processed": self.processing_stats["frames_processed"],
                "violations_detected": self.processing_stats["violations_detected"],
                "notifications_sent": self.processing_stats["notifications_sent"],
                "detection_rate": self.processing_stats["violations_detected"] / max(1, self.processing_stats["frames_processed"])
            }
            
            report = ViolationReport(
                report_id=f"report_{int(time.time())}",
                generation_time=time.time(),
                time_period=(start_time, end_time),
                total_violations=total_violations,
                violations_by_type=violations_by_type,
                violations_by_severity=violations_by_severity,
                violations_by_hour=violations_by_hour,
                top_violation_locations=top_violation_locations,
                repeat_offenders=repeat_offenders,
                false_positive_rate=false_positive_rate,
                system_performance=system_performance
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate violation report: {e}")
            return ViolationReport(
                report_id="error",
                generation_time=time.time(),
                time_period=(start_time, end_time),
                total_violations=0,
                violations_by_type={},
                violations_by_severity={},
                violations_by_hour={},
                top_violation_locations=[],
                repeat_offenders=[],
                false_positive_rate=0.0,
                system_performance={}
            )
    
    def mark_false_positive(self, violation_id: str):
        """Mark a violation as false positive."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE violations SET false_positive = TRUE 
                WHERE violation_id = ?
            """, (violation_id,))
            
            conn.commit()
            conn.close()
            
            # Update detector
            self.violation_detector.mark_false_positive(violation_id)
            
            # Update stats
            self.processing_stats["false_positives"] += 1
            
            logger.info(f"Marked violation {violation_id} as false positive")
            
        except Exception as e:
            logger.error(f"Failed to mark false positive: {e}")
    
    def get_violations_for_review(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get violations that need manual review."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM violations 
                WHERE reviewed = FALSE AND false_positive = FALSE
                ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
            
            columns = [description[0] for description in cursor.description]
            violations = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return violations
            
        except Exception as e:
            logger.error(f"Failed to get violations for review: {e}")
            return []
    
    def _background_processing(self):
        """Background processing tasks."""
        while self.running:
            try:
                # Clean up old data periodically
                self._cleanup_old_data()
                
                # Update hourly statistics
                self._update_hourly_statistics()
                
                # Sleep for 1 hour
                time.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in background processing: {e}")
                time.sleep(60)  # Sleep 1 minute on error
    
    def _cleanup_old_data(self):
        """Clean up old violation data."""
        try:
            retention_days = self.config["evidence_retention_days"]
            cutoff_time = time.time() - (retention_days * 86400)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete old violations
            cursor.execute("DELETE FROM violations WHERE timestamp < ?", (cutoff_time,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old violations")
            
            # Clean up violation detector memory
            self.violation_detector.cleanup_old_violations(retention_days * 86400)
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
    
    def _update_hourly_statistics(self):
        """Update hourly statistics aggregation."""
        # This could be expanded to create hourly summaries
        # for faster reporting and analysis
        pass
    
    def export_report_to_file(self, report: ViolationReport, filepath: str) -> bool:
        """Export violation report to JSON file."""
        try:
            report_data = asdict(report)
            
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            logger.info(f"Exported violation report to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export report: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        current_stats = self.get_current_statistics()
        
        return {
            "violation_manager": {
                "running": self.running,
                "active_sessions": len(self.active_sessions),
                "processing_stats": self.processing_stats
            },
            "violation_detector": self.violation_detector.get_statistics(),
            "notification_system": self.notification_system.get_alert_statistics(),
            "current_statistics": asdict(current_stats),
            "configuration": self.config
        }