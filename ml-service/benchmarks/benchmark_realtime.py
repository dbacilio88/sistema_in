"""
Benchmark suite for real-time traffic analysis system.

Performance benchmarks for pipeline processing, stream handling,
and system monitoring components.
"""

import time
import asyncio
import threading
import numpy as np
import cv2
import pytest
import statistics
from typing import List, Dict, Any
from unittest.mock import Mock, patch
import psutil
import os

from ..analysis_pipeline import RealTimeAnalysisPipeline, PipelineConfig
from ..stream_service import VideoStreamService, StreamConfig, MultiStreamManager
from ..monitoring import PerformanceMonitor, ViolationAnalytics
from ...detection.yolo_detector import Detection
from ...tracking.vehicle_tracker import TrackedVehicle


class PerformanceMetrics:
    """Container for performance metrics."""
    
    def __init__(self):
        self.processing_times: List[float] = []
        self.memory_usage: List[float] = []
        self.cpu_usage: List[float] = []
        self.fps_measurements: List[float] = []
        self.latency_measurements: List[float] = []
        
    def add_measurement(self, processing_time: float, memory_mb: float = None, 
                       cpu_percent: float = None, fps: float = None, latency_ms: float = None):
        """Add performance measurement."""
        self.processing_times.append(processing_time)
        if memory_mb is not None:
            self.memory_usage.append(memory_mb)
        if cpu_percent is not None:
            self.cpu_usage.append(cpu_percent)
        if fps is not None:
            self.fps_measurements.append(fps)
        if latency_ms is not None:
            self.latency_measurements.append(latency_ms)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = {}
        
        if self.processing_times:
            stats['processing_time'] = {
                'mean': statistics.mean(self.processing_times),
                'median': statistics.median(self.processing_times),
                'std': statistics.stdev(self.processing_times) if len(self.processing_times) > 1 else 0,
                'min': min(self.processing_times),
                'max': max(self.processing_times),
                'p95': np.percentile(self.processing_times, 95),
                'p99': np.percentile(self.processing_times, 99)
            }
        
        if self.memory_usage:
            stats['memory'] = {
                'mean_mb': statistics.mean(self.memory_usage),
                'max_mb': max(self.memory_usage),
                'min_mb': min(self.memory_usage)
            }
        
        if self.cpu_usage:
            stats['cpu'] = {
                'mean_percent': statistics.mean(self.cpu_usage),
                'max_percent': max(self.cpu_usage)
            }
        
        if self.fps_measurements:
            stats['fps'] = {
                'mean': statistics.mean(self.fps_measurements),
                'min': min(self.fps_measurements),
                'max': max(self.fps_measurements)
            }
        
        if self.latency_measurements:
            stats['latency'] = {
                'mean_ms': statistics.mean(self.latency_measurements),
                'p95_ms': np.percentile(self.latency_measurements, 95),
                'p99_ms': np.percentile(self.latency_measurements, 99)
            }
        
        return stats


