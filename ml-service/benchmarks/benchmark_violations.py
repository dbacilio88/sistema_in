"""
Benchmark suite for traffic violations detection module.

Performance benchmarks for violation detection, lane detection, and notification systems.
"""

import time
import numpy as np
import cv2
import pytest
from typing import List, Dict, Any, Tuple
import statistics
from contextlib import contextmanager
import psutil
import os

from ..violation_detector import (
    ViolationDetector, TrafficViolation, ViolationType, ViolationSeverity, ViolationLocation
)
from ..lane_detector import LaneDetector
from ..notification_system import NotificationSystem, NotificationChannel
from ..violation_manager import ViolationManager
from ...speed.speed_analyzer import SpeedViolation
from ...tracking.vehicle_tracker import TrackedVehicle


class PerformanceMetrics:
    """Performance metrics container."""
    
    def __init__(self):
        self.processing_times: List[float] = []
        self.memory_usage: List[float] = []
        self.cpu_usage: List[float] = []
        self.detection_rates: List[float] = []
        self.accuracy_scores: List[float] = []
        
    def add_measurement(self, processing_time: float, memory_mb: float = None, 
                       cpu_percent: float = None, detection_rate: float = None,
                       accuracy: float = None):
        """Add performance measurement."""
        self.processing_times.append(processing_time)
        if memory_mb is not None:
            self.memory_usage.append(memory_mb)
        if cpu_percent is not None:
            self.cpu_usage.append(cpu_percent)
        if detection_rate is not None:
            self.detection_rates.append(detection_rate)
        if accuracy is not None:
            self.accuracy_scores.append(accuracy)
    
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
                'fps': 1.0 / statistics.mean(self.processing_times) if statistics.mean(self.processing_times) > 0 else 0
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
        
        if self.detection_rates:
            stats['detection'] = {
                'mean_rate': statistics.mean(self.detection_rates),
                'total_detections': sum(self.detection_rates)
            }
        
        if self.accuracy_scores:
            stats['accuracy'] = {
                'mean_accuracy': statistics.mean(self.accuracy_scores),
                'min_accuracy': min(self.accuracy_scores),
                'max_accuracy': max(self.accuracy_scores)
            }
        
        return stats


@contextmanager
def measure_performance():
    """Context manager for measuring performance."""
    process = psutil.Process(os.getpid())
    
    # Initial measurements
    start_time = time.perf_counter()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    start_cpu = process.cpu_percent()
    
    try:
        yield
    finally:
        # Final measurements
        end_time = time.perf_counter()
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        end_cpu = process.cpu_percent()
        
        elapsed_time = end_time - start_time
        memory_usage = max(end_memory, start_memory)
        cpu_usage = max(end_cpu, start_cpu)
        
        # Store in global metrics (would need proper implementation)
        print(f"Performance: {elapsed_time:.4f}s, {memory_usage:.1f}MB, {cpu_usage:.1f}% CPU")


