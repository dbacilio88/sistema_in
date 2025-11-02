#!/usr/bin/env python3
"""
Example usage script for the traffic violations detection system.

This script demonstrates how to use the violations detection system
with sample data and common use cases.
"""

import time
import numpy as np
import cv2
from pathlib import Path
import sys

# Add parent directories to path for imports  
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent))

from src.violations.violation_detector import ViolationDetector, ViolationType, ViolationSeverity
from src.violations.lane_detector import LaneDetector
from src.violations.notification_system import NotificationSystem
from src.violations.violation_manager import ViolationManager
from src.speed.speed_analyzer import SpeedViolation
from src.tracking.vehicle_tracker import TrackedVehicle


def create_sample_frame() -> np.ndarray:
    """Create a sample traffic frame with lane markings."""
    # Create base frame
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    
    # Add road background
    cv2.rectangle(frame, (0, 400), (1920, 1080), (50, 50, 50), -1)
    
    # Add lane markings
    # Left lane
    cv2.line(frame, (600, 1080), (800, 400), (255, 255, 255), 8)
    # Center lane (dashed)
    for y in range(400, 1080, 40):
        cv2.line(frame, (960, y), (960, y+20), (255, 255, 0), 4)
    # Right lane  
    cv2.line(frame, (1320, 1080), (1120, 400), (255, 255, 255), 8)
    
    # Add some vehicles
    # Vehicle 1 (normal position)
    cv2.rectangle(frame, (700, 600), (850, 700), (0, 0, 255), -1)
    cv2.putText(frame, "CAR-001", (710, 690), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Vehicle 2 (crossing lanes)
    cv2.rectangle(frame, (900, 750), (1050, 850), (255, 0, 0), -1)
    cv2.putText(frame, "CAR-002", (910, 840), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Vehicle 3 (speeding)
    cv2.rectangle(frame, (1100, 500), (1250, 600), (0, 255, 0), -1)
    cv2.putText(frame, "CAR-003", (1110, 590), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    return frame


def create_sample_vehicles() -> list:
    """Create sample tracked vehicles."""
    vehicles = []
    
    # Vehicle 1 - Normal driving
    vehicle1 = TrackedVehicle(
        track_id=1,
        bbox=(700, 600, 850, 700),
        confidence=0.9,
        class_name="car"
    )
    vehicle1.trajectory = [
        (775, 750), (775, 720), (775, 690), (775, 660), (775, 650)
    ]
    vehicles.append(vehicle1)
    
    # Vehicle 2 - Lane violation
    vehicle2 = TrackedVehicle(
        track_id=2,
        bbox=(900, 750, 1050, 850),
        confidence=0.85,
        class_name="car"
    )
    vehicle2.trajectory = [
        (975, 900), (970, 870), (965, 840), (960, 810), (955, 800)
    ]
    vehicles.append(vehicle2)
    
    # Vehicle 3 - Speeding
    vehicle3 = TrackedVehicle(
        track_id=3,
        bbox=(1100, 500, 1250, 600),
        confidence=0.92,
        class_name="car"
    )
    vehicle3.trajectory = [
        (1175, 650), (1175, 620), (1175, 590), (1175, 560), (1175, 550)
    ]
    vehicles.append(vehicle3)
    
    return vehicles


def create_sample_speed_violations() -> list:
    """Create sample speed violations."""
    violations = []
    
    # Speed violation for vehicle 3
    speed_violation = SpeedViolation(
        vehicle_id=3,
        timestamp=time.time(),
        measured_speed=95.0,
        speed_limit=60.0,
        violation_amount=35.0,
        measurement_zone="highway_zone_1",
        confidence=0.9
    )
    violations.append(speed_violation)
    
    return violations


def example_basic_violation_detection():
    """Example: Basic violation detection workflow."""
    print("="*50)
    print("BASIC VIOLATION DETECTION EXAMPLE")
    print("="*50)
    
    # Initialize components
    detector = ViolationDetector()
    lane_detector = LaneDetector(1920, 1080)
    
    # Create sample data
    frame = create_sample_frame()
    vehicles = create_sample_vehicles()
    speed_violations = create_sample_speed_violations()
    
    print(f"Processing frame with {len(vehicles)} vehicles")
    
    # Detect lanes
    print("\n1. Detecting lanes...")
    lane_geometry = lane_detector.detect_lanes(frame)
    
    if lane_geometry.left_lane or lane_geometry.right_lane:
        print("✓ Lanes detected successfully")
        lane_mask = lane_detector.create_lane_mask(lane_geometry, frame.shape[:2])
    else:
        print("⚠ No lanes detected, using default mask")
        lane_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        lane_mask[400:1080, 500:1420] = 255  # Default lane area
    
    # Detect speed violations
    print("\n2. Detecting speed violations...")
    speed_viols = detector.detect_speed_violations(speed_violations, vehicles, frame)
    print(f"Found {len(speed_viols)} speed violations")
    
    for violation in speed_viols:
        print(f"  - Vehicle {violation.vehicle_id}: {violation.measured_speed:.1f} km/h "
              f"(limit: {violation.speed_limit:.1f} km/h, severity: {violation.severity.value})")
    
    # Detect lane violations
    print("\n3. Detecting lane violations...")
    lane_viols = detector.detect_lane_violations(vehicles, lane_mask, frame)
    print(f"Found {len(lane_viols)} lane violations")
    
    for violation in lane_viols:
        print(f"  - Vehicle {violation.vehicle_id}: Lane violation "
              f"(severity: {violation.severity.value})")
    
    # Detect wrong-way driving
    print("\n4. Detecting wrong-way driving...")
    expected_direction = np.array([0, -1])  # Upward movement expected
    wrong_way_viols = detector.detect_wrong_way_driving(vehicles, expected_direction, frame)
    print(f"Found {len(wrong_way_viols)} wrong-way violations")
    
    for violation in wrong_way_viols:
        print(f"  - Vehicle {violation.vehicle_id}: Wrong-way driving "
              f"(severity: {violation.severity.value})")
    
    # Detect following distance violations
    print("\n5. Detecting following distance violations...")
    following_viols = detector.detect_following_distance_violations(vehicles, frame)
    print(f"Found {len(following_viols)} following distance violations")
    
    for violation in following_viols:
        print(f"  - Vehicles {violation.vehicle_id}: Too close following "
              f"(severity: {violation.severity.value})")
    
    # Summary
    total_violations = len(speed_viols) + len(lane_viols) + len(wrong_way_viols) + len(following_viols)
    print(f"\nTotal violations detected: {total_violations}")
    
    return speed_viols + lane_viols + wrong_way_viols + following_viols


def example_notification_system():
    """Example: Notification system usage."""
    print("\n" + "="*50)
    print("NOTIFICATION SYSTEM EXAMPLE")
    print("="*50)
    
    # Initialize notification system
    notification_system = NotificationSystem()
    
    # Create a sample violation
    from src.violations.violation_detector import TrafficViolation, ViolationLocation
    
    violation = TrafficViolation(
        violation_id="example_001",
        timestamp=time.time(),
        violation_type=ViolationType.SPEED_VIOLATION,
        severity=ViolationSeverity.SEVERE,
        vehicle_id=1,
        description="Severe speed violation detected",
        confidence=0.95,
        location=ViolationLocation("zone_1", "Highway Section A", (960, 540)),
        speed_limit=60.0,
        measured_speed=110.0,
        license_plate="ABC-123"
    )
    
    print("Sending violation alert...")
    alert_id = notification_system.send_violation_alert(violation)
    
    if alert_id:
        print(f"✓ Alert sent successfully: {alert_id}")
    else:
        print("✗ Failed to send alert")
    
    # Check recent alerts
    recent_alerts = notification_system.get_recent_alerts(limit=5)
    print(f"\nRecent alerts: {len(recent_alerts)}")
    
    for alert in recent_alerts:
        print(f"  - {alert.alert_id}: {alert.priority.value} priority "
              f"({alert.violation.violation_type.value})")


def example_violation_manager():
    """Example: Complete violation management workflow."""
    print("\n" + "="*50)
    print("VIOLATION MANAGER EXAMPLE")
    print("="*50)
    
    # Initialize violation manager
    manager = ViolationManager()
    
    # Create sample data
    frame = create_sample_frame()
    vehicles = create_sample_vehicles()
    speed_violations = create_sample_speed_violations()
    
    print("Processing frame through violation manager...")
    
    # Process frame
    detected_violations = manager.process_frame(frame, vehicles, speed_violations)
    
    print(f"Detected {len(detected_violations)} violations")
    
    for violation in detected_violations:
        print(f"  - {violation.violation_type.value}: Vehicle {violation.vehicle_id} "
              f"(severity: {violation.severity.value})")
    
    # Get current statistics
    print("\nCurrent statistics:")
    stats = manager.get_current_statistics()
    print(f"  - Current violations: {stats.current_violations}")
    print(f"  - Daily total: {stats.daily_total}")
    print(f"  - Hourly rate: {stats.hourly_rate:.1f}")
    
    if stats.violations_by_type:
        print("  - By type:")
        for vtype, count in stats.violations_by_type.items():
            print(f"    * {vtype}: {count}")
    
    if stats.violations_by_severity:
        print("  - By severity:")
        for severity, count in stats.violations_by_severity.items():
            print(f"    * {severity}: {count}")
    
    # Generate report
    print("\nGenerating report...")
    end_time = time.time()
    start_time = end_time - 3600  # Last hour
    
    report = manager.generate_report(start_time, end_time)
    print(f"Report period: {report.period_start} to {report.period_end}")
    print(f"Total violations in period: {report.total_violations}")
    
    # System status
    print("\nSystem status:")
    status = manager.get_system_status()
    for component, component_status in status.items():
        if isinstance(component_status, dict) and "status" in component_status:
            print(f"  - {component}: {component_status['status']}")


def example_performance_monitoring():
    """Example: Performance monitoring during detection."""
    print("\n" + "="*50)
    print("PERFORMANCE MONITORING EXAMPLE")
    print("="*50)
    
    detector = ViolationDetector()
    
    # Create test data
    frames = [create_sample_frame() for _ in range(10)]
    vehicles_list = [create_sample_vehicles() for _ in range(10)]
    
    print("Processing 10 frames for performance measurement...")
    
    processing_times = []
    violation_counts = []
    
    for i, (frame, vehicles) in enumerate(zip(frames, vehicles_list)):
        start_time = time.perf_counter()
        
        # Simulate some processing
        lane_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        lane_mask[400:1080, 500:1420] = 255
        
        violations = detector.detect_lane_violations(vehicles, lane_mask, frame)
        
        end_time = time.perf_counter()
        processing_time = end_time - start_time
        
        processing_times.append(processing_time)
        violation_counts.append(len(violations))
        
        print(f"Frame {i+1}: {processing_time:.4f}s, {len(violations)} violations")
    
    # Calculate statistics
    avg_time = sum(processing_times) / len(processing_times)
    max_time = max(processing_times)
    min_time = min(processing_times)
    fps = 1.0 / avg_time if avg_time > 0 else 0
    total_violations = sum(violation_counts)
    
    print(f"\nPerformance Summary:")
    print(f"  - Average processing time: {avg_time:.4f}s")
    print(f"  - Min/Max processing time: {min_time:.4f}s / {max_time:.4f}s")
    print(f"  - Effective FPS: {fps:.1f}")
    print(f"  - Total violations detected: {total_violations}")


def example_configuration_customization():
    """Example: Customizing violation detection parameters."""
    print("\n" + "="*50)
    print("CONFIGURATION CUSTOMIZATION EXAMPLE")
    print("="*50)
    
    # Initialize detector
    detector = ViolationDetector()
    
    # Show default configuration
    print("Default speed thresholds:")
    print(f"  - Minor: {detector.speed_thresholds['minor']} km/h")
    print(f"  - Moderate: {detector.speed_thresholds['moderate']} km/h")
    print(f"  - Severe: {detector.speed_thresholds['severe']} km/h")
    print(f"  - Critical: {detector.speed_thresholds['critical']} km/h")
    
    # Customize thresholds
    print("\nCustomizing thresholds for school zone...")
    detector.speed_thresholds['minor'] = 5.0     # More strict for school zone
    detector.speed_thresholds['moderate'] = 10.0
    detector.speed_thresholds['severe'] = 20.0
    detector.speed_thresholds['critical'] = 30.0
    
    print("New speed thresholds:")
    print(f"  - Minor: {detector.speed_thresholds['minor']} km/h")
    print(f"  - Moderate: {detector.speed_thresholds['moderate']} km/h")
    print(f"  - Severe: {detector.speed_thresholds['severe']} km/h")
    print(f"  - Critical: {detector.speed_thresholds['critical']} km/h")
    
    # Customize cooldown periods
    print(f"\nDefault cooldown periods:")
    for vtype, period in detector.cooldown_periods.items():
        print(f"  - {vtype.value}: {period}s")
    
    print("\nCustomizing cooldown for high-traffic area...")
    detector.cooldown_periods[ViolationType.SPEED_VIOLATION] = 60.0  # Longer cooldown
    detector.cooldown_periods[ViolationType.LANE_VIOLATION] = 30.0
    
    print("New cooldown periods:")
    for vtype, period in detector.cooldown_periods.items():
        print(f"  - {vtype.value}: {period}s")


def main():
    """Run all examples."""
    print("TRAFFIC VIOLATIONS DETECTION - USAGE EXAMPLES")
    print("=" * 60)
    
    try:
        # Run examples
        violations = example_basic_violation_detection()
        example_notification_system()
        example_violation_manager()
        example_performance_monitoring()
        example_configuration_customization()
        
        print("\n" + "="*60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"Total violations processed: {len(violations)}")
        print("\nNext steps:")
        print("1. Integrate with your traffic monitoring system")
        print("2. Customize detection parameters for your use case")
        print("3. Configure notification channels")
        print("4. Set up automated reporting")
        print("5. Monitor performance in production")
        
    except Exception as e:
        print(f"\n✗ Example execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())