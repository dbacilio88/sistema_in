"""
Speed Analysis Benchmarks.

Performance benchmarks for speed calculation and violation detection.
"""

import time
import numpy as np
import cv2
from typing import List, Dict, Any
import statistics
import logging

from src.speed.camera_calibrator import CameraCalibrator, CalibrationZone
from src.speed.speed_calculator import SpeedCalculator
from src.speed.speed_analyzer import SpeedAnalyzer, AnalysisMode
from src.tracking.trajectory import Trajectory
from src.detection.vehicle_detector import YOLOv8VehicleDetector, Detection
from src.tracking.vehicle_tracker import VehicleTracker, TrackedVehicle

logger = logging.getLogger(__name__)

class SpeedBenchmark:
    """Benchmark suite for speed analysis components."""
    
    def __init__(self):
        """Initialize benchmark suite."""
        self.results = {}
        self.setup_components()
    
    def setup_components(self):
        """Setup test components."""
        # Setup calibrator
        self.calibrator = CameraCalibrator()
        self.calibrator.create_default_highway_calibration(1920, 1080)
        
        # Setup calculator
        self.calculator = SpeedCalculator(self.calibrator)
        
        # Mock detector and tracker for analyzer tests
        from unittest.mock import Mock
        detector = Mock(spec=YOLOv8VehicleDetector)
        tracker = Mock(spec=VehicleTracker)
        
        self.analyzer = SpeedAnalyzer(detector, tracker, self.calibrator, AnalysisMode.REALTIME)
    
    def create_test_trajectory(self, vehicle_id: int, num_points: int = 20) -> Trajectory:
        """Create test trajectory with specified number of points."""
        trajectory = Trajectory(vehicle_id=vehicle_id, max_history=100)
        
        base_time = time.time()
        for i in range(num_points):
            # Simulate vehicle moving diagonally
            x = 200 + i * 30
            y = 400 - i * 10
            timestamp = base_time + i * 0.1  # 10 FPS
            trajectory.add_position((x, y), timestamp)
        
        return trajectory
    
    def benchmark_calibration_setup(self, num_points: int = 6) -> Dict[str, float]:
        """Benchmark calibration setup time."""
        times = []
        
        for _ in range(10):  # Run 10 times for average
            calibrator = CameraCalibrator()
            
            start_time = time.time()
            
            # Add calibration points
            for i in range(num_points):
                px = 100 + i * 100
                py = 400 - i * 30
                rx = i * 5.0
                ry = i * 10.0
                calibrator.add_calibration_point(px, py, rx, ry)
            
            end_time = time.time()
            times.append(end_time - start_time)
        
        return {
            "avg_time": statistics.mean(times),
            "min_time": min(times),
            "max_time": max(times),
            "std_time": statistics.stdev(times) if len(times) > 1 else 0
        }
    
    def benchmark_pixel_to_real_conversion(self, num_conversions: int = 1000) -> Dict[str, float]:
        """Benchmark pixel to real-world coordinate conversion."""
        times = []
        
        # Generate random pixel coordinates
        pixel_coords = [(np.random.randint(0, 1920), np.random.randint(0, 1080)) 
                       for _ in range(num_conversions)]
        
        start_time = time.time()
        
        successful_conversions = 0
        for px, py in pixel_coords:
            result = self.calibrator.pixel_to_real(px, py)
            if result is not None:
                successful_conversions += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return {
            "total_time": total_time,
            "avg_time_per_conversion": total_time / num_conversions,
            "conversions_per_second": num_conversions / total_time,
            "success_rate": successful_conversions / num_conversions
        }
    
    def benchmark_distance_calculation(self, num_calculations: int = 1000) -> Dict[str, float]:
        """Benchmark distance calculation between pixel points."""
        times = []
        
        # Generate random point pairs
        point_pairs = [
            ((np.random.randint(0, 1920), np.random.randint(0, 1080)),
             (np.random.randint(0, 1920), np.random.randint(0, 1080)))
            for _ in range(num_calculations)
        ]
        
        start_time = time.time()
        
        successful_calculations = 0
        distances = []
        
        for point1, point2 in point_pairs:
            distance = self.calibrator.calculate_distance(point1, point2)
            if distance is not None:
                successful_calculations += 1
                distances.append(distance)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return {
            "total_time": total_time,
            "avg_time_per_calculation": total_time / num_calculations,
            "calculations_per_second": num_calculations / total_time,
            "success_rate": successful_calculations / num_calculations,
            "avg_distance": statistics.mean(distances) if distances else 0,
            "distance_range": (min(distances), max(distances)) if distances else (0, 0)
        }
    
    def benchmark_speed_calculation_from_trajectory(self, num_vehicles: int = 100) -> Dict[str, float]:
        """Benchmark speed calculation from trajectories."""
        trajectories = [self.create_test_trajectory(i, num_points=20) for i in range(num_vehicles)]
        
        start_time = time.time()
        
        successful_calculations = 0
        speeds = []
        
        for trajectory in trajectories:
            measurement = self.calculator.calculate_speed_from_trajectory(trajectory)
            if measurement is not None:
                successful_calculations += 1
                speeds.append(measurement.speed_kmh)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return {
            "total_time": total_time,
            "avg_time_per_calculation": total_time / num_vehicles,
            "calculations_per_second": num_vehicles / total_time,
            "success_rate": successful_calculations / num_vehicles,
            "avg_speed": statistics.mean(speeds) if speeds else 0,
            "speed_range": (min(speeds), max(speeds)) if speeds else (0, 0)
        }
    
    def benchmark_instantaneous_speed_calculation(self, trajectory_length: int = 50) -> Dict[str, float]:
        """Benchmark instantaneous speed calculation."""
        trajectory = self.create_test_trajectory(1, num_points=trajectory_length)
        
        times = []
        for window_size in [3, 5, 7]:
            start_time = time.time()
            speeds = self.calculator.calculate_instantaneous_speed(trajectory, window_size)
            end_time = time.time()
            
            times.append({
                "window_size": window_size,
                "time": end_time - start_time,
                "num_speeds": len(speeds),
                "speeds_per_second": len(speeds) / (end_time - start_time) if (end_time - start_time) > 0 else 0
            })
        
        return {
            "trajectory_length": trajectory_length,
            "window_results": times
        }
    
    def benchmark_violation_detection(self, num_measurements: int = 1000) -> Dict[str, float]:
        """Benchmark violation detection performance."""
        # Create test measurements with varying speeds
        measurements = []
        
        for i in range(num_measurements):
            # Generate speeds from 40-160 km/h
            speed = 40 + (120 * i / num_measurements)
            
            from src.speed.speed_calculator import SpeedMeasurement
            measurement = SpeedMeasurement(
                vehicle_id=i,
                timestamp=time.time(),
                speed_kmh=speed,
                speed_mps=speed / 3.6,
                distance_traveled=20.0,
                time_elapsed=2.0,
                measurement_zone="highway_main",
                confidence=0.9,
                entry_point=(0, 0),
                exit_point=(20, 0),
                entry_time=time.time() - 2,
                exit_time=time.time(),
                pixel_trajectory=[(100, 300), (300, 220)],
                real_trajectory=[(0, 0), (20, 0)]
            )
            measurements.append(measurement)
        
        start_time = time.time()
        
        violations = []
        for measurement in measurements:
            violation = self.calculator.detect_speed_violation(measurement)
            if violation is not None:
                violations.append(violation)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return {
            "total_time": total_time,
            "avg_time_per_check": total_time / num_measurements,
            "checks_per_second": num_measurements / total_time,
            "violation_rate": len(violations) / num_measurements,
            "total_violations": len(violations)
        }
    
    def benchmark_frame_analysis(self, num_frames: int = 100) -> Dict[str, float]:
        """Benchmark complete frame analysis."""
        # Create test frames
        frames = [np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8) 
                 for _ in range(num_frames)]
        
        # Mock detector and tracker responses
        detection = Detection(class_id=0, class_name="car", confidence=0.9, bbox=(100, 100, 200, 200))
        tracked_vehicle = TrackedVehicle(
            track_id=1, class_name="car", confidence=0.9, bbox=(100, 100, 200, 200),
            center_x=150, center_y=150, consecutive_frames=15
        )
        
        self.analyzer.detector.detect.return_value = [detection]
        self.analyzer.tracker.update.return_value = [tracked_vehicle]
        
        times = []
        fps_values = []
        
        for frame in frames:
            start_time = time.time()
            result = self.analyzer.analyze_frame(frame)
            end_time = time.time()
            
            frame_time = end_time - start_time
            times.append(frame_time)
            fps_values.append(result.fps)
        
        return {
            "num_frames": num_frames,
            "total_time": sum(times),
            "avg_time_per_frame": statistics.mean(times),
            "min_time_per_frame": min(times),
            "max_time_per_frame": max(times),
            "avg_fps": statistics.mean(fps_values),
            "min_fps": min(fps_values),
            "max_fps": max(fps_values),
            "frames_per_second": num_frames / sum(times)
        }
    
    def benchmark_memory_usage(self) -> Dict[str, Any]:
        """Benchmark memory usage of components."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Add many trajectories
        for i in range(1000):
            trajectory = self.create_test_trajectory(i, num_points=50)
            self.calculator.calculate_speed_from_trajectory(trajectory)
        
        # Memory after calculations
        after_calculations = process.memory_info().rss / 1024 / 1024  # MB
        
        # Add many violation events
        from unittest.mock import Mock
        for i in range(500):
            event = Mock()
            event.vehicle_id = i
            event.timestamp = time.time()
            self.analyzer.violation_events.append(event)
        
        # Memory after violations
        after_violations = process.memory_info().rss / 1024 / 1024  # MB
        
        return {
            "baseline_memory_mb": baseline_memory,
            "after_calculations_mb": after_calculations,
            "after_violations_mb": after_violations,
            "calculations_memory_increase_mb": after_calculations - baseline_memory,
            "violations_memory_increase_mb": after_violations - after_calculations,
            "total_memory_increase_mb": after_violations - baseline_memory
        }
    
    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all benchmarks and return results."""
        logger.info("Starting speed analysis benchmarks...")
        
        benchmarks = {
            "calibration_setup": self.benchmark_calibration_setup,
            "pixel_to_real_conversion": self.benchmark_pixel_to_real_conversion,
            "distance_calculation": self.benchmark_distance_calculation,
            "speed_calculation_from_trajectory": self.benchmark_speed_calculation_from_trajectory,
            "instantaneous_speed_calculation": self.benchmark_instantaneous_speed_calculation,
            "violation_detection": self.benchmark_violation_detection,
            "frame_analysis": self.benchmark_frame_analysis,
            "memory_usage": self.benchmark_memory_usage
        }
        
        results = {}
        
        for name, benchmark_func in benchmarks.items():
            logger.info(f"Running {name} benchmark...")
            try:
                start_time = time.time()
                result = benchmark_func()
                end_time = time.time()
                
                result["benchmark_time"] = end_time - start_time
                results[name] = result
                
                logger.info(f"Completed {name} benchmark in {end_time - start_time:.3f}s")
            except Exception as e:
                logger.error(f"Failed to run {name} benchmark: {e}")
                results[name] = {"error": str(e)}
        
        # Generate summary
        results["summary"] = self.generate_benchmark_summary(results)
        
        return results
    
    def generate_benchmark_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate benchmark summary."""
        summary = {
            "total_benchmarks": len([k for k in results.keys() if k != "summary"]),
            "successful_benchmarks": len([k for k, v in results.items() if k != "summary" and "error" not in v]),
            "calibration_performance": {},
            "calculation_performance": {},
            "analysis_performance": {},
            "memory_performance": {}
        }
        
        # Calibration performance
        if "calibration_setup" in results and "error" not in results["calibration_setup"]:
            summary["calibration_performance"]["setup_time"] = results["calibration_setup"]["avg_time"]
        
        if "pixel_to_real_conversion" in results and "error" not in results["pixel_to_real_conversion"]:
            summary["calibration_performance"]["conversions_per_second"] = results["pixel_to_real_conversion"]["conversions_per_second"]
        
        # Calculation performance
        if "speed_calculation_from_trajectory" in results and "error" not in results["speed_calculation_from_trajectory"]:
            summary["calculation_performance"]["speed_calculations_per_second"] = results["speed_calculation_from_trajectory"]["calculations_per_second"]
        
        if "violation_detection" in results and "error" not in results["violation_detection"]:
            summary["calculation_performance"]["violation_checks_per_second"] = results["violation_detection"]["checks_per_second"]
        
        # Analysis performance
        if "frame_analysis" in results and "error" not in results["frame_analysis"]:
            summary["analysis_performance"]["avg_fps"] = results["frame_analysis"]["avg_fps"]
            summary["analysis_performance"]["frames_per_second"] = results["frame_analysis"]["frames_per_second"]
        
        # Memory performance
        if "memory_usage" in results and "error" not in results["memory_usage"]:
            summary["memory_performance"] = results["memory_usage"]
        
        return summary
    
    def print_results(self, results: Dict[str, Any]):
        """Print benchmark results in a readable format."""
        print("\n" + "="*80)
        print("SPEED ANALYSIS BENCHMARK RESULTS")
        print("="*80)
        
        if "summary" in results:
            summary = results["summary"]
            print(f"\nSUMMARY:")
            print(f"  Total benchmarks: {summary['total_benchmarks']}")
            print(f"  Successful: {summary['successful_benchmarks']}")
            
            if summary.get("calibration_performance"):
                perf = summary["calibration_performance"]
                print(f"\nCALIBRATION PERFORMANCE:")
                if "setup_time" in perf:
                    print(f"  Setup time: {perf['setup_time']:.4f}s")
                if "conversions_per_second" in perf:
                    print(f"  Conversions/sec: {perf['conversions_per_second']:.1f}")
            
            if summary.get("calculation_performance"):
                perf = summary["calculation_performance"]
                print(f"\nCALCULATION PERFORMANCE:")
                if "speed_calculations_per_second" in perf:
                    print(f"  Speed calculations/sec: {perf['speed_calculations_per_second']:.1f}")
                if "violation_checks_per_second" in perf:
                    print(f"  Violation checks/sec: {perf['violation_checks_per_second']:.1f}")
            
            if summary.get("analysis_performance"):
                perf = summary["analysis_performance"]
                print(f"\nANALYSIS PERFORMANCE:")
                if "avg_fps" in perf:
                    print(f"  Average FPS: {perf['avg_fps']:.1f}")
                if "frames_per_second" in perf:
                    print(f"  Processing rate: {perf['frames_per_second']:.1f} frames/sec")
            
            if summary.get("memory_performance"):
                perf = summary["memory_performance"]
                print(f"\nMEMORY PERFORMANCE:")
                print(f"  Baseline: {perf.get('baseline_memory_mb', 0):.1f} MB")
                print(f"  Total increase: {perf.get('total_memory_increase_mb', 0):.1f} MB")
        
        print("\nDETAILED RESULTS:")
        for name, result in results.items():
            if name == "summary":
                continue
            
            print(f"\n{name.upper().replace('_', ' ')}:")
            if "error" in result:
                print(f"  ERROR: {result['error']}")
            else:
                for key, value in result.items():
                    if isinstance(value, float):
                        print(f"  {key}: {value:.4f}")
                    elif isinstance(value, (int, str)):
                        print(f"  {key}: {value}")
                    elif isinstance(value, tuple):
                        print(f"  {key}: {value}")
                    elif isinstance(value, list) and len(value) <= 5:
                        print(f"  {key}: {value}")
        
        print("\n" + "="*80)


def main():
    """Run speed analysis benchmarks."""
    benchmark = SpeedBenchmark()
    results = benchmark.run_all_benchmarks()
    benchmark.print_results(results)
    
    # Save results to file
    import json
    with open("speed_benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to speed_benchmark_results.json")


if __name__ == "__main__":
    main()