class BenchmarkViolationDetector:
    """Benchmark violation detection performance."""
    
    def setup_method(self):
        """Setup benchmark fixtures."""
        self.detector = ViolationDetector()
        self.metrics = PerformanceMetrics()
        
        # Create test data
        self.test_frames = []
        self.test_vehicles = []
        self.test_speed_violations = []
        
        self._generate_test_data()
    
    def _generate_test_data(self):
        """Generate test data for benchmarks."""
        # Generate test frames
        for i in range(100):
            frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
            self.test_frames.append(frame)
        
        # Generate test vehicles
        for i in range(50):
            vehicle = TrackedVehicle(
                track_id=i,
                bbox=(100 + i*10, 100 + i*5, 200 + i*10, 200 + i*5),
                confidence=0.8 + 0.1 * np.random.random(),
                class_name="car"
            )
            vehicle.trajectory = [(150 + i*10 + j*5, 150 + i*5 + j*10) for j in range(10)]
            self.test_vehicles.append(vehicle)
        
        # Generate test speed violations
        for i in range(20):
            speed_violation = SpeedViolation(
                vehicle_id=i,
                timestamp=time.time() - i*60,
                measured_speed=60 + i*5,
                speed_limit=50,
                violation_amount=10 + i*5,
                measurement_zone=f"zone_{i % 3}",
                confidence=0.8 + 0.1 * np.random.random()
            )
            self.test_speed_violations.append(speed_violation)
    
    def test_speed_violation_detection_performance(self):
        """Benchmark speed violation detection."""
        print("\n=== Speed Violation Detection Benchmark ===")
        
        for i in range(50):
            frame = self.test_frames[i % len(self.test_frames)]
            vehicles = self.test_vehicles[:10]  # 10 vehicles per frame
            speed_violations = self.test_speed_violations[:5]  # 5 violations per frame
            
            start_time = time.perf_counter()
            
            violations = self.detector.detect_speed_violations(
                speed_violations, vehicles, frame
            )
            
            end_time = time.perf_counter()
            processing_time = end_time - start_time
            
            self.metrics.add_measurement(
                processing_time=processing_time,
                detection_rate=len(violations)
            )
        
        stats = self.metrics.get_statistics()
        print(f"Speed Detection - Mean time: {stats['processing_time']['mean']:.4f}s")
        print(f"Speed Detection - FPS: {stats['processing_time']['fps']:.1f}")
        print(f"Speed Detection - Total detections: {stats['detection']['total_detections']}")
        
        # Performance assertions
        assert stats['processing_time']['mean'] < 0.1  # Should be under 100ms
        assert stats['processing_time']['fps'] > 10    # Should handle 10+ FPS
    
    def test_lane_violation_detection_performance(self):
        """Benchmark lane violation detection."""
        print("\n=== Lane Violation Detection Benchmark ===")
        
        # Create lane mask
        lane_mask = np.zeros((1080, 1920), dtype=np.uint8)
        lane_mask[200:800, 400:1500] = 255  # Valid lane area
        
        metrics = PerformanceMetrics()
        
        for i in range(50):
            frame = self.test_frames[i % len(self.test_frames)]
            vehicles = self.test_vehicles[:10]
            
            start_time = time.perf_counter()
            
            violations = self.detector.detect_lane_violations(vehicles, lane_mask, frame)
            
            end_time = time.perf_counter()
            processing_time = end_time - start_time
            
            metrics.add_measurement(
                processing_time=processing_time,
                detection_rate=len(violations)
            )
        
        stats = metrics.get_statistics()
        print(f"Lane Detection - Mean time: {stats['processing_time']['mean']:.4f}s")
        print(f"Lane Detection - FPS: {stats['processing_time']['fps']:.1f}")
        
        assert stats['processing_time']['mean'] < 0.05  # Should be under 50ms
    
    def test_wrong_way_detection_performance(self):
        """Benchmark wrong-way detection."""
        print("\n=== Wrong-Way Detection Benchmark ===")
        
        expected_direction = np.array([0, 1])  # Downward movement expected
        metrics = PerformanceMetrics()
        
        for i in range(50):
            frame = self.test_frames[i % len(self.test_frames)]
            vehicles = self.test_vehicles[:5]  # Fewer vehicles for trajectory analysis
            
            start_time = time.perf_counter()
            
            violations = self.detector.detect_wrong_way_driving(
                vehicles, expected_direction, frame
            )
            
            end_time = time.perf_counter()
            processing_time = end_time - start_time
            
            metrics.add_measurement(
                processing_time=processing_time,
                detection_rate=len(violations)
            )
        
        stats = metrics.get_statistics()
        print(f"Wrong-Way Detection - Mean time: {stats['processing_time']['mean']:.4f}s")
        print(f"Wrong-Way Detection - FPS: {stats['processing_time']['fps']:.1f}")
        
        assert stats['processing_time']['mean'] < 0.02  # Should be under 20ms
    
    def test_full_detection_pipeline_performance(self):
        """Benchmark full violation detection pipeline."""
        print("\n=== Full Detection Pipeline Benchmark ===")
        
        lane_mask = np.zeros((1080, 1920), dtype=np.uint8)
        lane_mask[200:800, 400:1500] = 255
        expected_direction = np.array([0, 1])
        
        metrics = PerformanceMetrics()
        
        for i in range(30):
            frame = self.test_frames[i % len(self.test_frames)]
            vehicles = self.test_vehicles[:15]
            speed_violations = self.test_speed_violations[:3]
            
            start_time = time.perf_counter()
            
            # Run all detection types
            speed_viols = self.detector.detect_speed_violations(
                speed_violations, vehicles, frame
            )
            lane_viols = self.detector.detect_lane_violations(
                vehicles, lane_mask, frame
            )
            wrong_way_viols = self.detector.detect_wrong_way_driving(
                vehicles, expected_direction, frame
            )
            following_viols = self.detector.detect_following_distance_violations(
                vehicles, frame
            )
            
            end_time = time.perf_counter()
            processing_time = end_time - start_time
            
            total_violations = len(speed_viols) + len(lane_viols) + len(wrong_way_viols) + len(following_viols)
            
            metrics.add_measurement(
                processing_time=processing_time,
                detection_rate=total_violations
            )
        
        stats = metrics.get_statistics()
        print(f"Full Pipeline - Mean time: {stats['processing_time']['mean']:.4f}s")
        print(f"Full Pipeline - FPS: {stats['processing_time']['fps']:.1f}")
        print(f"Full Pipeline - Total detections: {stats['detection']['total_detections']}")
        
        assert stats['processing_time']['mean'] < 0.2  # Should be under 200ms
        assert stats['processing_time']['fps'] > 5     # Should handle 5+ FPS


