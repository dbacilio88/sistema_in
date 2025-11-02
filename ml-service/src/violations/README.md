# Traffic Violations Detection System

A comprehensive traffic violations detection system that identifies various types of traffic infractions including speed violations, lane violations, wrong-way driving, and unsafe following distances.

## Features

### Violation Detection
- **Speed Violations**: Detects vehicles exceeding speed limits with configurable severity levels
- **Lane Violations**: Identifies vehicles crossing lane boundaries or driving outside designated lanes  
- **Wrong-Way Driving**: Detects vehicles traveling in the wrong direction
- **Following Distance**: Monitors unsafe following distances between vehicles
- **Configurable Rules**: Customizable violation rules and thresholds per zone

### Lane Detection
- **Advanced Lane Detection**: Uses Canny edge detection and Hough line transform
- **Polynomial Fitting**: Fits polynomial curves to detected lane markings
- **Lane Geometry Analysis**: Calculates lane width, curvature, and vehicle position
- **ROI Processing**: Focuses detection on relevant road areas

### Notification System
- **Multi-Channel Alerts**: Database, file, email, SMS, webhook, and API notifications
- **Priority-Based Routing**: Different notification channels based on violation severity
- **Rate Limiting**: Prevents notification spam with configurable rate limits
- **Template System**: Customizable alert message templates

### Violation Management
- **Central Coordination**: Unified management of all violation detection components
- **Database Integration**: SQLite database for violation storage and retrieval
- **Real-Time Statistics**: Live violation counts and trend analysis
- **Report Generation**: Automated periodic reports with detailed analytics
- **Evidence Management**: Stores violation evidence (images, metadata)

## Installation

### Prerequisites
```bash
pip install opencv-python numpy sqlite3 pytest psutil
```

### Setup
1. Run the initialization script:
```bash
python scripts/init_violations.py --base-dir /path/to/installation
```

2. This will create:
   - Directory structure for data, logs, and configuration
   - SQLite database with required tables
   - Default configuration file
   - Notification system setup

## Quick Start

### Basic Usage

```python
from src.violations.violation_manager import ViolationManager
from src.violations.violation_detector import ViolationDetector
import numpy as np

# Initialize the system
manager = ViolationManager()

# Create sample frame and vehicle data
frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
vehicles = []  # List of TrackedVehicle objects
speed_violations = []  # List of SpeedViolation objects

# Process frame for violations
violations = manager.process_frame(frame, vehicles, speed_violations)

# Print detected violations
for violation in violations:
    print(f"Violation: {violation.violation_type.value}")
    print(f"Vehicle: {violation.vehicle_id}")
    print(f"Severity: {violation.severity.value}")
```

### Speed Violation Detection

```python
from src.violations.violation_detector import ViolationDetector
from src.speed.speed_analyzer import SpeedViolation

detector = ViolationDetector()

# Create speed violation data
speed_violation = SpeedViolation(
    vehicle_id=1,
    timestamp=time.time(),
    measured_speed=85.0,
    speed_limit=60.0,
    violation_amount=25.0,
    measurement_zone="highway_1",
    confidence=0.9
)

# Detect violations
violations = detector.detect_speed_violations(
    [speed_violation], vehicles, frame
)
```

### Lane Violation Detection

```python
from src.violations.lane_detector import LaneDetector

lane_detector = LaneDetector(1920, 1080)

# Detect lanes in frame
lane_geometry = lane_detector.detect_lanes(frame)

# Create lane mask
lane_mask = lane_detector.create_lane_mask(lane_geometry, frame.shape[:2])

# Detect lane violations
lane_violations = detector.detect_lane_violations(vehicles, lane_mask, frame)
```

### Notification Setup

