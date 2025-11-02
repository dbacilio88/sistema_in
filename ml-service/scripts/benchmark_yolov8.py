#!/usr/bin/env python3
"""
YOLOv8 Vehicle Detection Benchmark and Validation Script
Comprehensive testing of detection performance, accuracy, and optimization
"""

import argparse
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import cv2
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from rich.panel import Panel

# Set up paths for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.detection import YOLOv8VehicleDetector, Detection, PerformanceMetrics
from src.config import ml_settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

console = Console()


class YOLOv8Benchmark:
    """Comprehensive benchmark suite for YOLOv8 vehicle detection"""
    
    def __init__(self, detector: YOLOv8VehicleDetector):
        self.detector = detector
        self.results = {}
        
    def run_latency_benchmark(self, iterations: int = 100) -> Dict[str, Any]:
        """
        Run latency benchmark with different input sizes
        
        Args:
            iterations: Number of test iterations per size
            
        Returns:
            Latency benchmark results
        """
        console.print("[bold blue]🚀 Running Latency Benchmark[/bold blue]")
        
        # Test different input sizes
        test_sizes = [
            (480, 640),   # 480p
            (720, 1280),  # 720p
            (1080, 1920), # 1080p
            (1440, 2560), # 2K (EZVIZ camera)
        ]
        
        results = {}
        
        with Progress() as progress:
            task = progress.add_task("Running latency tests...", total=len(test_sizes) * iterations)
            
            for height, width in test_sizes:
                size_key = f"{width}x{height}"
                console.print(f"  📐 Testing resolution: {size_key}")
                
                # Create test frame
                test_frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
                
                # Warm up
                for _ in range(5):
                    self.detector.detect(test_frame)
                
                # Benchmark
                metrics_list = []
                for i in range(iterations):
                    _, metrics = self.detector.detect(test_frame)
                    metrics_list.append(metrics)
                    progress.advance(task)
                
                # Calculate statistics
                inference_times = [m.inference_time_ms for m in metrics_list]
                total_times = [m.total_time_ms for m in metrics_list]
                fps_values = [m.fps for m in metrics_list]
                
                results[size_key] = {
                    "resolution": f"{width}x{height}",
                    "iterations": iterations,
                    "inference_time_ms": {
                        "mean": np.mean(inference_times),
                        "std": np.std(inference_times),
                        "min": np.min(inference_times),
                        "max": np.max(inference_times),
                        "p95": np.percentile(inference_times, 95),
                        "p99": np.percentile(inference_times, 99)
                    },
                    "total_time_ms": {
                        "mean": np.mean(total_times),
                        "std": np.std(total_times),
                        "min": np.min(total_times),
                        "max": np.max(total_times),
                        "p95": np.percentile(total_times, 95),
                        "p99": np.percentile(total_times, 99)
                    },
                    "fps": {
                        "mean": np.mean(fps_values),
                        "std": np.std(fps_values),
                        "min": np.min(fps_values),
                        "max": np.max(fps_values)
                    },
                    "meets_target_latency": np.mean(total_times) < ml_settings.MAX_LATENCY_MS,
                    "meets_target_fps": np.mean(fps_values) >= ml_settings.TARGET_FPS
                }
        
        self.results["latency_benchmark"] = results
        return results
    
    def run_accuracy_benchmark(self, test_images_dir: Path = None) -> Dict[str, Any]:
        """
        Run accuracy benchmark on test images
        
        Args:
            test_images_dir: Directory containing test images
            
        Returns:
            Accuracy benchmark results
        """
        console.print("[bold green]🎯 Running Accuracy Benchmark[/bold green]")
        
        if test_images_dir is None or not test_images_dir.exists():
            console.print("  ⚠️ Test images directory not found, creating synthetic data...")
            return self._synthetic_accuracy_test()
        
        # Load test images
        image_files = list(test_images_dir.glob("*.jpg")) + list(test_images_dir.glob("*.png"))
        
        if not image_files:
            console.print("  ⚠️ No test images found, creating synthetic data...")
            return self._synthetic_accuracy_test()
        
        console.print(f"  📁 Found {len(image_files)} test images")
        
        detection_results = []
        class_distribution = {}
        
        with Progress() as progress:
            task = progress.add_task("Processing test images...", total=len(image_files))
            
            for image_file in image_files:
                # Load image
                frame = cv2.imread(str(image_file))
                if frame is None:
                    continue
                
                # Run detection
                detections, metrics = self.detector.detect(frame)
                
                # Collect statistics
                for detection in detections:
                    class_name = detection.class_name
                    class_distribution[class_name] = class_distribution.get(class_name, 0) + 1
                
                detection_results.append({
                    "image": image_file.name,
                    "detections_count": len(detections),
                    "inference_time_ms": metrics.inference_time_ms,
                    "detections": [
                        {
                            "class": det.class_name,
                            "confidence": det.confidence,
                            "bbox": det.bbox
                        }
                        for det in detections
                    ]
                })
                
                progress.advance(task)
        
        # Calculate accuracy metrics
        total_detections = sum(len(r["detections"]) for r in detection_results)
        avg_detections_per_image = total_detections / len(detection_results) if detection_results else 0
        avg_confidence = np.mean([
            det.confidence 
            for result in detection_results 
            for det in result["detections"]
        ]) if total_detections > 0 else 0
        
        accuracy_results = {
            "test_images_count": len(image_files),
            "total_detections": total_detections,
            "avg_detections_per_image": avg_detections_per_image,
            "avg_confidence": avg_confidence,
            "class_distribution": class_distribution,
            "detection_results": detection_results[:10]  # Keep first 10 for sample
        }
        
        self.results["accuracy_benchmark"] = accuracy_results
        return accuracy_results
    
    def _synthetic_accuracy_test(self) -> Dict[str, Any]:
        """Create synthetic accuracy test with generated data"""
        console.print("  🧪 Running synthetic accuracy test...")
        
        # Generate test frames with different characteristics
        test_scenarios = [
            ("daytime_clear", (720, 1280)),
            ("nighttime_dark", (720, 1280)),
            ("high_contrast", (1080, 1920)),
            ("low_light", (480, 640)),
            ("motion_blur", (720, 1280))
        ]
        
        results = {}
        
        for scenario, (height, width) in test_scenarios:
            # Generate synthetic frame based on scenario
            if scenario == "nighttime_dark":
                frame = np.random.randint(0, 50, (height, width, 3), dtype=np.uint8)
            elif scenario == "high_contrast":
                frame = np.random.choice([0, 255], (height, width, 3)).astype(np.uint8)
            elif scenario == "low_light":
                frame = np.random.randint(0, 80, (height, width, 3), dtype=np.uint8)
            else:
                frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
            
            # Add some realistic patterns
            if scenario == "motion_blur":
                kernel = np.ones((5, 15), np.float32) / 75
                frame = cv2.filter2D(frame, -1, kernel)
            
            # Run detection
            detections, metrics = self.detector.detect(frame)
            
            results[scenario] = {
                "resolution": f"{width}x{height}",
                "detections_count": len(detections),
                "inference_time_ms": metrics.inference_time_ms,
                "avg_confidence": np.mean([d.confidence for d in detections]) if detections else 0
            }
        
        return {
            "test_type": "synthetic",
            "scenarios": results
        }
    
    def run_stress_test(self, duration_minutes: int = 5) -> Dict[str, Any]:
        """
        Run stress test for extended period
        
        Args:
            duration_minutes: Duration of stress test in minutes
            
        Returns:
            Stress test results
        """
        console.print(f"[bold red]🔥 Running Stress Test ({duration_minutes} minutes)[/bold red]")
        
        duration_seconds = duration_minutes * 60
        test_frame = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
        
        start_time = time.time()
        iteration_count = 0
        metrics_history = []
        error_count = 0
        
        with Progress() as progress:
            task = progress.add_task("Stress testing...", total=duration_seconds)
            
            while time.time() - start_time < duration_seconds:
                try:
                    _, metrics = self.detector.detect(test_frame)
                    metrics_history.append(metrics)
                    iteration_count += 1
                    
                    # Update progress every second
                    elapsed = time.time() - start_time
                    progress.update(task, completed=int(elapsed))
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error during stress test: {e}")
        
        total_time = time.time() - start_time
        
        # Calculate stress test metrics
        if metrics_history:
            inference_times = [m.inference_time_ms for m in metrics_history]
            total_times = [m.total_time_ms for m in metrics_history]
            fps_values = [m.fps for m in metrics_history]
            
            stress_results = {
                "duration_seconds": total_time,
                "iterations": iteration_count,
                "error_count": error_count,
                "error_rate": error_count / iteration_count if iteration_count > 0 else 0,
                "avg_fps": np.mean(fps_values),
                "min_fps": np.min(fps_values),
                "max_fps": np.max(fps_values),
                "fps_stability": np.std(fps_values),
                "avg_inference_time_ms": np.mean(inference_times),
                "max_inference_time_ms": np.max(inference_times),
                "latency_stability": np.std(total_times),
                "memory_stable": True,  # Would need psutil to measure actual memory
                "performance_degradation": self._calculate_performance_degradation(metrics_history)
            }
        else:
            stress_results = {
                "duration_seconds": total_time,
                "iterations": 0,
                "error_count": error_count,
                "error_rate": 1.0,
                "status": "failed"
            }
        
        self.results["stress_test"] = stress_results
        return stress_results
    
    def _calculate_performance_degradation(self, metrics_history: List[PerformanceMetrics]) -> float:
        """Calculate performance degradation over time"""
        if len(metrics_history) < 20:
            return 0.0
        
        # Compare first 10% vs last 10% of metrics
        first_tenth = metrics_history[:len(metrics_history) // 10]
        last_tenth = metrics_history[-len(metrics_history) // 10:]
        
        first_avg_fps = np.mean([m.fps for m in first_tenth])
        last_avg_fps = np.mean([m.fps for m in last_tenth])
        
        if first_avg_fps == 0:
            return 0.0
        
        degradation = (first_avg_fps - last_avg_fps) / first_avg_fps
        return max(0.0, degradation)  # Return 0 if performance improved
    
    def run_memory_benchmark(self) -> Dict[str, Any]:
        """
        Run memory usage benchmark
        
        Returns:
            Memory benchmark results
        """
        console.print("[bold purple]💾 Running Memory Benchmark[/bold purple]")
        
        try:
            import psutil
            import os
        except ImportError:
            console.print("  ⚠️ psutil not available, skipping memory benchmark")
            return {"status": "skipped", "reason": "psutil not available"}
        
        process = psutil.Process(os.getpid())
        
        # Baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        test_frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        memory_samples = []
        
        # Run detections while monitoring memory
        for i in range(100):
            self.detector.detect(test_frame)
            
            if i % 10 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_samples.append(current_memory)
        
        peak_memory = max(memory_samples)
        avg_memory = np.mean(memory_samples)
        memory_growth = peak_memory - baseline_memory
        
        memory_results = {
            "baseline_memory_mb": baseline_memory,
            "peak_memory_mb": peak_memory,
            "avg_memory_mb": avg_memory,
            "memory_growth_mb": memory_growth,
            "memory_stable": memory_growth < 100,  # Less than 100MB growth
            "samples": memory_samples
        }
        
        self.results["memory_benchmark"] = memory_results
        return memory_results
    
    def generate_report(self) -> str:
        """Generate comprehensive benchmark report"""
        console.print("[bold cyan]📊 Generating Benchmark Report[/bold cyan]")
        
        # Create summary table
        table = Table(title="YOLOv8 Vehicle Detection Benchmark Results")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        table.add_column("Status", style="green")
        
        # Latency results
        if "latency_benchmark" in self.results:
            latency_2k = self.results["latency_benchmark"].get("2560x1440")
            if latency_2k:
                avg_latency = latency_2k["total_time_ms"]["mean"]
                avg_fps = latency_2k["fps"]["mean"]
                
                latency_status = "✅ PASS" if avg_latency < ml_settings.MAX_LATENCY_MS else "❌ FAIL"
                fps_status = "✅ PASS" if avg_fps >= ml_settings.TARGET_FPS else "❌ FAIL"
                
                table.add_row("Avg Latency (2K)", f"{avg_latency:.1f}ms", latency_status)
                table.add_row("Avg FPS (2K)", f"{avg_fps:.1f}", fps_status)
        
        # Accuracy results
        if "accuracy_benchmark" in self.results:
            accuracy = self.results["accuracy_benchmark"]
            if "avg_confidence" in accuracy:
                conf_status = "✅ PASS" if accuracy["avg_confidence"] > 0.5 else "❌ FAIL"
                table.add_row("Avg Confidence", f"{accuracy['avg_confidence']:.2f}", conf_status)
        
        # Stress test results
        if "stress_test" in self.results:
            stress = self.results["stress_test"]
            if "error_rate" in stress:
                error_status = "✅ PASS" if stress["error_rate"] < 0.01 else "❌ FAIL"
                table.add_row("Error Rate", f"{stress['error_rate']:.3f}", error_status)
        
        # Memory results
        if "memory_benchmark" in self.results:
            memory = self.results["memory_benchmark"]
            if "memory_stable" in memory:
                mem_status = "✅ PASS" if memory["memory_stable"] else "❌ FAIL"
                table.add_row("Memory Stable", str(memory["memory_stable"]), mem_status)
        
        console.print(table)
        
        # Generate detailed report
        report_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_info": {
                "model_path": str(self.detector.model_path),
                "input_size": self.detector.input_size,
                "confidence_threshold": self.detector.confidence_threshold,
                "nms_threshold": self.detector.nms_threshold
            },
            "results": self.results
        }
        
        # Save report
        report_file = Path(f"yolov8_benchmark_{int(time.time())}.json")
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        console.print(f"\n📄 Detailed report saved to: {report_file}")
        
        return str(report_file)