class BenchmarkRealTimePipeline:
    """Benchmark real-time analysis pipeline performance."""
    
    def setup_method(self):
        """Setup benchmark fixtures."""
        self.config = PipelineConfig(
            detection_model_path="test_model.onnx",
            target_fps=30.0,
            metrics_enabled=True
        )
        
        # Generate test data
        self.test_frames = self._generate_test_frames(100)
        self.test_detections = self._generate_test_detections(50)
        self.test_vehicles = self._generate_test_vehicles(50)
        
        self.metrics = PerformanceMetrics()
    
    def _generate_test_frames(self, count: int) -> List[np.ndarray]:
        """Generate test video frames."""
        frames = []
        for i in range(count):
            # Create realistic frame with some content
            frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
            
            # Add some shapes to simulate vehicles
            cv2.rectangle(frame, (100 + i*5, 200 + i*3), (200 + i*5, 300 + i*3), (255, 255, 255), -1)
            cv2.rectangle(frame, (500 + i*3, 400 + i*2), (600 + i*3, 500 + i*2), (128, 128, 128), -1)
            
            frames.append(frame)
        
        return frames
    
    def _generate_test_detections(self, count: int) -> List[List[Detection]]:
        """Generate test detection results."""
        detection_sets = []
        
        for i in range(count):
            detections = []
            num_detections = np.random.randint(0, 8)  # 0-7 vehicles per frame
            
            for j in range(num_detections):
                detection = Mock(spec=Detection)
                detection.bbox = (
                    100 + j*150 + np.random.randint(-20, 20),
                    200 + j*100 + np.random.randint(-15, 15),
                    200 + j*150 + np.random.randint(-20, 20),
                    300 + j*100 + np.random.randint(-15, 15)
                )
                detection.confidence = 0.7 + np.random.random() * 0.3
                detection.class_name = "car"
                detections.append(detection)
            
            detection_sets.append(detections)
        
        return detection_sets
    
    def _generate_test_vehicles(self, count: int) -> List[List[TrackedVehicle]]:
        """Generate test tracked vehicles."""
        vehicle_sets = []
        
        for i in range(count):
            vehicles = []
            num_vehicles = np.random.randint(0, 6)  # 0-5 tracked vehicles
            
            for j in range(num_vehicles):
                vehicle = Mock(spec=TrackedVehicle)
                vehicle.track_id = j + 1
                vehicle.bbox = (
                    120 + j*140 + np.random.randint(-15, 15),
                    220 + j*90 + np.random.randint(-10, 10),
                    220 + j*140 + np.random.randint(-15, 15),
                    320 + j*90 + np.random.randint(-10, 10)
                )
                vehicle.confidence = 0.8 + np.random.random() * 0.2
                vehicle.trajectory = [
                    (120 + j*140 + k*5, 220 + j*90 + k*3) 
                    for k in range(10)
                ]
                vehicles.append(vehicle)
            
            vehicle_sets.append(vehicles)
        
        return vehicle_sets
    
    def test_single_frame_processing_performance(self):
        """Benchmark single frame processing."""
        print("\n=== Single Frame Processing Benchmark ===")
        
        with patch('src.detection.yolo_detector.YOLODetector'), \
             patch('src.tracking.vehicle_tracker.VehicleTracker'), \
             patch('src.plate_recognition.plate_detector.PlateDetector'), \
             patch('src.speed.speed_analyzer.SpeedAnalyzer'), \
             patch('src.violations.violation_manager.ViolationManager'):
            
            pipeline = RealTimeAnalysisPipeline(self.config, "benchmark_cam")
            
            # Mock component responses
            pipeline.detector.detect.side_effect = self.test_detections
            pipeline.tracker.update.side_effect = self.test_vehicles
            pipeline.plate_detector.detect_and_read.return_value = []
            pipeline.speed_analyzer.calculate_speed.return_value = None
            pipeline.violation_manager.process_frame.return_value = []
            
            # Benchmark processing
            processing_times = []
            
            for i, frame in enumerate(self.test_frames[:50]):  # Test 50 frames
                start_time = time.perf_counter()
                
                result = pipeline.process_frame(frame)
                
                end_time = time.perf_counter()
                processing_time = (end_time - start_time) * 1000  # Convert to ms
                
                processing_times.append(processing_time)
                
                # Get memory usage
                process = psutil.Process(os.getpid())
                memory_mb = process.memory_info().rss / 1024 / 1024
                
                self.metrics.add_measurement(
                    processing_time=processing_time,
                    memory_mb=memory_mb,
                    fps=1000/processing_time if processing_time > 0 else 0,
                    latency_ms=processing_time
                )
        
        stats = self.metrics.get_statistics()
        
        print(f"Single Frame Processing Results:")
        print(f"  Mean processing time: {stats['processing_time']['mean']:.2f}ms")
        print(f"  Median processing time: {stats['processing_time']['median']:.2f}ms")
        print(f"  95th percentile: {stats['processing_time']['p95']:.2f}ms")
        print(f"  99th percentile: {stats['processing_time']['p99']:.2f}ms")
        print(f"  Mean FPS capability: {stats['fps']['mean']:.1f}")
        print(f"  Mean memory usage: {stats['memory']['mean_mb']:.1f}MB")
        
        # Performance assertions
        assert stats['processing_time']['mean'] < 200  # Should process under 200ms
        assert stats['fps']['mean'] > 5  # Should handle at least 5 FPS
        assert stats['memory']['mean_mb'] < 500  # Should use less than 500MB
    
    def test_sustained_processing_performance(self):
        """Benchmark sustained processing over time."""
        print("\n=== Sustained Processing Benchmark ===")
        
        with patch('src.detection.yolo_detector.YOLODetector'), \
             patch('src.tracking.vehicle_tracker.VehicleTracker'), \
             patch('src.plate_recognition.plate_detector.PlateDetector'), \
             patch('src.speed.speed_analyzer.SpeedAnalyzer'), \
             patch('src.violations.violation_manager.ViolationManager'):
            
            pipeline = RealTimeAnalysisPipeline(self.config, "sustained_benchmark")
            
            # Mock components
            pipeline.detector.detect.return_value = self.test_detections[0]
            pipeline.tracker.update.return_value = self.test_vehicles[0]
            pipeline.plate_detector.detect_and_read.return_value = []
            pipeline.speed_analyzer.calculate_speed.return_value = None
            pipeline.violation_manager.process_frame.return_value = []
            
            # Benchmark sustained processing (simulate 10 seconds at 30 FPS)
            target_fps = 30
            duration_seconds = 10
            target_frames = target_fps * duration_seconds
            
            processing_times = []
            frame_intervals = []
            last_frame_time = time.perf_counter()
            
            for i in range(target_frames):
                frame = self.test_frames[i % len(self.test_frames)]
                
                start_time = time.perf_counter()
                result = pipeline.process_frame(frame)
                end_time = time.perf_counter()
                
                processing_time = (end_time - start_time) * 1000
                processing_times.append(processing_time)
                
                # Calculate actual frame interval
                current_time = time.perf_counter()
                frame_interval = current_time - last_frame_time
                frame_intervals.append(frame_interval)
                last_frame_time = current_time
                
                # Simulate frame rate timing
                target_interval = 1.0 / target_fps
                sleep_time = max(0, target_interval - (end_time - start_time))
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        # Calculate actual achieved FPS
        actual_fps = len(frame_intervals) / sum(frame_intervals) if frame_intervals else 0
        avg_processing_time = statistics.mean(processing_times)
        max_processing_time = max(processing_times)
        
        print(f"Sustained Processing Results:")
        print(f"  Target FPS: {target_fps}")
        print(f"  Actual FPS: {actual_fps:.1f}")
        print(f"  Frames processed: {len(processing_times)}")
        print(f"  Avg processing time: {avg_processing_time:.2f}ms")
        print(f"  Max processing time: {max_processing_time:.2f}ms")
        print(f"  FPS efficiency: {(actual_fps/target_fps)*100:.1f}%")
        
        # Performance assertions
        assert actual_fps >= target_fps * 0.8  # Should achieve at least 80% of target FPS
        assert avg_processing_time < 25  # Should process frames in under 25ms on average
    
    def test_memory_usage_over_time(self):
        """Benchmark memory usage patterns."""
        print("\n=== Memory Usage Benchmark ===")
        
        with patch('src.detection.yolo_detector.YOLODetector'), \
             patch('src.tracking.vehicle_tracker.VehicleTracker'), \
             patch('src.violations.violation_manager.ViolationManager'):
            
            pipeline = RealTimeAnalysisPipeline(self.config, "memory_benchmark")
            
            # Mock components
            pipeline.detector.detect.return_value = []
            pipeline.tracker.update.return_value = []
            pipeline.violation_manager.process_frame.return_value = []
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024
            memory_measurements = [initial_memory]
            
            # Process many frames to check for memory leaks
            for i in range(200):
                frame = self.test_frames[i % len(self.test_frames)]
                pipeline.process_frame(frame)
                
                if i % 20 == 0:  # Sample memory every 20 frames
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_measurements.append(current_memory)
            
            final_memory = process.memory_info().rss / 1024 / 1024
            max_memory = max(memory_measurements)
            memory_growth = final_memory - initial_memory
            
            print(f"Memory Usage Results:")
            print(f"  Initial memory: {initial_memory:.1f}MB")
            print(f"  Final memory: {final_memory:.1f}MB")
            print(f"  Max memory: {max_memory:.1f}MB")
            print(f"  Memory growth: {memory_growth:.1f}MB")
            print(f"  Memory efficiency: {'PASS' if memory_growth < 50 else 'FAIL'}")
            
            # Memory assertions
            assert memory_growth < 100  # Should not grow more than 100MB
            assert max_memory < 1000  # Should not exceed 1GB