```python
from src.violations.notification_system import (
    NotificationSystem, NotificationConfig, NotificationChannel
)

notification_system = NotificationSystem()

# Configure email notifications
email_config = NotificationConfig(
    channel=NotificationChannel.EMAIL,
    enabled=True,
    config={
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "alerts@example.com",
        "password": "app_password",
        "recipients": ["traffic@example.com"]
    },
    rate_limit=10  # Max 10 emails per hour
)

notification_system.add_notification_config(email_config)

# Send violation alert
alert_id = notification_system.send_violation_alert(violation)
```

## Configuration

### Violation Detection Parameters

```json
{
  "violation_detection": {
    "speed_threshold_minor": 10.0,
    "speed_threshold_moderate": 20.0,
    "speed_threshold_severe": 40.0,
    "speed_threshold_critical": 60.0,
    "following_distance_min": 15.0,
    "wrong_way_angle_threshold": 90.0,
    "lane_violation_threshold": 0.3,
    "confidence_threshold": 0.7,
    "cooldown_periods": {
      "speed_violation": 30.0,
      "lane_violation": 15.0,
      "wrong_way": 60.0,
      "following_distance": 20.0
    }
  }
}
```

### Lane Detection Settings

```json
{
  "lane_detection": {
    "image_width": 1920,
    "image_height": 1080,
    "roi_height_ratio": 0.6,
    "roi_width_ratio": 0.8,
    "canny_low_threshold": 50,
    "canny_high_threshold": 150,
    "hough_threshold": 50,
    "hough_min_line_length": 100,
    "hough_max_line_gap": 50,
    "polynomial_degree": 2,
    "smoothing_factor": 0.7
  }
}
```

### Notification Configuration

```json
{
  "notifications": {
    "enabled_channels": ["database", "file", "email"],
    "rate_limits": {
      "email": 10,
      "sms": 5,
      "webhook": 100,
      "database": 1000,
      "file": 500
    },
    "priority_thresholds": {
      "critical": ["wrong_way", "severe_speed"],
      "high": ["moderate_speed", "lane_violation"],
      "medium": ["minor_speed", "following_distance"],
      "low": ["info"]
    }
  }
}
```

## API Reference

### ViolationDetector

Main class for detecting traffic violations.

#### Methods

- `detect_speed_violations(speed_violations, vehicles, frame)`: Detect speed violations
- `detect_lane_violations(vehicles, lane_mask, frame)`: Detect lane violations  
- `detect_wrong_way_driving(vehicles, expected_direction, frame)`: Detect wrong-way driving
- `detect_following_distance_violations(vehicles, frame)`: Detect unsafe following distances
- `add_violation_rule(rule)`: Add custom violation rule
- `get_statistics()`: Get violation detection statistics

### LaneDetector

Class for detecting lane markings and calculating lane geometry.

#### Methods

- `detect_lanes(image)`: Detect lane markings in image
- `create_lane_mask(lane_geometry, shape)`: Create lane validity mask
- `detect_vehicle_lane_position(vehicle_position, lane_geometry)`: Calculate vehicle lane position

### NotificationSystem

Multi-channel notification system for violation alerts.

#### Methods

- `send_violation_alert(violation)`: Send alert for violation
- `add_notification_config(config)`: Add notification channel configuration
- `get_recent_alerts(limit)`: Get recent alerts
- `get_notification_statistics()`: Get notification statistics

### ViolationManager

Central management system coordinating all violation detection components.

#### Methods

- `process_frame(frame, vehicles, speed_violations)`: Process frame for all violation types
- `get_current_statistics()`: Get real-time violation statistics
- `generate_report(start_time, end_time)`: Generate violation report
- `mark_false_positive(violation_id)`: Mark violation as false positive
- `get_system_status()`: Get system health status

## Data Models

### TrafficViolation

```python
@dataclass
class TrafficViolation:
    violation_id: str
    timestamp: float
    violation_type: ViolationType
    severity: ViolationSeverity
    vehicle_id: int
    description: str
    confidence: float
    location: ViolationLocation
    # Type-specific fields
    speed_limit: Optional[float] = None
    measured_speed: Optional[float] = None
    license_plate: Optional[str] = None
    evidence_path: Optional[str] = None
```

