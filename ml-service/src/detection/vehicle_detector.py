"""
Vehicle detection using YOLOv8 with ONNX Runtime optimization
"""

import time
import logging
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass
import numpy as np
import cv2
import onnxruntime as ort
from ultralytics import YOLO

from src.config import ml_settings

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """Vehicle detection result"""
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    center: Tuple[int, int]
    area: float


@dataclass
class PerformanceMetrics:
    """Performance metrics for detection"""
    inference_time_ms: float
    preprocessing_time_ms: float
    postprocessing_time_ms: float
    total_time_ms: float
    fps: float
    detections_count: int


class YOLOv8VehicleDetector:
    """
    YOLOv8 vehicle detector optimized with ONNX Runtime
    Supports TensorRT acceleration for high-performance inference
    """
    
    def __init__(
        self,
        model_path: Optional[Path] = None,
        confidence_threshold: float = None,
        nms_threshold: float = None,
        use_gpu: bool = None
    ):
        """
        Initialize YOLOv8 vehicle detector
        
        Args:
            model_path: Path to ONNX model file
            confidence_threshold: Minimum confidence for detections
            nms_threshold: Non-maximum suppression threshold
            use_gpu: Whether to use GPU acceleration
        """
        self.model_path = model_path or ml_settings.get_model_path("onnx")
        self.confidence_threshold = confidence_threshold or ml_settings.CONFIDENCE_THRESHOLD
        self.nms_threshold = nms_threshold or ml_settings.NMS_THRESHOLD
        self.use_gpu = use_gpu if use_gpu is not None else ml_settings.USE_GPU
        
        # Model properties
        self.input_size = (640, 640)  # YOLOv8 default input size
        self.session = None
        self.input_name = None
        self.output_names = None
        
        # Performance tracking
        self.performance_history: List[PerformanceMetrics] = []
        
        # Vehicle classes
        self.vehicle_classes = set(ml_settings.VEHICLE_CLASSES)
        self.class_names = ml_settings.CLASS_NAMES
        
        logger.info(f"Initializing YOLOv8 detector with model: {self.model_path}")
        self._load_model()
    
    def _load_model(self) -> None:
        """Load ONNX model with optimal providers"""
        if not self.model_path.exists():
            logger.warning(f"Model file not found: {self.model_path}")
            logger.info("Attempting to download and convert YOLOv8 model...")
            self._download_and_convert_model()
        
        try:
            # Configure providers
            providers = ml_settings.get_onnx_providers()
            
            logger.info(f"Loading ONNX model with providers: {[p[0] if isinstance(p, tuple) else p for p in providers]}")
            
            # Create inference session
            self.session = ort.InferenceSession(
                str(self.model_path),
                providers=providers
            )
            
            # Get input/output information
            self.input_name = self.session.get_inputs()[0].name
            self.output_names = [output.name for output in self.session.get_outputs()]
            
            # Get input shape
            input_shape = self.session.get_inputs()[0].shape
            if len(input_shape) == 4 and input_shape[2] > 0 and input_shape[3] > 0:
                self.input_size = (input_shape[2], input_shape[3])
            
            logger.info(f"Model loaded successfully")
            logger.info(f"Input shape: {input_shape}")
            logger.info(f"Input name: {self.input_name}")
            logger.info(f"Output names: {self.output_names}")
            
            # Test inference
            self._test_inference()
            
        except Exception as e:
            logger.error(f"Failed to load ONNX model: {e}")
            raise
    
    def _download_and_convert_model(self) -> None:
        """Download YOLOv8 model and convert to ONNX"""
        try:
            logger.info(f"Downloading YOLOv8{ml_settings.YOLO_MODEL_SIZE} model...")
            
            # Download PyTorch model
            model = YOLO(f"yolov8{ml_settings.YOLO_MODEL_SIZE}.pt")
            
            # Save PyTorch weights
            pytorch_path = ml_settings.YOLO_WEIGHTS_PATH
            pytorch_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Converting to ONNX format...")
            
            # Export to ONNX
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
                source_onnx.rename(self.model_path)
                logger.info(f"ONNX model saved to: {self.model_path}")
            else:
                raise FileNotFoundError("ONNX export failed")
                
        except Exception as e:
            logger.error(f"Failed to download/convert model: {e}")
            raise
    
    def _test_inference(self) -> None:
        """Test inference with dummy input"""
        try:
            dummy_input = np.random.rand(1, 3, *self.input_size).astype(np.float32)
            
            start_time = time.time()
            outputs = self.session.run(self.output_names, {self.input_name: dummy_input})
            inference_time = (time.time() - start_time) * 1000
            
            logger.info(f"Test inference successful: {inference_time:.2f}ms")
            logger.info(f"Output shapes: {[output.shape for output in outputs]}")
            
        except Exception as e:
            logger.error(f"Test inference failed: {e}")
            raise
    
    def preprocess(self, frame: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Preprocess frame for YOLOv8 inference
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            Tuple of (preprocessed_tensor, scale_factor)
        """
        # Get original dimensions
        original_height, original_width = frame.shape[:2]
        
        # Calculate scale factor
        scale = min(self.input_size[0] / original_width, self.input_size[1] / original_height)
        
        # Resize frame maintaining aspect ratio
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        resized = cv2.resize(frame, (new_width, new_height))
        
        # Create padded image
        padded = np.full((*self.input_size, 3), 114, dtype=np.uint8)
        
        # Calculate padding offsets
        pad_x = (self.input_size[0] - new_width) // 2
        pad_y = (self.input_size[1] - new_height) // 2
        
        # Place resized image in center
        padded[pad_y:pad_y + new_height, pad_x:pad_x + new_width] = resized
        
        # Convert to RGB and normalize
        rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
        
        # Convert to tensor format (NCHW)
        tensor = rgb.transpose(2, 0, 1).astype(np.float32) / 255.0
        tensor = np.expand_dims(tensor, axis=0)
        
        return tensor, scale
    
    def postprocess(
        self, 
        outputs: List[np.ndarray], 
        scale: float, 
        original_shape: Tuple[int, int]
    ) -> List[Detection]:
        """
        Postprocess YOLO outputs to extract vehicle detections
        
        Args:
            outputs: Raw model outputs
            scale: Scale factor from preprocessing
            original_shape: Original frame dimensions (height, width)
            
        Returns:
            List of vehicle detections
        """
        if not outputs or len(outputs) == 0:
            return []
        
        # YOLOv8 output format: [batch, 84, 8400] where 84 = 4 bbox + 80 classes
        predictions = outputs[0]
        
        if len(predictions.shape) == 3:
            predictions = predictions[0]  # Remove batch dimension
        
        # Transpose to [8400, 84]
        if predictions.shape[0] == 84:
            predictions = predictions.T
        
        detections = []
        
        for prediction in predictions:
            # Extract bbox and confidence
            x_center, y_center, width, height = prediction[:4]
            class_scores = prediction[4:]
            
            # Find best class
            class_id = np.argmax(class_scores)
            confidence = class_scores[class_id]
            
            # Filter by confidence and vehicle classes
            if confidence < self.confidence_threshold or class_id not in self.vehicle_classes:
                continue
            
            # Convert to corner coordinates
            x1 = int((x_center - width / 2) / scale)
            y1 = int((y_center - height / 2) / scale)
            x2 = int((x_center + width / 2) / scale)
            y2 = int((y_center + height / 2) / scale)
            
            # Clamp to image bounds
            x1 = max(0, min(x1, original_shape[1]))
            y1 = max(0, min(y1, original_shape[0]))
            x2 = max(0, min(x2, original_shape[1]))
            y2 = max(0, min(y2, original_shape[0]))
            
            # Skip invalid boxes
            if x2 <= x1 or y2 <= y1:
                continue
            
            # Calculate center and area
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            area = (x2 - x1) * (y2 - y1)
            
            detection = Detection(
                class_id=class_id,
                class_name=self.class_names.get(class_id, f"class_{class_id}"),
                confidence=float(confidence),
                bbox=(x1, y1, x2, y2),
                center=(center_x, center_y),
                area=area
            )
            
            detections.append(detection)
        
        # Apply Non-Maximum Suppression
        if len(detections) > 1:
            detections = self._apply_nms(detections)
        
        return detections
    
    def _apply_nms(self, detections: List[Detection]) -> List[Detection]:
        """Apply Non-Maximum Suppression to remove duplicate detections"""
        if len(detections) <= 1:
            return detections
        
        # Prepare data for cv2.dnn.NMSBoxes
        boxes = []
        scores = []
        
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            boxes.append([x1, y1, x2 - x1, y2 - y1])  # Convert to x, y, w, h
            scores.append(det.confidence)
        
        # Apply NMS
        indices = cv2.dnn.NMSBoxes(
            boxes, 
            scores, 
            self.confidence_threshold, 
            self.nms_threshold
        )
        
        if len(indices) == 0:
            return []
        
        # Return filtered detections
        filtered_detections = []
        for i in indices.flatten():
            filtered_detections.append(detections[i])
        
        return filtered_detections
    
    def detect(self, frame: np.ndarray) -> Tuple[List[Detection], PerformanceMetrics]:
        """
        Detect vehicles in a frame
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            Tuple of (detections, performance_metrics)
        """
        total_start = time.time()
        
        # Preprocessing
        preprocess_start = time.time()
        input_tensor, scale = self.preprocess(frame)
        preprocess_time = (time.time() - preprocess_start) * 1000
        
        # Inference
        inference_start = time.time()
        outputs = self.session.run(self.output_names, {self.input_name: input_tensor})
        inference_time = (time.time() - inference_start) * 1000
        
        # Postprocessing
        postprocess_start = time.time()
        detections = self.postprocess(outputs, scale, frame.shape[:2])
        postprocess_time = (time.time() - postprocess_start) * 1000
        
        total_time = (time.time() - total_start) * 1000
        fps = 1000 / total_time if total_time > 0 else 0
        
        # Create performance metrics
        metrics = PerformanceMetrics(
            inference_time_ms=inference_time,
            preprocessing_time_ms=preprocess_time,
            postprocessing_time_ms=postprocess_time,
            total_time_ms=total_time,
            fps=fps,
            detections_count=len(detections)
        )
        
        # Store performance history (keep last 100 measurements)
        self.performance_history.append(metrics)
        if len(self.performance_history) > 100:
            self.performance_history.pop(0)
        
        return detections, metrics
    
    def get_average_performance(self, last_n: int = 50) -> Dict[str, float]:
        """Get average performance metrics from recent detections"""
        if not self.performance_history:
            return {}
        
        recent_metrics = self.performance_history[-last_n:]
        
        return {
            "avg_inference_time_ms": np.mean([m.inference_time_ms for m in recent_metrics]),
            "avg_preprocessing_time_ms": np.mean([m.preprocessing_time_ms for m in recent_metrics]),
            "avg_postprocessing_time_ms": np.mean([m.postprocessing_time_ms for m in recent_metrics]),
            "avg_total_time_ms": np.mean([m.total_time_ms for m in recent_metrics]),
            "avg_fps": np.mean([m.fps for m in recent_metrics]),
            "avg_detections_count": np.mean([m.detections_count for m in recent_metrics]),
            "measurements_count": len(recent_metrics)
        }
    
    def visualize_detections(
        self, 
        frame: np.ndarray, 
        detections: List[Detection],
        show_confidence: bool = True,
        show_class: bool = True
    ) -> np.ndarray:
        """
        Draw detection results on frame
        
        Args:
            frame: Input frame
            detections: List of detections
            show_confidence: Whether to show confidence scores
            show_class: Whether to show class names
            
        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        
        # Color map for different vehicle types
        colors = {
            2: (0, 255, 0),    # car - green
            3: (255, 0, 0),    # motorcycle - blue
            5: (0, 255, 255),  # bus - yellow
            7: (255, 0, 255),  # truck - magenta
        }
        
        for detection in detections:
            x1, y1, x2, y2 = detection.bbox
            color = colors.get(detection.class_id, (128, 128, 128))
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Prepare label
            label_parts = []
            if show_class:
                label_parts.append(detection.class_name)
            if show_confidence:
                label_parts.append(f"{detection.confidence:.2f}")
            
            if label_parts:
                label = " ".join(label_parts)
                
                # Calculate text size
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.6
                thickness = 2
                (text_width, text_height), baseline = cv2.getTextSize(
                    label, font, font_scale, thickness
                )
                
                # Draw label background
                label_y = y1 - 10 if y1 - 10 > text_height else y1 + text_height + 10
                cv2.rectangle(
                    annotated,
                    (x1, label_y - text_height - 5),
                    (x1 + text_width + 5, label_y + 5),
                    color,
                    -1
                )
                
                # Draw label text
                cv2.putText(
                    annotated,
                    label,
                    (x1 + 2, label_y - 2),
                    font,
                    font_scale,
                    (255, 255, 255),
                    thickness
                )
        
        return annotated
    
    def benchmark(self, num_iterations: int = 100) -> Dict[str, Any]:
        """
        Run performance benchmark
        
        Args:
            num_iterations: Number of test iterations
            
        Returns:
            Benchmark results
        """
        logger.info(f"Running benchmark with {num_iterations} iterations...")
        
        # Create dummy input
        dummy_frame = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
        
        results = []
        
        for i in range(num_iterations):
            _, metrics = self.detect(dummy_frame)
            results.append(metrics)
            
            if (i + 1) % 10 == 0:
                logger.info(f"Completed {i + 1}/{num_iterations} iterations")
        
        # Calculate statistics
        inference_times = [r.inference_time_ms for r in results]
        total_times = [r.total_time_ms for r in results]
        fps_values = [r.fps for r in results]
        
        benchmark_results = {
            "iterations": num_iterations,
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
            "target_latency_met": np.mean(total_times) < ml_settings.MAX_LATENCY_MS,
            "target_fps_met": np.mean(fps_values) >= ml_settings.TARGET_FPS
        }
        
        logger.info(f"Benchmark completed:")
        logger.info(f"  Average inference time: {benchmark_results['inference_time_ms']['mean']:.2f}ms")
        logger.info(f"  Average total time: {benchmark_results['total_time_ms']['mean']:.2f}ms")
        logger.info(f"  Average FPS: {benchmark_results['fps']['mean']:.2f}")
        logger.info(f"  Latency target met: {benchmark_results['target_latency_met']}")
        logger.info(f"  FPS target met: {benchmark_results['target_fps_met']}")
        
        return benchmark_results


def create_detector(model_path: Optional[Path] = None) -> YOLOv8VehicleDetector:
    """Factory function to create a YOLOv8 vehicle detector"""
    return YOLOv8VehicleDetector(model_path=model_path)