class BenchmarkStreamService:
    """Benchmark stream service performance."""
    
    def setup_method(self):
        """Setup benchmark fixtures."""
        self.config = StreamConfig(
            buffer_size=10,
            target_fps=30.0,
            reconnect_attempts=3
        )
        self.metrics = PerformanceMetrics()
    
    @patch('cv2.VideoCapture')
    def test_stream_read_performance(self, mock_capture):
        """Benchmark stream reading performance."""
        print("\n=== Stream Reading Benchmark ===")
        
        # Mock video capture with realistic frame timing
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        
        # Generate test frames
        test_frames = [
            np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
            for _ in range(100)
        ]
        
        frame_iter = iter(test_frames * 10)  # Cycle through frames
        mock_cap.read.side_effect = lambda: (True, next(frame_iter, test_frames[0]))
        mock_capture.return_value = mock_cap
        
        # Create stream service
        stream = VideoStreamService("rtsp://test", self.config)
        
        # Start stream and measure performance
        stream.start()
        time.sleep(2)  # Let it run for 2 seconds
        
        # Collect statistics
        stats = stream.get_statistics()
        stream.stop()
        
        print(f"Stream Reading Results:")
        print(f"  Frames read: {stats.frames_read}")
        print(f"  Frames dropped: {stats.frames_dropped}")
        print(f"  FPS: {stats.fps:.1f}")
        print(f"  Avg read time: {stats.avg_read_time_ms:.2f}ms")
        print(f"  Drop rate: {(stats.frames_dropped/stats.frames_read)*100:.1f}%")
        
        # Performance assertions
        assert stats.fps > 15  # Should achieve at least 15 FPS
        assert stats.avg_read_time_ms < 50  # Should read frames in under 50ms
        assert (stats.frames_dropped / max(stats.frames_read, 1)) < 0.1  # Drop rate under 10%
    
    def test_multi_stream_performance(self):
        """Benchmark multiple stream handling."""
        print("\n=== Multi-Stream Benchmark ===")
        
        with patch('cv2.VideoCapture') as mock_capture:
            # Mock multiple video captures
            mock_caps = []
            for i in range(4):  # Test 4 concurrent streams
                mock_cap = Mock()
                mock_cap.isOpened.return_value = True
                mock_cap.read.return_value = (
                    True, 
                    np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
                )
                mock_caps.append(mock_cap)
            
            mock_capture.side_effect = mock_caps
            
            manager = MultiStreamManager()
            
            # Add multiple streams
            stream_ids = []
            for i in range(4):
                stream_id = f"cam_{i:03d}"
                success = manager.add_stream(stream_id, f"rtsp://test{i}", self.config)
                assert success
                stream_ids.append(stream_id)
            
            # Start all streams
            start_results = manager.start_all_streams()
            assert all(start_results.values())
            
            # Let streams run
            time.sleep(3)
            
            # Collect aggregated statistics
            stats = manager.get_aggregated_stats()
            
            # Stop all streams
            manager.stop_all_streams()
            
            print(f"Multi-Stream Results:")
            print(f"  Total streams: {stats['total_streams']}")
            print(f"  Total frames read: {stats['total_frames_read']}")
            print(f"  Average FPS: {stats['average_fps']:.1f}")
            print(f"  Drop rate: {stats['drop_rate']*100:.1f}%")
            
            # Performance assertions
            assert stats['total_streams'] == 4
            assert stats['average_fps'] > 10  # Should maintain reasonable FPS across all streams
            assert stats['drop_rate'] < 0.15  # Drop rate should be under 15%


