"""
Test suite for real-time traffic analysis system.

Comprehensive tests for the real-time analysis pipeline, stream processing,
and monitoring components.
"""

import pytest
import asyncio
import time
import threading
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict

from ..analysis_pipeline import (
    RealTimeAnalysisPipeline, PipelineConfig, StreamProcessor,
    FrameData, ProcessingResult, StreamMetrics
)
from ..stream_service import VideoStreamService, StreamConfig, MultiStreamManager
from ..monitoring import PerformanceMonitor, ViolationAnalytics, AlertRule, Alert
from ...detection.yolo_detector import Detection
from ...tracking.vehicle_tracker import TrackedVehicle
from ...violations.violation_detector import TrafficViolation, ViolationType, ViolationSeverity


class TestRealTimeAnalysisPipeline:
    """Test the real-time analysis pipeline."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.config = PipelineConfig(
            detection_model_path="test_model.onnx",
            target_fps=30.0,
            metrics_enabled=True
        )
        self.device_id = "test_camera_001"
        
        # Mock the ML components to avoid loading actual models
        with patch('src.detection.yolo_detector.YOLODetector'), \
             patch('src.tracking.vehicle_tracker.VehicleTracker'), \
             patch('src.plate_recognition.plate_detector.PlateDetector'), \
             patch('src.speed.speed_analyzer.SpeedAnalyzer'), \
             patch('src.violations.violation_manager.ViolationManager'):
            
            self.pipeline = RealTimeAnalysisPipeline(self.config, self.device_id)
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        assert self.pipeline.device_id == self.device_id
        assert self.pipeline.config == self.config
        assert not self.pipeline.is_running
        assert self.pipeline.frame_counter == 0
        assert len(self.pipeline.frame_buffer) == 0
    
    def test_pipeline_start_stop(self):
        """Test pipeline start and stop."""
        # Test start
        self.pipeline.start()
        assert self.pipeline.is_running
        assert self.pipeline.start_time is not None
        assert self.pipeline.frame_counter == 0
        
        # Test stop
        self.pipeline.stop()
        assert not self.pipeline.is_running
    
    def test_frame_processing(self):
        """Test processing a single frame."""
        # Create test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Mock detection results
        mock_detections = [
            Mock(spec=Detection),
            Mock(spec=Detection)
        ]
        mock_detections[0].bbox = (100, 100, 200, 200)
        mock_detections[0].confidence = 0.8
        mock_detections[0].class_name = "car"
        
        self.pipeline.detector.detect.return_value = mock_detections
        
        # Mock tracking results
        mock_vehicles = [Mock(spec=TrackedVehicle)]
        mock_vehicles[0].track_id = 1
        mock_vehicles[0].bbox = (100, 100, 200, 200)
        
        self.pipeline.tracker.update.return_value = mock_vehicles
        
        # Mock other components
        self.pipeline.plate_detector.detect_and_read.return_value = []
        self.pipeline.speed_analyzer.calculate_speed.return_value = None
        self.pipeline.violation_manager.process_frame.return_value = []
        
        # Process frame
        result = self.pipeline.process_frame(test_frame)
        
        # Verify results
        assert isinstance(result, ProcessingResult)
        assert result.success
        assert len(result.detections) == 2
        assert len(result.tracked_vehicles) == 1
        assert result.processing_time_ms > 0
    
    def test_metrics_update(self):
        """Test metrics tracking."""
        # Create test frame and process
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Mock components
        self.pipeline.detector.detect.return_value = []
        self.pipeline.tracker.update.return_value = []
        
        initial_frames = self.pipeline.metrics.frames_processed
        
        # Process frame
        result = self.pipeline.process_frame(test_frame)
        
        # Check metrics updated
        assert self.pipeline.metrics.frames_processed == initial_frames + 1
        assert self.pipeline.frame_counter == 1
    
    def test_pipeline_status(self):
        """Test pipeline status reporting."""
        status = self.pipeline.get_status()
        
        assert "device_id" in status
        assert "is_running" in status
        assert "metrics" in status
        assert "components" in status
        assert "configuration" in status
        
        assert status["device_id"] == self.device_id
        assert isinstance(status["metrics"], dict)


class TestVideoStreamService:
    """Test video stream service."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.config = StreamConfig(
            buffer_size=5,
            target_fps=30.0,
            reconnect_attempts=3
        )
        
        # Use a test video file path (won't actually open in tests)
        self.source = "test_video.mp4"
    
    def test_stream_initialization(self):
        """Test stream service initialization."""
        stream = VideoStreamService(self.source, self.config)
        
        assert stream.source == self.source
        assert stream.config == self.config
        assert not stream.is_running
        assert stream.capture is None
        assert len(stream.frame_buffer) == 0
    
    @patch('cv2.VideoCapture')
    def test_stream_connection(self, mock_capture):
        """Test stream connection."""
        # Mock successful connection
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_capture.return_value = mock_cap
        
        stream = VideoStreamService(self.source, self.config)
        
        # Test connection
        success = stream._connect()
        assert success
        assert stream.stats.is_connected
    
    @patch('cv2.VideoCapture')
    def test_stream_connection_failure(self, mock_capture):
        """Test stream connection failure."""
        # Mock failed connection
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False
        mock_capture.return_value = mock_cap
        
        stream = VideoStreamService(self.source, self.config)
        
        # Test connection failure
        success = stream._connect()
        assert not success
        assert not stream.stats.is_connected
    
    def test_stream_statistics(self):
        """Test stream statistics tracking."""
        stream = VideoStreamService(self.source, self.config)
        
        # Check initial stats
        stats = stream.get_statistics()
        assert stats.frames_read == 0
        assert stats.frames_dropped == 0
        assert stats.fps == 0.0
        assert not stats.is_connected
    
    def test_stream_health_check(self):
        """Test stream health checking."""
        stream = VideoStreamService(self.source, self.config)
        
        # Initially unhealthy
        assert not stream.is_healthy()
        
        # Mock connected state
        stream.stats.is_connected = True
        stream.is_running = True
        stream.stats.last_frame_time = time.time()
        
        # Should be healthy now
        assert stream.is_healthy()