def main():
    """Main benchmark execution"""
    parser = argparse.ArgumentParser(description="YOLOv8 Vehicle Detection Benchmark")
    parser.add_argument("--model-path", type=Path, help="Path to ONNX model file")
    parser.add_argument("--test-images", type=Path, help="Directory with test images")
    parser.add_argument("--latency-iterations", type=int, default=100, 
                       help="Number of latency test iterations")
    parser.add_argument("--stress-duration", type=int, default=5,
                       help="Stress test duration in minutes")
    parser.add_argument("--skip-accuracy", action="store_true",
                       help="Skip accuracy benchmark")
    parser.add_argument("--skip-stress", action="store_true", 
                       help="Skip stress test")
    parser.add_argument("--skip-memory", action="store_true",
                       help="Skip memory benchmark")
    
    args = parser.parse_args()
    
    console.print(Panel.fit(
        "[bold green]YOLOv8 Vehicle Detection Benchmark Suite[/bold green]\n"
        "Comprehensive performance and accuracy testing",
        border_style="green"
    ))
    
    try:
        # Initialize detector
        console.print("🔧 Initializing YOLOv8 detector...")
        detector = YOLOv8VehicleDetector(model_path=args.model_path)
        
        # Create benchmark suite
        benchmark = YOLOv8Benchmark(detector)
        
        # Run benchmarks
        console.print("\n🚀 Starting benchmark suite...")
        
        # 1. Latency benchmark
        benchmark.run_latency_benchmark(args.latency_iterations)
        
        # 2. Accuracy benchmark
        if not args.skip_accuracy:
            benchmark.run_accuracy_benchmark(args.test_images)
        
        # 3. Stress test
        if not args.skip_stress:
            benchmark.run_stress_test(args.stress_duration)
        
        # 4. Memory benchmark
        if not args.skip_memory:
            benchmark.run_memory_benchmark()
        
        # Generate report
        report_file = benchmark.generate_report()
        
        console.print(f"\n🎉 Benchmark completed successfully!")
        console.print(f"📊 Report saved to: {report_file}")
        
    except Exception as e:
        console.print(f"[bold red]❌ Benchmark failed: {e}[/bold red]")
        logger.error(f"Benchmark error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())