class BenchmarkPerformanceMonitor:
    """Benchmark performance monitoring system."""
    
    def test_monitoring_overhead(self):
        """Benchmark monitoring system overhead."""
        print("\n=== Monitoring Overhead Benchmark ===")
        
        monitor = PerformanceMonitor(monitoring_interval=0.1)  # Fast monitoring
        
        # Measure baseline performance without monitoring
        baseline_times = []
        for i in range(100):
            start = time.perf_counter()
            # Simulate some work
            time.sleep(0.001)
            baseline_times.append((time.perf_counter() - start) * 1000)
        
        baseline_avg = statistics.mean(baseline_times)
        
        # Start monitoring and measure performance
        monitor.start_monitoring()
        
        monitored_times = []
        for i in range(100):
            start = time.perf_counter()
            # Simulate some work
            time.sleep(0.001)
            monitored_times.append((time.perf_counter() - start) * 1000)
        
        monitor.stop_monitoring()
        monitored_avg = statistics.mean(monitored_times)
        
        overhead_percent = ((monitored_avg - baseline_avg) / baseline_avg) * 100
        
        print(f"Monitoring Overhead Results:")
        print(f"  Baseline avg time: {baseline_avg:.3f}ms")
        print(f"  Monitored avg time: {monitored_avg:.3f}ms")
        print(f"  Overhead: {overhead_percent:.1f}%")
        
        # Should have minimal overhead
        assert overhead_percent < 5  # Less than 5% overhead
    
    def test_metrics_collection_performance(self):
        """Benchmark metrics collection performance."""
        print("\n=== Metrics Collection Benchmark ===")
        
        monitor = PerformanceMonitor()
        
        # Benchmark system metrics collection
        collection_times = []
        for i in range(50):
            start = time.perf_counter()
            monitor._collect_system_metrics()
            collection_times.append((time.perf_counter() - start) * 1000)
        
        avg_collection_time = statistics.mean(collection_times)
        max_collection_time = max(collection_times)
        
        print(f"Metrics Collection Results:")
        print(f"  Avg collection time: {avg_collection_time:.2f}ms")
        print(f"  Max collection time: {max_collection_time:.2f}ms")
        
        # Metrics collection should be fast
        assert avg_collection_time < 50  # Should collect in under 50ms
        assert max_collection_time < 100  # Max should be under 100ms