class BenchmarkLaneDetector:
    """Benchmark lane detection performance."""
    
    def setup_method(self):
        """Setup benchmark fixtures."""
        self.detector = LaneDetector(1920, 1080)
        self.metrics = PerformanceMetrics()
        
        # Generate test images
        self.test_images = self._generate_test_images()
    
    def _generate_test_images(self) -> List[np.ndarray]:
        """Generate test images with lane markings."""
        images = []
        
        for i in range(50):
            # Create base image
            image = np.random.randint(50, 150, (1080, 1920, 3), dtype=np.uint8)
            
            # Add lane markings
            # Left lane
            cv2.line(image, (600 + i*2, 1080), (800 + i, 400), (255, 255, 255), 8)
            # Right lane
            cv2.line(image, (1200 - i*2, 1080), (1000 - i, 400), (255, 255, 255), 8)
            
            # Add some noise
            noise = np.random.randint(0, 50, image.shape, dtype=np.uint8)
            image = cv2.add(image, noise)
            
            images.append(image)
        
        return images
    
    def test_lane_detection_performance(self):
        """Benchmark lane detection."""
        print("\n=== Lane Detection Benchmark ===")
        
        for i, image in enumerate(self.test_images):
            start_time = time.perf_counter()
            
            lane_geometry = self.detector.detect_lanes(image)
            
            end_time = time.perf_counter()
            processing_time = end_time - start_time
            
            # Simple success metric
            detection_success = 1.0 if lane_geometry.left_lane or lane_geometry.right_lane else 0.0
            
            self.metrics.add_measurement(
                processing_time=processing_time,
                accuracy=detection_success
            )
        
        stats = self.metrics.get_statistics()
        print(f"Lane Detection - Mean time: {stats['processing_time']['mean']:.4f}s")
        print(f"Lane Detection - FPS: {stats['processing_time']['fps']:.1f}")
        print(f"Lane Detection - Success rate: {stats['accuracy']['mean_accuracy']:.2f}")
        
        assert stats['processing_time']['mean'] < 0.3   # Should be under 300ms
        assert stats['processing_time']['fps'] > 3      # Should handle 3+ FPS
        assert stats['accuracy']['mean_accuracy'] > 0.5 # Should detect lanes in >50% of cases
    
    def test_lane_mask_creation_performance(self):
        """Benchmark lane mask creation."""
        print("\n=== Lane Mask Creation Benchmark ===")
        
        # Create mock lane geometry
        from ..lane_detector import LaneMarking, LaneGeometry, LaneType
        
        left_lane = LaneMarking(
            points=[(600, 1000), (700, 800), (800, 600), (900, 400)],
            lane_type=LaneType.SOLID,
            confidence=0.9,
            side="left"
        )
        right_lane = LaneMarking(
            points=[(1200, 1000), (1100, 800), (1000, 600), (900, 400)],
            lane_type=LaneType.SOLID,
            confidence=0.9,
            side="right"
        )
        
        lane_geometry = LaneGeometry(
            left_lane=left_lane,
            right_lane=right_lane,
            center_line=None,
            lane_width=None,
            curve_radius=None
        )
        
        metrics = PerformanceMetrics()
        
        for i in range(100):
            start_time = time.perf_counter()
            
            mask = self.detector.create_lane_mask(lane_geometry, (1080, 1920))
            
            end_time = time.perf_counter()
            processing_time = end_time - start_time
            
            metrics.add_measurement(processing_time=processing_time)
        
        stats = metrics.get_statistics()
        print(f"Lane Mask - Mean time: {stats['processing_time']['mean']:.4f}s")
        print(f"Lane Mask - FPS: {stats['processing_time']['fps']:.1f}")
        
        assert stats['processing_time']['mean'] < 0.01  # Should be under 10ms