class TestMultiStreamManager:
    """Test multi-stream manager."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.manager = MultiStreamManager()
        self.config = StreamConfig()
    
    @patch('src.realtime.stream_service.VideoStreamService')
    def test_add_stream(self, mock_stream_service):
        """Test adding a stream."""
        mock_stream = Mock()
        mock_stream_service.return_value = mock_stream
        
        success = self.manager.add_stream("cam001", "rtsp://test", self.config)
        
        assert success
        assert "cam001" in self.manager.streams
        assert "cam001" in self.manager.stream_configs
    
    def test_add_duplicate_stream(self):
        """Test adding duplicate stream."""
        with patch('src.realtime.stream_service.VideoStreamService'):
            # Add first stream
            self.manager.add_stream("cam001", "rtsp://test", self.config)
            
            # Try to add duplicate
            success = self.manager.add_stream("cam001", "rtsp://test2", self.config)
            assert not success
    
    def test_remove_stream(self):
        """Test removing a stream."""
        with patch('src.realtime.stream_service.VideoStreamService'):
            # Add stream
            self.manager.add_stream("cam001", "rtsp://test", self.config)
            
            # Remove stream
            success = self.manager.remove_stream("cam001")
            assert success
            assert "cam001" not in self.manager.streams
    
    def test_aggregated_stats(self):
        """Test aggregated statistics."""
        with patch('src.realtime.stream_service.VideoStreamService'):
            # Add mock streams
            mock_stream1 = Mock()
            mock_stream1.stats.frames_read = 100
            mock_stream1.stats.frames_dropped = 5
            mock_stream1.stats.total_errors = 2
            mock_stream1.stats.fps = 25.0
            
            mock_stream2 = Mock()
            mock_stream2.stats.frames_read = 200
            mock_stream2.stats.frames_dropped = 10
            mock_stream2.stats.total_errors = 1
            mock_stream2.stats.fps = 28.0
            
            self.manager.streams["cam001"] = mock_stream1
            self.manager.streams["cam002"] = mock_stream2
            
            # Get aggregated stats
            stats = self.manager.get_aggregated_stats()
            
            assert stats["total_streams"] == 2
            assert stats["total_frames_read"] == 300
            assert stats["total_frames_dropped"] == 15
            assert stats["total_errors"] == 3
            assert stats["average_fps"] == 26.5


class TestPerformanceMonitor:
    """Test performance monitoring system."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.monitor = PerformanceMonitor(monitoring_interval=0.1)  # Fast interval for testing
    
    def test_monitor_initialization(self):
        """Test monitor initialization."""
        assert not self.monitor.is_monitoring
        assert len(self.monitor.alert_rules) > 0  # Default rules should be loaded
        assert len(self.monitor.active_alerts) == 0
    
    def test_system_metrics_collection(self):
        """Test system metrics collection."""
        self.monitor._collect_system_metrics()
        
        metrics = self.monitor.system_metrics
        assert metrics.cpu_percent >= 0
        assert metrics.memory_percent >= 0
        assert metrics.memory_used_mb >= 0
        assert metrics.process_cpu_percent >= 0
    
    def test_alert_rule_management(self):
        """Test alert rule management."""
        rule = AlertRule(
            rule_id="test_rule",
            name="Test Rule",
            description="Test alert rule",
            metric_path="system.cpu_percent",
            threshold=50.0,
            comparison="greater",
            duration_seconds=10.0
        )
        
        # Add rule
        self.monitor.add_alert_rule(rule)
        assert "test_rule" in self.monitor.alert_rules
        
        # Remove rule
        self.monitor.remove_alert_rule("test_rule")
        assert "test_rule" not in self.monitor.alert_rules
    
    def test_pipeline_metrics_update(self):
        """Test pipeline metrics updates."""
        metrics = StreamMetrics()
        metrics.frames_processed = 100
        metrics.fps = 25.0
        metrics.violations_count = 5
        
        self.monitor.update_pipeline_metrics("cam001", metrics)
        
        assert "cam001" in self.monitor.pipeline_metrics
        assert self.monitor.pipeline_metrics["cam001"] == metrics
    
    def test_aggregated_metrics_calculation(self):
        """Test aggregated metrics calculation."""
        # Add mock pipeline metrics
        metrics1 = StreamMetrics()
        metrics1.frames_processed = 100
        metrics1.fps = 25.0
        metrics1.violations_count = 5
        
        metrics2 = StreamMetrics()
        metrics2.frames_processed = 200
        metrics2.fps = 30.0
        metrics2.violations_count = 3
        
        self.monitor.pipeline_metrics["cam001"] = metrics1
        self.monitor.pipeline_metrics["cam002"] = metrics2
        
        self.monitor._update_aggregated_metrics()
        
        aggregated = self.monitor.aggregated_metrics
        assert aggregated["total_frames"] == 300
        assert aggregated["total_violations"] == 8
        assert aggregated["avg_fps"] == 27.5
    
    @patch('time.time')
    def test_alert_generation(self, mock_time):
        """Test alert generation."""
        mock_time.return_value = 1000.0
        
        # Create rule that should trigger
        rule = AlertRule(
            rule_id="test_alert",
            name="Test Alert",
            description="Test alert for high CPU",
            metric_path="system.cpu_percent",
            threshold=10.0,  # Low threshold to trigger easily
            comparison="greater",
            duration_seconds=1.0,
            cooldown_seconds=60.0
        )
        
        self.monitor.add_alert_rule(rule)
        
        # Set high CPU to trigger alert
        self.monitor.system_metrics.cpu_percent = 50.0
        
        # Set condition start time
        rule.condition_start = 990.0  # 10 seconds ago
        
        # Check rules (should trigger alert)
        self.monitor._check_alert_rules()
        
        # Verify alert was created
        assert len(self.monitor.active_alerts) > 0