class BenchmarkViolationAnalytics:
    """Benchmark violation analytics performance."""
    
    def test_violation_recording_performance(self):
        """Benchmark violation recording performance."""
        print("\n=== Violation Recording Benchmark ===")
        
        analytics = ViolationAnalytics()
        
        # Benchmark recording many violations
        start_time = time.perf_counter()
        
        for i in range(10000):
            analytics.record_violation(
                f"violation_type_{i % 5}",
                f"device_{i % 10}",
                time.time() - (i * 0.1)
            )
        
        recording_time = (time.perf_counter() - start_time) * 1000
        rate = 10000 / (recording_time / 1000)
        
        print(f"Violation Recording Results:")
        print(f"  Total violations: 10,000")
        print(f"  Recording time: {recording_time:.1f}ms")
        print(f"  Recording rate: {rate:.1f} violations/sec")
        
        # Should handle high recording rates
        assert rate > 1000  # Should record more than 1000 violations per second
    
    def test_analytics_query_performance(self):
        """Benchmark analytics query performance."""
        print("\n=== Analytics Query Benchmark ===")
        
        analytics = ViolationAnalytics()
        
        # Pre-populate with test data
        current_time = time.time()
        for i in range(5000):
            analytics.record_violation(
                f"violation_type_{i % 3}",
                f"device_{i % 20}",
                current_time - (i * 60)  # One per minute going back
            )
        
        # Benchmark trend analysis
        trend_times = []
        for _ in range(20):
            start = time.perf_counter()
            trends = analytics.get_violation_trends(24)
            trend_times.append((time.perf_counter() - start) * 1000)
        
        # Benchmark hotspot analysis
        hotspot_times = []
        for _ in range(20):
            start = time.perf_counter()
            hotspots = analytics.get_hotspot_analysis()
            hotspot_times.append((time.perf_counter() - start) * 1000)
        
        avg_trend_time = statistics.mean(trend_times)
        avg_hotspot_time = statistics.mean(hotspot_times)
        
        print(f"Analytics Query Results:")
        print(f"  Avg trend analysis time: {avg_trend_time:.2f}ms")
        print(f"  Avg hotspot analysis time: {avg_hotspot_time:.2f}ms")
        print(f"  Total violations analyzed: 5,000")
        
        # Queries should be fast
        assert avg_trend_time < 100  # Under 100ms
        assert avg_hotspot_time < 50  # Under 50ms


