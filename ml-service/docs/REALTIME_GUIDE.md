"""
Real-time traffic analysis system documentation and deployment guide.

This module provides comprehensive real-time analysis capabilities
for traffic monitoring and violation detection.
"""

# Real-Time Traffic Analysis System

The real-time traffic analysis system integrates all ML components into a unified pipeline for comprehensive traffic monitoring and violation detection.

## Architecture Overview

### Core Components

1. **RealTimeAnalysisPipeline** (`analysis_pipeline.py`)
   - Orchestrates all ML components
   - Handles frame processing workflow
   - Manages pipeline state and metrics
   - Provides async processing capabilities

2. **VideoStreamService** (`stream_service.py`) 
   - Manages video stream connections (RTSP/file)
   - Handles automatic reconnection
   - Buffers frames for smooth processing
   - Supports multiple concurrent streams

3. **PerformanceMonitor** (`monitoring.py`)
   - System resource monitoring
   - Performance metrics collection
   - Alert system for anomalies
   - Violation analytics and trends

4. **API Server** (`api_server.py`)
   - REST API for system management
   - WebSocket for real-time updates
   - Stream control endpoints
   - Monitoring and metrics APIs

## Installation and Setup

### Prerequisites

```bash
# Install Python dependencies
pip install -r requirements.txt

# Additional dependencies for real-time processing
pip install fastapi uvicorn websockets psutil
```

### Configuration

1. **Pipeline Configuration** (`PipelineConfig`)
   ```python
   config = PipelineConfig(
       detection_model_path="models/yolov8n.onnx",
       target_fps=30.0,
       confidence_threshold=0.5,
       metrics_enabled=True,
       enable_speed_analysis=True,
       enable_violation_detection=True
   )
   ```

2. **Stream Configuration** (`StreamConfig`)
   ```python
   stream_config = StreamConfig(
       buffer_size=10,
       target_fps=30.0,
       reconnect_attempts=5,
       reconnect_delay=2.0
   )
   ```

## Usage Examples

### Basic Pipeline Usage

```python
from src.realtime.analysis_pipeline import RealTimeAnalysisPipeline, PipelineConfig

# Create configuration
config = PipelineConfig(
    detection_model_path="models/yolov8n.onnx",
    target_fps=30.0
)

# Initialize pipeline
pipeline = RealTimeAnalysisPipeline(config, device_id="main_camera")

# Process frames
frame = cv2.imread("test_frame.jpg")
result = pipeline.process_frame(frame)

print(f"Detected {len(result.detections)} vehicles")
print(f"Tracked {len(result.tracked_vehicles)} vehicles")
print(f"Found {len(result.violations)} violations")
```

### Stream Processing

```python
from src.realtime.stream_service import VideoStreamService, StreamConfig

# Configure stream
config = StreamConfig(buffer_size=10, target_fps=30.0)

# Create and start stream
stream = VideoStreamService("rtsp://camera.ip/stream", config)
stream.start()

# Process frames
while stream.is_running():
    frame = stream.get_latest_frame()
    if frame is not None:
        # Process frame with pipeline
        result = pipeline.process_frame(frame)
        
        # Handle results
        process_results(result)

stream.stop()
```

### Multi-Stream Management

```python
from src.realtime.stream_service import MultiStreamManager

manager = MultiStreamManager()

# Add multiple streams
manager.add_stream("cam_001", "rtsp://cam1.ip/stream", config)
manager.add_stream("cam_002", "rtsp://cam2.ip/stream", config)
manager.add_stream("cam_003", "rtsp://cam3.ip/stream", config)

# Start all streams
manager.start_all_streams()

# Process all streams
for stream_id in manager.get_active_streams():
    frame = manager.get_latest_frame(stream_id)
    if frame is not None:
        result = pipeline.process_frame(frame)
        process_stream_result(stream_id, result)
```

### Performance Monitoring

```python
from src.realtime.monitoring import PerformanceMonitor, AlertRule

# Create monitor with custom alert rules
monitor = PerformanceMonitor()

# Add alert rules
monitor.add_alert_rule(AlertRule(
    name="high_cpu",
    metric="cpu_percent",
    threshold=80.0,
    operator=">",
    severity="warning"
))

monitor.add_alert_rule(AlertRule(
    name="low_fps",
    metric="fps",
    threshold=15.0,
    operator="<",
    severity="critical"
))

# Start monitoring
monitor.start_monitoring()

# Check for alerts
alerts = monitor.get_active_alerts()
for alert in alerts:
    print(f"ALERT: {alert.rule_name} - {alert.message}")
```

### Violation Analytics

```python
from src.realtime.monitoring import ViolationAnalytics

analytics = ViolationAnalytics()

# Record violations
analytics.record_violation("speed_violation", "cam_001")
analytics.record_violation("red_light", "cam_002")

# Get trend analysis
trends = analytics.get_violation_trends(hours=24)
print(f"Speed violations in last 24h: {trends['speed_violation']}")

# Get hotspot analysis
hotspots = analytics.get_hotspot_analysis()
for device_id, count in hotspots.items():
    print(f"Device {device_id}: {count} violations")
```

### REST API Server