class TestViolationAnalytics:
    """Test violation analytics system."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.analytics = ViolationAnalytics(retention_days=7)
    
    def test_analytics_initialization(self):
        """Test analytics initialization."""
        assert len(self.analytics.violation_history) == 0
        assert len(self.analytics.violation_stats) == 0
    
    def test_violation_recording(self):
        """Test violation recording."""
        # Record some violations
        self.analytics.record_violation("speed_violation", "cam001", 1000.0)
        self.analytics.record_violation("lane_violation", "cam001", 1001.0)
        self.analytics.record_violation("speed_violation", "cam002", 1002.0)
        
        # Check statistics
        assert len(self.analytics.violation_history) == 3
        assert self.analytics.violation_stats["speed_violation"] == 2
        assert self.analytics.violation_stats["lane_violation"] == 1
        assert self.analytics.location_stats["cam001"]["speed_violation"] == 1
        assert self.analytics.location_stats["cam001"]["lane_violation"] == 1
    
    def test_violation_trends(self):
        """Test violation trend analysis."""
        current_time = time.time()
        
        # Record violations over time
        for i in range(10):
            self.analytics.record_violation(
                "speed_violation", 
                "cam001", 
                current_time - (i * 3600)  # One per hour
            )
        
        # Get trends for last 24 hours
        trends = self.analytics.get_violation_trends(24)
        
        assert trends["total_violations"] == 10
        assert trends["by_type"]["speed_violation"] == 10
        assert trends["violations_per_hour"] == 10 / 24
    
    def test_hotspot_analysis(self):
        """Test hotspot analysis."""
        # Record violations at different locations
        self.analytics.record_violation("speed_violation", "cam001")
        self.analytics.record_violation("speed_violation", "cam001")
        self.analytics.record_violation("speed_violation", "cam001")
        self.analytics.record_violation("lane_violation", "cam002")
        self.analytics.record_violation("speed_violation", "cam003")
        
        hotspots = self.analytics.get_hotspot_analysis()
        
        # cam001 should be the top hotspot with 3 violations
        assert hotspots["hotspots"][0][0] == "cam001"
        assert hotspots["hotspots"][0][1] == 3
        assert hotspots["total_locations"] == 3
    
    def test_current_statistics(self):
        """Test current statistics."""
        # Record some violations
        self.analytics.record_violation("speed_violation", "cam001")
        self.analytics.record_violation("lane_violation", "cam002")
        
        stats = self.analytics.get_current_stats()
        
        assert stats["total_violations"] == 2
        assert stats["total_by_type"]["speed_violation"] == 1
        assert stats["total_by_type"]["lane_violation"] == 1
        assert stats["active_locations"] == 2


class TestStreamProcessor:
    """Test stream processor integration."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.processor = StreamProcessor()
    
    def test_processor_initialization(self):
        """Test processor initialization."""
        assert len(self.processor.pipelines) == 0
        assert len(self.processor.streams) == 0
        assert len(self.processor.processing_tasks) == 0
    
    @patch('cv2.VideoCapture')
    @patch('src.detection.yolo_detector.YOLODetector')
    @patch('src.tracking.vehicle_tracker.VehicleTracker')
    @patch('src.violations.violation_manager.ViolationManager')
    def test_add_camera_stream(self, mock_violation_manager, mock_tracker, mock_detector, mock_capture):
        """Test adding a camera stream."""
        # Mock successful video capture
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_capture.return_value = mock_cap
        
        config = PipelineConfig()
        
        # Add camera stream
        self.processor.add_camera_stream("cam001", "rtsp://test", config)
        
        assert "cam001" in self.processor.pipelines
        assert "cam001" in self.processor.streams
    
    def test_remove_camera_stream(self):
        """Test removing a camera stream."""
        with patch('cv2.VideoCapture'), \
             patch('src.detection.yolo_detector.YOLODetector'), \
             patch('src.tracking.vehicle_tracker.VehicleTracker'), \
             patch('src.violations.violation_manager.ViolationManager'):
            
            config = PipelineConfig()
            
            # Add and then remove
            self.processor.add_camera_stream("cam001", "rtsp://test", config)
            self.processor.remove_camera_stream("cam001")
            
            assert "cam001" not in self.processor.pipelines
            assert "cam001" not in self.processor.streams
    
    def test_aggregated_metrics(self):
        """Test aggregated metrics calculation."""
        # Test with no pipelines
        metrics = self.processor.get_aggregated_metrics()
        assert metrics["total_streams"] == 0
        assert metrics["active_streams"] == 0
        
        # Add mock pipelines
        with patch('cv2.VideoCapture'), \
             patch('src.detection.yolo_detector.YOLODetector'), \
             patch('src.tracking.vehicle_tracker.VehicleTracker'), \
             patch('src.violations.violation_manager.ViolationManager'):
            
            config = PipelineConfig()
            self.processor.add_camera_stream("cam001", "rtsp://test", config)
            
            # Mock some metrics
            pipeline = self.processor.pipelines["cam001"]
            pipeline.metrics.frames_processed = 100
            pipeline.metrics.violations_count = 5
            pipeline.metrics.fps = 25.0
            
            metrics = self.processor.get_aggregated_metrics()
            assert metrics["total_streams"] == 1
            assert metrics["total_frames"] == 100
            assert metrics["total_violations"] == 5


# Integration tests
class TestRealTimeIntegration:
    """Integration tests for the complete real-time system."""
    
    @pytest.mark.asyncio
    async def test_full_pipeline_integration(self):
        """Test complete pipeline integration with mock data."""
        # This test would require extensive mocking and is mainly for
        # integration testing in a real environment
        pass
    
    def test_performance_under_load(self):
        """Test system performance under simulated load."""
        # This test would simulate multiple streams and high frame rates
        # to validate performance characteristics
        pass