def run_all_benchmarks():
    """Run all performance benchmarks."""
    print("=" * 80)
    print("REAL-TIME TRAFFIC ANALYSIS - PERFORMANCE BENCHMARKS")
    print("=" * 80)
    
    # Pipeline Benchmarks
    print("\n" + "="*50)
    print("PIPELINE BENCHMARKS")
    print("="*50)
    
    pipeline_bench = BenchmarkRealTimePipeline()
    pipeline_bench.setup_method()
    pipeline_bench.test_single_frame_processing_performance()
    pipeline_bench.test_sustained_processing_performance()
    pipeline_bench.test_memory_usage_over_time()
    
    # Stream Service Benchmarks
    print("\n" + "="*50)
    print("STREAM SERVICE BENCHMARKS")
    print("="*50)
    
    stream_bench = BenchmarkStreamService()
    stream_bench.setup_method()
    stream_bench.test_stream_read_performance()
    stream_bench.test_multi_stream_performance()
    
    # Monitoring Benchmarks
    print("\n" + "="*50)
    print("MONITORING BENCHMARKS")
    print("="*50)
    
    monitor_bench = BenchmarkPerformanceMonitor()
    monitor_bench.test_monitoring_overhead()
    monitor_bench.test_metrics_collection_performance()
    
    # Analytics Benchmarks
    print("\n" + "="*50)
    print("ANALYTICS BENCHMARKS")
    print("="*50)
    
    analytics_bench = BenchmarkViolationAnalytics()
    analytics_bench.test_violation_recording_performance()
    analytics_bench.test_analytics_query_performance()
    
    print("\n" + "="*80)
    print("BENCHMARKS COMPLETED")
    print("="*80)
    print("\nPerformance Summary:")
    print("- Pipeline: <200ms processing, >5 FPS capability")
    print("- Streams: >15 FPS per stream, <10% drop rate")
    print("- Monitoring: <5% overhead, <50ms metrics collection")
    print("- Analytics: >1000 violations/sec recording, <100ms queries")


if __name__ == "__main__":
    run_all_benchmarks()