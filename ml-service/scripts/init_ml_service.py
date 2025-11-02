#!/usr/bin/env python3
"""
ML Service Initialization and Setup Script
Downloads models, validates configuration, and prepares the service
"""

import sys
import os
import logging
from pathlib import Path
import json
import time
import numpy as np
from typing import Dict, Any

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.config import ml_settings
from src.detection import YOLOv8VehicleDetector

# Set up logging
logging.basicConfig(
    level=getattr(logging, ml_settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MLServiceInitializer:
    """Initialize and validate ML service components"""
    
    def __init__(self):
        self.initialization_results = {}
        
    def create_directories(self) -> bool:
        """Create necessary directories"""
        logger.info("Creating service directories...")
        
        try:
            ml_settings.create_directories()
            
            # Check if directories were created
            required_dirs = [
                ml_settings.MODELS_DIR,
                ml_settings.WEIGHTS_DIR,
                ml_settings.DATASETS_DIR,
                ml_settings.OUTPUTS_DIR,
                ml_settings.LOGS_DIR
            ]
            
            for dir_path in required_dirs:
                if not dir_path.exists():
                    raise Exception(f"Failed to create directory: {dir_path}")
                logger.info(f"✅ Directory created: {dir_path}")
            
            self.initialization_results["directories"] = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
            self.initialization_results["directories"] = False
            return False
    
    def download_and_convert_models(self) -> bool:
        """Download and convert YOLOv8 models"""
        logger.info("Downloading and converting YOLOv8 models...")
        
        try:
            from ultralytics import YOLO
            
            # Download PyTorch model
            pytorch_path = ml_settings.YOLO_WEIGHTS_PATH
            onnx_path = ml_settings.YOLO_ONNX_PATH
            
            logger.info(f"Downloading YOLOv8{ml_settings.YOLO_MODEL_SIZE} model...")
            model = YOLO(f"yolov8{ml_settings.YOLO_MODEL_SIZE}.pt")
            
            # Save PyTorch weights
            pytorch_path.parent.mkdir(parents=True, exist_ok=True)
            
            if not pytorch_path.exists():
                logger.info(f"Saving PyTorch model to: {pytorch_path}")
                # The model is already downloaded, we just need to move it
                import shutil
                source_path = Path.home() / ".ultralytics" / "models" / f"yolov8{ml_settings.YOLO_MODEL_SIZE}.pt"
                if source_path.exists():
                    shutil.copy2(source_path, pytorch_path)
            
            # Convert to ONNX
            if not onnx_path.exists():
                logger.info("Converting to ONNX format...")
                model.export(
                    format="onnx",
                    imgsz=640,
                    dynamic=True,
                    simplify=True,
                    optimize=True
                )
                
                # Move ONNX file to correct location
                source_onnx = pytorch_path.with_suffix('.onnx')
                if source_onnx.exists():
                    source_onnx.rename(onnx_path)
                    logger.info(f"✅ ONNX model saved to: {onnx_path}")
                else:
                    raise Exception("ONNX export failed - file not found")
            else:
                logger.info(f"✅ ONNX model already exists: {onnx_path}")
            
            # Validate model files
            if not pytorch_path.exists():
                raise Exception(f"PyTorch model not found: {pytorch_path}")
            if not onnx_path.exists():
                raise Exception(f"ONNX model not found: {onnx_path}")
            
            # Get file sizes
            pytorch_size = pytorch_path.stat().st_size / (1024*1024)  # MB
            onnx_size = onnx_path.stat().st_size / (1024*1024)  # MB
            
            self.initialization_results["models"] = {
                "status": True,
                "pytorch_path": str(pytorch_path),
                "onnx_path": str(onnx_path),
                "pytorch_size_mb": round(pytorch_size, 2),
                "onnx_size_mb": round(onnx_size, 2)
            }
            
            logger.info(f"✅ Models ready - PyTorch: {pytorch_size:.1f}MB, ONNX: {onnx_size:.1f}MB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download/convert models: {e}")
            self.initialization_results["models"] = {"status": False, "error": str(e)}
            return False
    
    def validate_gpu_setup(self) -> bool:
        """Validate GPU and CUDA setup"""
        logger.info("Validating GPU setup...")
        
        try:
            import torch
            import onnxruntime as ort
            
            gpu_info = {
                "cuda_available": torch.cuda.is_available(),
                "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
                "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
                "gpu_names": [],
                "onnx_providers": ort.get_available_providers()
            }
            
            if gpu_info["cuda_available"]:
                for i in range(gpu_info["gpu_count"]):
                    gpu_name = torch.cuda.get_device_name(i)
                    gpu_info["gpu_names"].append(gpu_name)
                    logger.info(f"✅ GPU {i}: {gpu_name}")
            else:
                logger.warning("⚠️ CUDA not available - will use CPU only")
            
            # Check ONNX providers
            has_gpu_provider = any(
                provider in gpu_info["onnx_providers"] 
                for provider in ["CUDAExecutionProvider", "TensorrtExecutionProvider"]
            )
            
            if has_gpu_provider:
                logger.info("✅ ONNX Runtime GPU providers available")
            else:
                logger.warning("⚠️ ONNX Runtime GPU providers not available")
            
            self.initialization_results["gpu"] = gpu_info
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate GPU setup: {e}")
            self.initialization_results["gpu"] = {"status": False, "error": str(e)}
            return False
    
    def test_detector_initialization(self) -> bool:
        """Test YOLOv8 detector initialization"""
        logger.info("Testing detector initialization...")
        
        try:
            # Try to initialize detector
            detector = YOLOv8VehicleDetector()
            
            # Test with dummy frame
            import numpy as np
            dummy_frame = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            
            start_time = time.time()
            detections, metrics = detector.detect(dummy_frame)
            init_time = time.time() - start_time
            
            detector_info = {
                "status": True,
                "model_path": str(detector.model_path),
                "input_size": detector.input_size,
                "confidence_threshold": detector.confidence_threshold,
                "test_inference_time_ms": metrics.total_time_ms,
                "test_detections_count": len(detections),
                "initialization_time_s": round(init_time, 2)
            }
            
            logger.info(f"✅ Detector initialized successfully")
            logger.info(f"   Inference time: {metrics.total_time_ms:.1f}ms")
            logger.info(f"   Initialization time: {init_time:.1f}s")
            
            self.initialization_results["detector"] = detector_info
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize detector: {e}")
            self.initialization_results["detector"] = {"status": False, "error": str(e)}
            return False
    
    def validate_configuration(self) -> bool:
        """Validate ML service configuration"""
        logger.info("Validating configuration...")
        
        try:
            config_info = {
                "model_size": ml_settings.YOLO_MODEL_SIZE,
                "confidence_threshold": ml_settings.CONFIDENCE_THRESHOLD,
                "nms_threshold": ml_settings.NMS_THRESHOLD,
                "target_fps": ml_settings.TARGET_FPS,
                "max_latency_ms": ml_settings.MAX_LATENCY_MS,
                "use_gpu": ml_settings.USE_GPU,
                "tensorrt_enabled": ml_settings.TENSORRT_ENABLED,
                "vehicle_classes": ml_settings.VEHICLE_CLASSES,
                "batch_size": ml_settings.BATCH_SIZE
            }
            
            # Validate configuration values
            issues = []
            
            if ml_settings.CONFIDENCE_THRESHOLD <= 0 or ml_settings.CONFIDENCE_THRESHOLD >= 1:
                issues.append("Invalid confidence threshold (should be 0-1)")
            
            if ml_settings.NMS_THRESHOLD <= 0 or ml_settings.NMS_THRESHOLD >= 1:
                issues.append("Invalid NMS threshold (should be 0-1)")
            
            if ml_settings.TARGET_FPS <= 0:
                issues.append("Invalid target FPS (should be > 0)")
            
            if ml_settings.MAX_LATENCY_MS <= 0:
                issues.append("Invalid max latency (should be > 0)")
            
            if not ml_settings.VEHICLE_CLASSES:
                issues.append("No vehicle classes defined")
            
            if issues:
                config_info["issues"] = issues
                logger.warning(f"Configuration issues found: {issues}")
            else:
                logger.info("✅ Configuration valid")
            
            self.initialization_results["configuration"] = config_info
            return len(issues) == 0
            
        except Exception as e:
            logger.error(f"Failed to validate configuration: {e}")
            self.initialization_results["configuration"] = {"status": False, "error": str(e)}
            return False
    
    def run_quick_benchmark(self) -> bool:
        """Run quick performance benchmark"""
        logger.info("Running quick benchmark...")
        
        try:
            detector = YOLOv8VehicleDetector()
            
            # Test different resolutions
            test_resolutions = [
                (480, 640),   # 480p
                (720, 1280),  # 720p
                (1080, 1920), # 1080p
            ]
            
            benchmark_results = {}
            
            for height, width in test_resolutions:
                resolution_key = f"{width}x{height}"
                
                # Create test frame
                test_frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
                
                # Warm up
                for _ in range(3):
                    detector.detect(test_frame)
                
                # Benchmark
                times = []
                for _ in range(10):
                    start = time.time()
                    _, metrics = detector.detect(test_frame)
                    times.append(metrics.total_time_ms)
                
                avg_time = np.mean(times)
                avg_fps = 1000 / avg_time if avg_time > 0 else 0
                
                benchmark_results[resolution_key] = {
                    "avg_time_ms": round(avg_time, 2),
                    "avg_fps": round(avg_fps, 2),
                    "meets_target": avg_time < ml_settings.MAX_LATENCY_MS
                }
                
                logger.info(f"  {resolution_key}: {avg_time:.1f}ms ({avg_fps:.1f} FPS)")
            
            self.initialization_results["benchmark"] = benchmark_results
            
            # Check if any resolution meets targets
            meets_targets = any(r["meets_target"] for r in benchmark_results.values())
            
            if meets_targets:
                logger.info("✅ Performance targets met")
            else:
                logger.warning("⚠️ Performance targets not met - consider optimization")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to run benchmark: {e}")
            self.initialization_results["benchmark"] = {"status": False, "error": str(e)}
            return False
    
    def save_initialization_report(self) -> str:
        """Save initialization report"""
        report_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "service_version": "1.0.0",
            "initialization_results": self.initialization_results
        }
        
        report_file = ml_settings.LOGS_DIR / f"initialization_report_{int(time.time())}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"📄 Initialization report saved: {report_file}")
        return str(report_file)
    
    def run_full_initialization(self) -> bool:
        """Run complete initialization sequence"""
        logger.info("🚀 Starting ML Service initialization...")
        
        steps = [
            ("Creating directories", self.create_directories),
            ("Downloading models", self.download_and_convert_models),
            ("Validating GPU setup", self.validate_gpu_setup),
            ("Validating configuration", self.validate_configuration),
            ("Testing detector", self.test_detector_initialization),
            ("Running benchmark", self.run_quick_benchmark)
        ]
        
        total_steps = len(steps)
        completed_steps = 0
        
        for step_name, step_func in steps:
            logger.info(f"Step {completed_steps + 1}/{total_steps}: {step_name}")
            
            try:
                success = step_func()
                if success:
                    completed_steps += 1
                    logger.info(f"✅ {step_name} completed")
                else:
                    logger.error(f"❌ {step_name} failed")
            except Exception as e:
                logger.error(f"❌ {step_name} failed with error: {e}")
        
        # Save report
        report_file = self.save_initialization_report()
        
        success_rate = completed_steps / total_steps
        
        if success_rate >= 0.8:  # 80% success rate
            logger.info(f"🎉 Initialization completed successfully ({completed_steps}/{total_steps} steps)")
            logger.info("ML Service is ready for use!")
            return True
        else:
            logger.error(f"❌ Initialization failed ({completed_steps}/{total_steps} steps)")
            logger.error("Check logs and fix issues before using ML Service")
            return False


def main():
    """Main initialization function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ML Service Initialization")
    parser.add_argument("--skip-models", action="store_true", 
                       help="Skip model download")
    parser.add_argument("--skip-benchmark", action="store_true",
                       help="Skip performance benchmark")
    parser.add_argument("--skip-gpu-check", action="store_true",
                       help="Skip GPU validation")
    
    args = parser.parse_args()
    
    initializer = MLServiceInitializer()
    
    try:
        if args.skip_models:
            logger.info("Skipping model download as requested")
        if args.skip_benchmark:
            logger.info("Skipping benchmark as requested")
        if args.skip_gpu_check:
            logger.info("Skipping GPU check as requested")
        
        # Run custom initialization based on arguments
        success = True
        
        # Always create directories and validate config
        success &= initializer.create_directories()
        success &= initializer.validate_configuration()
        
        if not args.skip_models:
            success &= initializer.download_and_convert_models()
        
        if not args.skip_gpu_check:
            success &= initializer.validate_gpu_setup()
        
        success &= initializer.test_detector_initialization()
        
        if not args.skip_benchmark:
            success &= initializer.run_quick_benchmark()
        
        # Save report
        initializer.save_initialization_report()
        
        if success:
            logger.info("🎉 ML Service initialization completed successfully!")
            return 0
        else:
            logger.error("❌ ML Service initialization failed!")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Initialization cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Initialization failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())