class BenchmarkNotificationSystem:
    """Benchmark notification system performance."""
    
    def setup_method(self):
        """Setup benchmark fixtures."""
        self.notification_system = NotificationSystem()
        self.metrics = PerformanceMetrics()
        
        # Generate test violations
        self.test_violations = self._generate_test_violations()
    
    def _generate_test_violations(self) -> List[TrafficViolation]:
        """Generate test violations."""
        violations = []
        
        for i in range(100):
            violation = TrafficViolation(
                violation_id=f"bench_violation_{i}",
                timestamp=time.time() - i*60,
                violation_type=ViolationType.SPEED_VIOLATION,
                severity=ViolationSeverity.MODERATE,
                vehicle_id=i % 20,
                description=f"Benchmark violation {i}",
                confidence=0.8 + 0.1 * np.random.random(),
                location=ViolationLocation(f"zone_{i % 5}", f"Zone {i % 5}", (100 + i, 100 + i))
            )
            violations.append(violation)
        
        return violations
    
    def test_violation_alert_performance(self):
        """Benchmark violation alert processing."""
        print("\n=== Violation Alert Performance Benchmark ===")
        
        for violation in self.test_violations[:50]:  # Test 50 violations
            start_time = time.perf_counter()
            
            alert_id = self.notification_system.send_violation_alert(violation)
            
            end_time = time.perf_counter()
            processing_time = end_time - start_time
            
            success = 1.0 if alert_id else 0.0
            
            self.metrics.add_measurement(
                processing_time=processing_time,
                accuracy=success
            )
        
        stats = self.metrics.get_statistics()
        print(f"Alert Processing - Mean time: {stats['processing_time']['mean']:.4f}s")
        print(f"Alert Processing - Rate: {1/stats['processing_time']['mean']:.1f} alerts/sec")
        print(f"Alert Processing - Success rate: {stats['accuracy']['mean_accuracy']:.2f}")
        
        assert stats['processing_time']['mean'] < 0.1   # Should be under 100ms
        assert stats['accuracy']['mean_accuracy'] > 0.9 # Should succeed >90% of time
    
    def test_notification_throughput(self):
        """Benchmark notification throughput."""
        print("\n=== Notification Throughput Benchmark ===")
        
        # Test batch processing
        batch_sizes = [1, 5, 10, 20, 50]
        
        for batch_size in batch_sizes:
            violations_batch = self.test_violations[:batch_size]
            
            start_time = time.perf_counter()
            
            alert_ids = []
            for violation in violations_batch:
                alert_id = self.notification_system.send_violation_alert(violation)
                alert_ids.append(alert_id)
            
            end_time = time.perf_counter()
            processing_time = end_time - start_time
            
            throughput = batch_size / processing_time
            success_rate = sum(1 for aid in alert_ids if aid) / len(alert_ids)
            
            print(f"Batch size {batch_size:2d}: {throughput:6.1f} alerts/sec, "
                  f"{success_rate:.2f} success rate")
        
        # Basic throughput assertion
        assert throughput > 50  # Should handle >50 alerts per second


