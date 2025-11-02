#!/usr/bin/env python3
"""
Comprehensive benchmark for tracking system.

This script tests tracking performance, accuracy, and memory usage
with various scenarios and real-world conditions.
"""

import argparse
import logging
import time
import numpy as np
import cv2
from pathlib import Path
import json
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Tuple
import statistics
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from detection.vehicle_detector import YOLOv8VehicleDetector
from tracking.vehicle_tracker import VehicleTracker, Detection
from tracking.trajectory import TrajectoryManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TrackingBenchmark:
    """
    Comprehensive tracking benchmark suite.
    
    Tests tracking performance, accuracy, and robustness under various conditions.
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize benchmark.
        
        Args:
            model_path: Path to YOLOv8 model (optional for pure tracking tests)
        """
        self.model_path = model_path
        self.detector = None
        self.tracker = None
        self.results = {}
        
        if model_path and Path(model_path).exists():
            logger.info(f"Loading YOLOv8 detector from {model_path}")
            self.detector = YOLOv8VehicleDetector(model_path)
        
        logger.info("Initializing VehicleTracker")
        self.tracker = VehicleTracker()
    
    def generate_synthetic_detections(self, frame_count: int, vehicle_count: int) -> List[List[Detection]]:
        """
        Generate synthetic vehicle detections for testing.
        
        Args:
            frame_count: Number of frames to generate
            vehicle_count: Number of vehicles to simulate
            
        Returns:
            List of detection lists (one per frame)
        """
        logger.info(f"Generating {frame_count} frames with {vehicle_count} vehicles")
        
        detections_per_frame = []
        
        # Initialize vehicle positions and velocities
        vehicles = []
        for i in range(vehicle_count):
            vehicles.append({
                'id': i,
                'x': np.random.randint(50, 550),  # Start position X
                'y': np.random.randint(50, 350),  # Start position Y
                'vx': np.random.uniform(-2, 2),   # Velocity X
                'vy': np.random.uniform(-2, 2),   # Velocity Y
                'width': np.random.randint(80, 120),
                'height': np.random.randint(40, 80),
                'class_name': np.random.choice(['car', 'truck', 'bus'])
            })
        
        for frame_idx in range(frame_count):
            frame_detections = []
            
            for vehicle in vehicles:
                # Update position
                vehicle['x'] += vehicle['vx']
                vehicle['y'] += vehicle['vy']
                
                # Bounce off boundaries
                if vehicle['x'] < 0 or vehicle['x'] > 640:
                    vehicle['vx'] *= -1
                if vehicle['y'] < 0 or vehicle['y'] > 480:
                    vehicle['vy'] *= -1
                
                # Keep in bounds
                vehicle['x'] = max(0, min(640 - vehicle['width'], vehicle['x']))
                vehicle['y'] = max(0, min(480 - vehicle['height'], vehicle['y']))
                
                # Add some noise to simulate detection uncertainty
                noise_x = np.random.normal(0, 2)
                noise_y = np.random.normal(0, 2)
                
                x1 = int(vehicle['x'] + noise_x)
                y1 = int(vehicle['y'] + noise_y)
                x2 = x1 + vehicle['width']
                y2 = y1 + vehicle['height']
                
                # Simulate occasional missed detections
                if np.random.random() > 0.1:  # 90% detection rate
                    detection = Detection(
                        bbox=(x1, y1, x2, y2),
                        confidence=np.random.uniform(0.7, 0.95),
                        class_id=2,  # Vehicle class
                        class_name=vehicle['class_name']
                    )
                    frame_detections.append(detection)
            
            detections_per_frame.append(frame_detections)
        
        return detections_per_frame
    
    def benchmark_tracking_performance(self, frame_count: int = 100, vehicle_count: int = 5) -> Dict[str, Any]:
        """
        Benchmark tracking performance with synthetic data.
        
        Args:
            frame_count: Number of frames to process
            vehicle_count: Number of vehicles to track
            
        Returns:
            Performance metrics dictionary
        """
        logger.info(f"Running tracking performance benchmark: {frame_count} frames, {vehicle_count} vehicles")
        
        # Generate synthetic data
        detections_sequence = self.generate_synthetic_detections(frame_count, vehicle_count)
        frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(frame_count)]
        
        # Reset tracker
        self.tracker.reset()
        
        # Track performance metrics
        processing_times = []
        memory_usage = []
        track_counts = []
        
        start_time = time.time()
        
        for frame_idx, (detections, frame) in enumerate(zip(detections_sequence, frames)):
            frame_start = time.time()
            
            # Run tracking
            tracked_vehicles = self.tracker.update(detections, frame)
            
            frame_time = time.time() - frame_start
            processing_times.append(frame_time)
            track_counts.append(len(tracked_vehicles))
            
            # Log progress
            if frame_idx % 20 == 0:
                logger.info(f"Processed frame {frame_idx}/{frame_count}")
        
        total_time = time.time() - start_time
        
        # Calculate metrics
        avg_processing_time = statistics.mean(processing_times)
        max_processing_time = max(processing_times)
        min_processing_time = min(processing_times)
        fps = 1.0 / avg_processing_time
        
        # Get tracker statistics
        tracker_stats = self.tracker.get_tracking_stats()
        
        results = {
            "test_name": "tracking_performance",
            "frame_count": frame_count,
            "vehicle_count": vehicle_count,
            "total_time_seconds": total_time,
            "avg_processing_time_ms": avg_processing_time * 1000,
            "max_processing_time_ms": max_processing_time * 1000,
            "min_processing_time_ms": min_processing_time * 1000,
            "fps": fps,
            "avg_tracks_per_frame": statistics.mean(track_counts),
            "max_tracks": max(track_counts),
            "tracker_stats": tracker_stats,
            "processing_times_ms": [t * 1000 for t in processing_times]
        }
        
        logger.info(f"Tracking Performance Results:")
        logger.info(f"  Average FPS: {fps:.2f}")
        logger.info(f"  Average processing time: {avg_processing_time*1000:.2f}ms")
        logger.info(f"  Average tracks per frame: {statistics.mean(track_counts):.1f}")
        
        return results
    
    def benchmark_tracking_accuracy(self, frame_count: int = 200, vehicle_count: int = 3) -> Dict[str, Any]:
        """
        Benchmark tracking accuracy and ID consistency.
        
        Args:
            frame_count: Number of frames to process
            vehicle_count: Number of vehicles to track
            
        Returns:
            Accuracy metrics dictionary
        """
        logger.info(f"Running tracking accuracy benchmark: {frame_count} frames, {vehicle_count} vehicles")
        
        # Generate deterministic synthetic data for accuracy testing
        np.random.seed(42)  # For reproducible results
        detections_sequence = self.generate_synthetic_detections(frame_count, vehicle_count)
        frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(frame_count)]
        
        # Reset tracker
        self.tracker.reset()
        
        # Track ID consistency
        track_histories = {}  # ground_truth_id -> [assigned_track_ids]
        id_switches = 0
        total_tracks_created = 0
        frames_with_tracks = 0
        
        for frame_idx, (detections, frame) in enumerate(zip(detections_sequence, frames)):
            tracked_vehicles = self.tracker.update(detections, frame)
            
            if tracked_vehicles:
                frames_with_tracks += 1
            
            # Simple ID consistency check (based on position proximity)
            for vehicle in tracked_vehicles:
                # Find closest detection (ground truth)
                min_distance = float('inf')
                closest_detection_idx = -1
                
                vehicle_center = vehicle.center
                for det_idx, detection in enumerate(detections):
                    det_center = (
                        (detection.bbox[0] + detection.bbox[2]) // 2,
                        (detection.bbox[1] + detection.bbox[3]) // 2
                    )
                    distance = np.sqrt(
                        (vehicle_center[0] - det_center[0])**2 + 
                        (vehicle_center[1] - det_center[1])**2
                    )
                    if distance < min_distance:
                        min_distance = distance
                        closest_detection_idx = det_idx
                
                # Track ID history for this ground truth vehicle
                if closest_detection_idx != -1 and min_distance < 50:  # Reasonable matching threshold
                    if closest_detection_idx not in track_histories:
                        track_histories[closest_detection_idx] = []
                    
                    prev_track_ids = track_histories[closest_detection_idx]
                    if prev_track_ids and prev_track_ids[-1] != vehicle.track_id:
                        id_switches += 1
                        logger.debug(f"ID switch detected for vehicle {closest_detection_idx}: {prev_track_ids[-1]} -> {vehicle.track_id}")
                    
                    track_histories[closest_detection_idx].append(vehicle.track_id)
        
        # Calculate accuracy metrics
        total_tracks_created = len(set(track_id for history in track_histories.values() for track_id in history))
        id_consistency_rate = 1.0 - (id_switches / max(total_tracks_created, 1))
        
        # Trajectory quality metrics
        trajectory_stats = self.tracker.trajectory_manager.get_trajectory_statistics()
        
        results = {
            "test_name": "tracking_accuracy",
            "frame_count": frame_count,
            "vehicle_count": vehicle_count,
            "id_switches": id_switches,
            "total_tracks_created": total_tracks_created,
            "id_consistency_rate": id_consistency_rate,
            "frames_with_tracks": frames_with_tracks,
            "tracking_coverage": frames_with_tracks / frame_count,
            "trajectory_stats": trajectory_stats
        }
        
        logger.info(f"Tracking Accuracy Results:")
        logger.info(f"  ID consistency rate: {id_consistency_rate:.3f}")
        logger.info(f"  Total ID switches: {id_switches}")
        logger.info(f"  Tracking coverage: {frames_with_tracks/frame_count:.3f}")
        
        return results
    
    def benchmark_memory_usage(self, duration_minutes: int = 2) -> Dict[str, Any]:
        """
        Benchmark memory usage over extended operation.
        
        Args:
            duration_minutes: How long to run the test
            
        Returns:
            Memory usage metrics
        """
        logger.info(f"Running memory usage benchmark for {duration_minutes} minutes")
        
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Reset tracker
        self.tracker.reset()
        
        memory_samples = []
        trajectory_counts = []
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        frame_count = 0
        while time.time() < end_time:
            # Generate frame data
            detections = self.generate_synthetic_detections(1, 5)[0]
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            # Process frame
            self.tracker.update(detections, frame)
            
            # Sample memory every 100 frames
            if frame_count % 100 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_samples.append(current_memory)
                
                trajectory_count = len(self.tracker.trajectory_manager.trajectories)
                trajectory_counts.append(trajectory_count)
                
                logger.debug(f"Frame {frame_count}: Memory {current_memory:.1f}MB, Trajectories {trajectory_count}")
            
            frame_count += 1
            
            # Small delay to avoid overwhelming the system
            if frame_count % 1000 == 0:
                time.sleep(0.1)
                gc.collect()  # Force garbage collection
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        max_memory = max(memory_samples) if memory_samples else final_memory
        avg_memory = statistics.mean(memory_samples) if memory_samples else final_memory
        
        results = {
            "test_name": "memory_usage",
            "duration_minutes": duration_minutes,
            "frames_processed": frame_count,
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "max_memory_mb": max_memory,
            "avg_memory_mb": avg_memory,
            "memory_growth_mb": final_memory - initial_memory,
            "avg_trajectories": statistics.mean(trajectory_counts) if trajectory_counts else 0,
            "max_trajectories": max(trajectory_counts) if trajectory_counts else 0,
            "memory_samples": memory_samples,
            "trajectory_samples": trajectory_counts
        }
        
        logger.info(f"Memory Usage Results:")
        logger.info(f"  Initial memory: {initial_memory:.1f}MB")
        logger.info(f"  Final memory: {final_memory:.1f}MB")
        logger.info(f"  Memory growth: {final_memory - initial_memory:.1f}MB")
        logger.info(f"  Max memory: {max_memory:.1f}MB")
        
        return results
    
    def benchmark_stress_test(self, max_vehicles: int = 20, duration_seconds: int = 60) -> Dict[str, Any]:
        """
        Stress test with high vehicle count and fast updates.
        
        Args:
            max_vehicles: Maximum number of vehicles to simulate
            duration_seconds: Duration of stress test
            
        Returns:
            Stress test metrics
        """
        logger.info(f"Running stress test: up to {max_vehicles} vehicles for {duration_seconds}s")
        
        # Reset tracker
        self.tracker.reset()
        
        processing_times = []
        vehicle_counts = []
        dropped_frames = 0
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        frame_count = 0
        
        while time.time() < end_time:
            # Gradually increase vehicle count
            current_vehicle_count = min(max_vehicles, 1 + (frame_count // 100))
            
            # Generate detections
            detections = self.generate_synthetic_detections(1, current_vehicle_count)[0]
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            # Process with timing
            frame_start = time.time()
            tracked_vehicles = self.tracker.update(detections, frame)
            processing_time = time.time() - frame_start
            
            processing_times.append(processing_time)
            vehicle_counts.append(len(tracked_vehicles))
            
            # Check for dropped frames (>33ms = <30 FPS)
            if processing_time > 0.033:
                dropped_frames += 1
            
            frame_count += 1
        
        # Calculate metrics
        avg_processing_time = statistics.mean(processing_times)
        max_processing_time = max(processing_times)
        percentile_95 = np.percentile(processing_times, 95)
        
        results = {
            "test_name": "stress_test",
            "max_vehicles": max_vehicles,
            "duration_seconds": duration_seconds,
            "frames_processed": frame_count,
            "avg_processing_time_ms": avg_processing_time * 1000,
            "max_processing_time_ms": max_processing_time * 1000,
            "p95_processing_time_ms": percentile_95 * 1000,
            "dropped_frames": dropped_frames,
            "drop_rate": dropped_frames / frame_count,
            "avg_vehicles_tracked": statistics.mean(vehicle_counts),
            "max_vehicles_tracked": max(vehicle_counts),
            "fps": frame_count / duration_seconds
        }
        
        logger.info(f"Stress Test Results:")
        logger.info(f"  Average processing time: {avg_processing_time*1000:.2f}ms")
        logger.info(f"  95th percentile: {percentile_95*1000:.2f}ms")
        logger.info(f"  Dropped frames: {dropped_frames}/{frame_count} ({dropped_frames/frame_count:.2%})")
        logger.info(f"  Average FPS: {frame_count/duration_seconds:.1f}")
        
        return results
    
    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all benchmark tests."""
        logger.info("Starting comprehensive tracking benchmarks")
        
        all_results = {
            "timestamp": time.time(),
            "benchmarks": {}
        }
        
        # Performance benchmark
        try:
            perf_results = self.benchmark_tracking_performance()
            all_results["benchmarks"]["performance"] = perf_results
        except Exception as e:
            logger.error(f"Performance benchmark failed: {e}")
            all_results["benchmarks"]["performance"] = {"error": str(e)}
        
        # Accuracy benchmark
        try:
            acc_results = self.benchmark_tracking_accuracy()
            all_results["benchmarks"]["accuracy"] = acc_results
        except Exception as e:
            logger.error(f"Accuracy benchmark failed: {e}")
            all_results["benchmarks"]["accuracy"] = {"error": str(e)}
        
        # Memory benchmark (shorter for CI)
        try:
            mem_results = self.benchmark_memory_usage(duration_minutes=1)
            all_results["benchmarks"]["memory"] = mem_results
        except Exception as e:
            logger.error(f"Memory benchmark failed: {e}")
            all_results["benchmarks"]["memory"] = {"error": str(e)}
        
        # Stress test
        try:
            stress_results = self.benchmark_stress_test(duration_seconds=30)
            all_results["benchmarks"]["stress"] = stress_results
        except Exception as e:
            logger.error(f"Stress test failed: {e}")
            all_results["benchmarks"]["stress"] = {"error": str(e)}
        
        return all_results
    
    def save_results(self, results: Dict[str, Any], output_file: str):
        """Save benchmark results to JSON file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to {output_path}")
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable report from results."""
        report = ["# Tracking Benchmark Report", ""]
        report.append(f"**Timestamp**: {time.ctime(results['timestamp'])}")
        report.append("")
        
        for benchmark_name, benchmark_results in results["benchmarks"].items():
            if "error" in benchmark_results:
                report.append(f"## {benchmark_name.title()} Benchmark")
                report.append(f"**ERROR**: {benchmark_results['error']}")
                report.append("")
                continue
            
            report.append(f"## {benchmark_name.title()} Benchmark")
            
            if benchmark_name == "performance":
                report.append(f"- **Average FPS**: {benchmark_results['fps']:.2f}")
                report.append(f"- **Processing Time**: {benchmark_results['avg_processing_time_ms']:.2f}ms avg")
                report.append(f"- **Tracks per Frame**: {benchmark_results['avg_tracks_per_frame']:.1f}")
                
            elif benchmark_name == "accuracy":
                report.append(f"- **ID Consistency**: {benchmark_results['id_consistency_rate']:.3f}")
                report.append(f"- **ID Switches**: {benchmark_results['id_switches']}")
                report.append(f"- **Tracking Coverage**: {benchmark_results['tracking_coverage']:.3f}")
                
            elif benchmark_name == "memory":
                report.append(f"- **Memory Growth**: {benchmark_results['memory_growth_mb']:.1f}MB")
                report.append(f"- **Max Memory**: {benchmark_results['max_memory_mb']:.1f}MB")
                report.append(f"- **Frames Processed**: {benchmark_results['frames_processed']}")
                
            elif benchmark_name == "stress":
                report.append(f"- **Max Vehicles**: {benchmark_results['max_vehicles_tracked']}")
                report.append(f"- **Drop Rate**: {benchmark_results['drop_rate']:.2%}")
                report.append(f"- **Average FPS**: {benchmark_results['fps']:.1f}")
            
            report.append("")
        
        return "\n".join(report)

def main():
    """Main benchmark execution."""
    parser = argparse.ArgumentParser(description="Tracking System Benchmark")
    parser.add_argument("--model", type=str, help="Path to YOLOv8 model (optional)")
    parser.add_argument("--output", type=str, default="tracking_benchmark_results.json",
                       help="Output file for results")
    parser.add_argument("--report", type=str, default="tracking_benchmark_report.md",
                       help="Output file for report")
    parser.add_argument("--test", type=str, choices=["performance", "accuracy", "memory", "stress", "all"],
                       default="all", help="Which test to run")
    
    args = parser.parse_args()
    
    # Create benchmark instance
    benchmark = TrackingBenchmark(args.model)
    
    # Run specified tests
    if args.test == "all":
        results = benchmark.run_all_benchmarks()
    elif args.test == "performance":
        results = {"benchmarks": {"performance": benchmark.benchmark_tracking_performance()}}
    elif args.test == "accuracy":
        results = {"benchmarks": {"accuracy": benchmark.benchmark_tracking_accuracy()}}
    elif args.test == "memory":
        results = {"benchmarks": {"memory": benchmark.benchmark_memory_usage()}}
    elif args.test == "stress":
        results = {"benchmarks": {"stress": benchmark.benchmark_stress_test()}}
    
    # Save results
    benchmark.save_results(results, args.output)
    
    # Generate and save report
    report = benchmark.generate_report(results)
    with open(args.report, 'w') as f:
        f.write(report)
    
    print(f"Benchmark completed. Results saved to {args.output}")
    print(f"Report saved to {args.report}")

if __name__ == "__main__":
    main()