```python
from src.realtime.api_server import create_app
import uvicorn

# Create FastAPI app
app = create_app()

# Start server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## API Endpoints

### Stream Management
- `POST /streams` - Add new stream
- `GET /streams` - List all streams
- `GET /streams/{stream_id}` - Get stream info
- `POST /streams/{stream_id}/start` - Start stream
- `POST /streams/{stream_id}/stop` - Stop stream
- `DELETE /streams/{stream_id}` - Remove stream

### Monitoring
- `GET /monitoring/system` - Get system metrics
- `GET /monitoring/performance` - Get performance metrics
- `GET /monitoring/alerts` - Get active alerts

### Analytics
- `GET /analytics/violations/trends` - Get violation trends
- `GET /analytics/violations/hotspots` - Get violation hotspots
- `GET /analytics/violations/summary` - Get violation summary

### Real-time Updates (WebSocket)
- `WS /ws/realtime` - Real-time frame results
- `WS /ws/monitoring` - Real-time monitoring data
- `WS /ws/alerts` - Real-time alert notifications

## Performance Benchmarks

The system includes comprehensive benchmarks to validate performance:

### Frame Processing Performance
- **Target**: <200ms per frame processing
- **FPS Capability**: >5 FPS sustained processing
- **Memory Usage**: <500MB average

### Stream Handling Performance  
- **Multi-stream**: 4+ concurrent streams
- **FPS**: >15 FPS per stream
- **Drop Rate**: <10% frame drops

### System Monitoring
- **Monitoring Overhead**: <5% performance impact
- **Metrics Collection**: <50ms per collection cycle

### Analytics Performance
- **Violation Recording**: >1000 violations/second
- **Query Performance**: <100ms for trend analysis

## Deployment Considerations

### Hardware Requirements
- **CPU**: 8+ cores recommended for multi-stream processing
- **Memory**: 8GB+ RAM for optimal performance
- **GPU**: CUDA-capable GPU recommended for ML inference
- **Storage**: SSD recommended for model loading

### Network Requirements
- **Bandwidth**: 10Mbps+ per HD stream
- **Latency**: <100ms for real-time processing
- **Reliability**: Stable network for RTSP streams

### Production Setup

1. **Docker Deployment**
   ```bash
   # Build container
   docker build -t traffic-analysis .
   
   # Run with GPU support
   docker run --gpus all -p 8000:8000 traffic-analysis
   ```

2. **Environment Variables**
   ```bash
   export MODEL_PATH=/models/yolov8n.onnx
   export TARGET_FPS=30
   export ENABLE_MONITORING=true
   export API_HOST=0.0.0.0
   export API_PORT=8000
   ```

3. **Monitoring Setup**
   - Configure Prometheus metrics endpoint
   - Set up Grafana dashboards
   - Configure alert notifications

## Troubleshooting

### Common Issues

1. **High CPU Usage**
   - Reduce target FPS
   - Limit number of concurrent streams
   - Check for memory leaks

2. **Frame Drops**
   - Increase buffer size
   - Improve network connection
   - Optimize processing pipeline

3. **Memory Leaks**
   - Monitor memory usage trends
   - Check for unclosed resources
   - Review detection model efficiency

4. **Stream Connection Issues**
   - Verify RTSP URLs
   - Check network connectivity
   - Review authentication credentials

### Debug Mode

Enable debug logging for detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Pipeline will now log detailed processing information
pipeline = RealTimeAnalysisPipeline(config, device_id="debug")
```

### Performance Profiling

Use the benchmark suite to identify performance bottlenecks:

```bash
python benchmarks/benchmark_realtime.py
```

## Integration Examples

### With Backend API

```python
import requests

# Send violation to backend
def send_violation_to_backend(violation_data):
    response = requests.post(
        "http://backend:8000/api/violations/",
        json=violation_data,
        headers={"Authorization": "Bearer <token>"}
    )
    return response.status_code == 201

# Process violation
if result.violations:
    for violation in result.violations:
        violation_data = {
            "type": violation.violation_type,
            "device_id": violation.device_id,
            "timestamp": violation.timestamp.isoformat(),
            "severity": violation.severity,
            "image_path": violation.evidence_path
        }
        send_violation_to_backend(violation_data)
```

### With Notification System

```python
import smtplib
from email.mime.text import MIMEText

def send_alert_notification(alert):
    """Send email notification for critical alerts."""
    if alert.severity == "critical":
        msg = MIMEText(f"Critical alert: {alert.message}")
        msg['Subject'] = f"Traffic System Alert: {alert.rule_name}"
        msg['From'] = "alerts@traffic-system.com"
        msg['To'] = "admin@traffic-system.com"
        
        server = smtplib.SMTP('localhost')
        server.send_message(msg)
        server.quit()

# Monitor alerts
monitor = PerformanceMonitor()
monitor.start_monitoring()

while True:
    alerts = monitor.get_active_alerts()
    for alert in alerts:
        send_alert_notification(alert)
    time.sleep(30)
```

## Next Steps

This real-time analysis system provides a solid foundation for traffic monitoring. Consider these enhancements:

1. **Advanced Analytics**
   - Traffic flow analysis
   - Congestion detection
   - Predictive modeling

2. **Enhanced Visualization**
   - Real-time dashboards
   - Heat maps
   - Video overlays

3. **Integration Features**
   - External system APIs
   - Cloud storage
   - Mobile applications

4. **Scalability**
   - Distributed processing
   - Load balancing
   - Auto-scaling