class BenchmarkViolationManager:
    """Benchmark violation manager performance."""
    
    def setup_method(self):
        """Setup benchmark fixtures."""
        import tempfile
        
        # Use temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.manager = ViolationManager()
        self.manager.db_path = self.temp_db.name
        self.manager._init_database()
        
        self.metrics = PerformanceMetrics()
    
    def teardown_method(self):
        """Cleanup benchmark fixtures."""
        import os
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    def test_violation_storage_performance(self):
        """Benchmark violation storage."""
        print("\n=== Violation Storage Benchmark ===")
        
        violations = []
        for i in range(1000):
            violation = TrafficViolation(
                violation_id=f"bench_violation_{i}",
                timestamp=time.time() - i*60,
                violation_type=ViolationType.SPEED_VIOLATION,
                severity=ViolationSeverity.MODERATE,
                vehicle_id=i % 100,
                description=f"Benchmark violation {i}",
                confidence=0.8,
                location=ViolationLocation(f"zone_{i % 10}", f"Zone {i % 10}", (100, 100))
            )
            violations.append(violation)
        
        start_time = time.perf_counter()
        
        for violation in violations:
            self.manager._store_violation(violation)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        storage_rate = len(violations) / total_time
        
        print(f"Storage rate: {storage_rate:.1f} violations/sec")
        print(f"Total time for {len(violations)} violations: {total_time:.2f}s")
        
        assert storage_rate > 100  # Should handle >100 violations per second
    
    def test_statistics_generation_performance(self):
        """Benchmark statistics generation."""
        print("\n=== Statistics Generation Benchmark ===")
        
        # Add test data
        for i in range(500):
            violation = TrafficViolation(
                violation_id=f"stats_violation_{i}",
                timestamp=time.time() - i*60,
                violation_type=list(ViolationType)[i % len(ViolationType)],
                severity=list(ViolationSeverity)[i % len(ViolationSeverity)],
                vehicle_id=i % 50,
                description=f"Stats violation {i}",
                confidence=0.8,
                location=ViolationLocation(f"zone_{i % 10}", f"Zone {i % 10}", (100, 100))
            )
            self.manager._store_violation(violation)
        
        # Benchmark statistics generation
        start_time = time.perf_counter()
        
        stats = self.manager.get_current_statistics()
        
        end_time = time.perf_counter()
        processing_time = end_time - start_time
        
        print(f"Statistics generation time: {processing_time:.4f}s")
        print(f"Total violations in stats: {stats.current_violations}")
        
        assert processing_time < 1.0  # Should be under 1 second
    
    def test_report_generation_performance(self):
        """Benchmark report generation."""
        print("\n=== Report Generation Benchmark ===")
        
        # Add test data
        current_time = time.time()
        for i in range(200):
            violation = TrafficViolation(
                violation_id=f"report_violation_{i}",
                timestamp=current_time - i*3600,  # Spread over hours
                violation_type=list(ViolationType)[i % len(ViolationType)],
                severity=list(ViolationSeverity)[i % len(ViolationSeverity)],
                vehicle_id=i % 30,
                description=f"Report violation {i}",
                confidence=0.8,
                location=ViolationLocation(f"zone_{i % 5}", f"Zone {i % 5}", (100, 100))
            )
            self.manager._store_violation(violation)
        
        # Benchmark report generation
        start_time = current_time - 24*3600  # Last 24 hours
        end_time = current_time
        
        start_perf = time.perf_counter()
        
        report = self.manager.generate_report(start_time, end_time)
        
        end_perf = time.perf_counter()
        processing_time = end_perf - start_perf
        
        print(f"Report generation time: {processing_time:.4f}s")
        print(f"Report covers {report.total_violations} violations")
        
        assert processing_time < 2.0  # Should be under 2 seconds


def run_all_benchmarks():
    """Run all performance benchmarks."""
    print("=" * 60)
    print("TRAFFIC VIOLATIONS DETECTION - PERFORMANCE BENCHMARKS")
    print("=" * 60)
    
    # Violation Detector Benchmarks
    print("\n" + "="*40)
    print("VIOLATION DETECTOR BENCHMARKS")
    print("="*40)
    
    detector_bench = BenchmarkViolationDetector()
    detector_bench.setup_method()
    detector_bench.test_speed_violation_detection_performance()
    detector_bench.test_lane_violation_detection_performance()
    detector_bench.test_wrong_way_detection_performance()
    detector_bench.test_full_detection_pipeline_performance()
    
    # Lane Detector Benchmarks
    print("\n" + "="*40)
    print("LANE DETECTOR BENCHMARKS")
    print("="*40)
    
    lane_bench = BenchmarkLaneDetector()
    lane_bench.setup_method()
    lane_bench.test_lane_detection_performance()
    lane_bench.test_lane_mask_creation_performance()
    
    # Notification System Benchmarks
    print("\n" + "="*40)
    print("NOTIFICATION SYSTEM BENCHMARKS")
    print("="*40)
    
    notification_bench = BenchmarkNotificationSystem()
    notification_bench.setup_method()
    notification_bench.test_violation_alert_performance()
    notification_bench.test_notification_throughput()
    
    # Violation Manager Benchmarks
    print("\n" + "="*40)
    print("VIOLATION MANAGER BENCHMARKS")
    print("="*40)
    
    manager_bench = BenchmarkViolationManager()
    manager_bench.setup_method()
    manager_bench.test_violation_storage_performance()
    manager_bench.test_statistics_generation_performance()
    manager_bench.test_report_generation_performance()
    manager_bench.teardown_method()
    
    print("\n" + "="*60)
    print("BENCHMARKS COMPLETED")
    print("="*60)


if __name__ == "__main__":
    run_all_benchmarks()