### ViolationType

```python
class ViolationType(Enum):
    SPEED_VIOLATION = "speed_violation"
    LANE_VIOLATION = "lane_violation"
    WRONG_WAY = "wrong_way"
    FOLLOWING_DISTANCE = "following_distance"
    RED_LIGHT = "red_light"
    STOP_SIGN = "stop_sign"
    PARKING_VIOLATION = "parking_violation"
```

### ViolationSeverity

```python
class ViolationSeverity(Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"
```

## Testing

### Run Tests

```bash
# Run all tests
python -m pytest tests/test_violations.py -v

# Run specific test class
python -m pytest tests/test_violations.py::TestViolationDetector -v

# Run with coverage
python -m pytest tests/test_violations.py --cov=src.violations
```

### Run Benchmarks

```bash
# Run performance benchmarks
python benchmarks/benchmark_violations.py

# Run specific benchmark
python -c "
from benchmarks.benchmark_violations import BenchmarkViolationDetector
bench = BenchmarkViolationDetector()
bench.setup_method()
bench.test_speed_violation_detection_performance()
"
```

## Performance

### Typical Performance Metrics

- **Speed Violation Detection**: ~10-50ms per frame (10+ vehicles)
- **Lane Detection**: ~200-300ms per frame (1920x1080)
- **Notification Processing**: ~50-100ms per alert
- **Database Storage**: ~100+ violations per second
- **Memory Usage**: ~50-100MB for active processing

### Optimization Tips

1. **ROI Processing**: Limit lane detection to relevant image areas
2. **Batch Processing**: Process multiple violations together
3. **Caching**: Cache lane detection results for consecutive frames
4. **Database Indexing**: Index frequently queried fields
5. **Notification Batching**: Batch non-critical notifications

## Integration

### With Speed Analysis System

```python
from src.speed.speed_analyzer import SpeedAnalyzer
from src.violations.violation_manager import ViolationManager

speed_analyzer = SpeedAnalyzer()
violation_manager = ViolationManager()

# Process frame
speed_violations = speed_analyzer.analyze_frame(frame, vehicles)
all_violations = violation_manager.process_frame(frame, vehicles, speed_violations)
```

### With Vehicle Tracking

```python
from src.tracking.vehicle_tracker import VehicleTracker
from src.violations.violation_detector import ViolationDetector

tracker = VehicleTracker()
detector = ViolationDetector()

# Track vehicles and detect violations
vehicles = tracker.track_frame(frame)
violations = detector.detect_lane_violations(vehicles, lane_mask, frame)
```

## Examples

Complete usage examples are available in:
- `examples/violations_usage.py` - Basic usage patterns
- `scripts/init_violations.py` - System initialization
- `tests/test_violations.py` - Test examples

## Troubleshooting

### Common Issues

1. **Lane Detection Fails**
   - Check image quality and lighting conditions
   - Adjust Canny and Hough transform parameters
   - Verify ROI settings for your camera setup

2. **High False Positive Rate**
   - Increase confidence thresholds
   - Adjust violation-specific parameters
   - Implement additional filtering rules

3. **Performance Issues**
   - Reduce image resolution for processing
   - Optimize ROI to focus on relevant areas
   - Use frame skipping for less critical detections

4. **Database Errors**
   - Check database permissions and disk space
   - Verify SQLite database file integrity
   - Monitor database connection pool

### Logging

Enable debug logging for detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Component-specific logging
logging.getLogger('violations.detector').setLevel(logging.DEBUG)
logging.getLogger('violations.notification').setLevel(logging.INFO)
```

## Contributing

1. Follow the existing code structure and patterns
2. Add comprehensive tests for new features
3. Update documentation and examples
4. Run benchmarks to ensure performance standards
5. Test integration with existing components

## License

This traffic violations detection system is part of the comprehensive traffic monitoring solution.