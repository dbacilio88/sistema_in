#!/usr/bin/env python3
"""
Benchmark for license plate recognition system.

This script tests OCR performance, accuracy, and speed
with various plate images and conditions.
"""

import argparse
import logging
import time
import numpy as np
import cv2
from pathlib import Path
import json
import sys
import os
from typing import List, Dict, Any, Tuple
import statistics

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from recognition.plate_detector import LicensePlateDetector
from recognition.plate_reader import LicensePlateReader
from recognition.plate_validator import PeruvianPlateValidator, PlateFormat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PlateRecognitionBenchmark:
    """
    Comprehensive benchmark for license plate recognition.
    
    Tests detection, OCR, and validation performance with various conditions.
    """
    
    def __init__(self):
        """Initialize benchmark components."""
        self.detector = LicensePlateDetector(use_cascade=True)
        self.reader = LicensePlateReader(languages=['en'])
        self.validator = PeruvianPlateValidator()
        
        # Test data
        self.test_plates = [
            # Valid Peruvian plates
            "ABC123", "ABC1234", "XYZ789", "XYZ9876",
            "T1A123", "T2B456", "A1123", "B2456",
            "PNP123", "CD456", "TP789", "AB1234"
        ]
        
        self.invalid_plates = [
            "WTF123", "ASS456", "12345", "ABCDEF",
            "A", "123", "ABC", "TOOLONG123"
        ]
        
        logger.info("PlateRecognitionBenchmark initialized")
    
    def generate_synthetic_plate_images(self, count: int = 100) -> List[Tuple[np.ndarray, str]]:
        """
        Generate synthetic license plate images for testing.
        
        Args:
            count: Number of images to generate
            
        Returns:
            List of (image, ground_truth_text) tuples
        """
        logger.info(f"Generating {count} synthetic plate images")
        
        images = []
        
        for i in range(count):
            # Select random plate text
            plate_text = np.random.choice(self.test_plates)
            
            # Create plate image
            plate_img = self._create_synthetic_plate(plate_text)
            
            # Add random transformations and noise
            transformed = self._apply_transformations(plate_img)
            
            images.append((transformed, plate_text))
        
        return images
    
    def _create_synthetic_plate(self, text: str) -> np.ndarray:
        """Create synthetic license plate image."""
        # Plate dimensions (Peruvian standard approx 520x110mm)
        width, height = 300, 60
        
        # Create white background
        plate = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        # Add border
        cv2.rectangle(plate, (2, 2), (width-3, height-3), (0, 0, 0), 2)
        
        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.5
        thickness = 3
        
        # Calculate text size and position
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
        x = (width - text_width) // 2
        y = (height + text_height) // 2
        
        # Add dash if needed
        display_text = text
        if len(text) == 6 and text[:3].isalpha() and text[3:].isdigit():
            display_text = text[:3] + "-" + text[3:]
        elif len(text) == 7 and text[:3].isalpha() and text[3:].isdigit():
            display_text = text[:3] + "-" + text[3:]
        
        cv2.putText(plate, display_text, (x, y), font, font_scale, (0, 0, 0), thickness)
        
        return plate
    
    def _apply_transformations(self, image: np.ndarray) -> np.ndarray:
        """Apply random transformations to simulate real conditions."""
        result = image.copy()
        
        # Random rotation (-15 to +15 degrees)
        angle = np.random.uniform(-15, 15)
        center = (result.shape[1] // 2, result.shape[0] // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        result = cv2.warpAffine(result, M, (result.shape[1], result.shape[0]), 
                               borderValue=(128, 128, 128))
        
        # Random perspective transform
        h, w = result.shape[:2]
        src_points = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        
        # Add random perspective distortion
        offset = 10
        dst_points = np.float32([
            [np.random.randint(0, offset), np.random.randint(0, offset)],
            [w - np.random.randint(0, offset), np.random.randint(0, offset)],
            [w - np.random.randint(0, offset), h - np.random.randint(0, offset)],
            [np.random.randint(0, offset), h - np.random.randint(0, offset)]
        ])
        
        M = cv2.getPerspectiveTransform(src_points, dst_points)
        result = cv2.warpPerspective(result, M, (w, h), borderValue=(128, 128, 128))
        
        # Random noise
        noise = np.random.normal(0, 10, result.shape).astype(np.uint8)
        result = cv2.add(result, noise)
        
        # Random blur
        if np.random.random() > 0.5:
            kernel_size = np.random.choice([3, 5])
            result = cv2.GaussianBlur(result, (kernel_size, kernel_size), 0)
        
        # Random brightness/contrast
        alpha = np.random.uniform(0.7, 1.3)  # Contrast
        beta = np.random.randint(-30, 30)    # Brightness
        result = cv2.convertScaleAbs(result, alpha=alpha, beta=beta)
        
        return result
    
    def benchmark_detection_accuracy(self, test_images: List[Tuple[np.ndarray, str]]) -> Dict[str, Any]:
        """Benchmark detection accuracy."""
        logger.info("Running detection accuracy benchmark")
        
        total_images = len(test_images)
        detected_count = 0
        detection_times = []
        confidence_scores = []
        
        for i, (image, ground_truth) in enumerate(test_images):
            start_time = time.time()
            
            # Run detection
            detections = self.detector.detect_plates(image)
            
            detection_time = time.time() - start_time
            detection_times.append(detection_time)
            
            if detections:
                detected_count += 1
                confidence_scores.append(max(d.confidence for d in detections))
            
            if i % 20 == 0:
                logger.info(f"Processed {i}/{total_images} images")
        
        detection_rate = detected_count / total_images
        avg_detection_time = statistics.mean(detection_times)
        avg_confidence = statistics.mean(confidence_scores) if confidence_scores else 0.0
        
        results = {
            "test_name": "detection_accuracy",
            "total_images": total_images,
            "detected_count": detected_count,
            "detection_rate": detection_rate,
            "avg_detection_time_ms": avg_detection_time * 1000,
            "avg_confidence": avg_confidence,
            "detection_times_ms": [t * 1000 for t in detection_times]
        }
        
        logger.info(f"Detection Results:")
        logger.info(f"  Detection rate: {detection_rate:.2%}")
        logger.info(f"  Average time: {avg_detection_time*1000:.2f}ms")
        logger.info(f"  Average confidence: {avg_confidence:.3f}")
        
        return results
    
    def benchmark_ocr_accuracy(self, test_images: List[Tuple[np.ndarray, str]]) -> Dict[str, Any]:
        """Benchmark OCR accuracy."""
        logger.info("Running OCR accuracy benchmark")
        
        total_plates = 0
        correct_readings = 0
        partial_matches = 0
        ocr_times = []
        confidence_scores = []
        
        for i, (image, ground_truth) in enumerate(test_images):
            # First detect plates
            detections = self.detector.detect_plates(image)
            
            for detection in detections:
                total_plates += 1
                
                start_time = time.time()
                
                # Run OCR
                reading = self.reader.read_plate(detection.plate_image)
                
                ocr_time = time.time() - start_time
                ocr_times.append(ocr_time)
                confidence_scores.append(reading.confidence)
                
                # Check accuracy
                predicted = reading.plate_text.replace('-', '').upper()
                actual = ground_truth.replace('-', '').upper()
                
                if predicted == actual:
                    correct_readings += 1
                elif self._is_partial_match(predicted, actual):
                    partial_matches += 1
            
            if i % 20 == 0:
                logger.info(f"Processed {i}/{len(test_images)} images")
        
        if total_plates == 0:
            return {"error": "No plates detected for OCR testing"}
        
        accuracy = correct_readings / total_plates
        partial_accuracy = (correct_readings + partial_matches) / total_plates
        avg_ocr_time = statistics.mean(ocr_times)
        avg_confidence = statistics.mean(confidence_scores)
        
        results = {
            "test_name": "ocr_accuracy",
            "total_plates": total_plates,
            "correct_readings": correct_readings,
            "partial_matches": partial_matches,
            "accuracy": accuracy,
            "partial_accuracy": partial_accuracy,
            "avg_ocr_time_ms": avg_ocr_time * 1000,
            "avg_confidence": avg_confidence,
            "ocr_times_ms": [t * 1000 for t in ocr_times]
        }
        
        logger.info(f"OCR Results:")
        logger.info(f"  Exact accuracy: {accuracy:.2%}")
        logger.info(f"  Partial accuracy: {partial_accuracy:.2%}")
        logger.info(f"  Average time: {avg_ocr_time*1000:.2f}ms")
        logger.info(f"  Average confidence: {avg_confidence:.3f}")
        
        return results
    
    def benchmark_validation_accuracy(self) -> Dict[str, Any]:
        """Benchmark validation accuracy."""
        logger.info("Running validation accuracy benchmark")
        
        # Test valid plates
        valid_correct = 0
        for plate in self.test_plates:
            result = self.validator.validate(plate)
            if result.is_valid:
                valid_correct += 1
        
        # Test invalid plates
        invalid_correct = 0
        for plate in self.invalid_plates:
            result = self.validator.validate(plate)
            if not result.is_valid:
                invalid_correct += 1
        
        total_valid = len(self.test_plates)
        total_invalid = len(self.invalid_plates)
        
        valid_accuracy = valid_correct / total_valid
        invalid_accuracy = invalid_correct / total_invalid
        overall_accuracy = (valid_correct + invalid_correct) / (total_valid + total_invalid)
        
        results = {
            "test_name": "validation_accuracy",
            "valid_plates_tested": total_valid,
            "valid_plates_correct": valid_correct,
            "valid_accuracy": valid_accuracy,
            "invalid_plates_tested": total_invalid,
            "invalid_plates_correct": invalid_correct,
            "invalid_accuracy": invalid_accuracy,
            "overall_accuracy": overall_accuracy
        }
        
        logger.info(f"Validation Results:")
        logger.info(f"  Valid plate accuracy: {valid_accuracy:.2%}")
        logger.info(f"  Invalid plate accuracy: {invalid_accuracy:.2%}")
        logger.info(f"  Overall accuracy: {overall_accuracy:.2%}")
        
        return results
    
    def benchmark_end_to_end_performance(self, test_images: List[Tuple[np.ndarray, str]]) -> Dict[str, Any]:
        """Benchmark complete pipeline performance."""
        logger.info("Running end-to-end performance benchmark")
        
        total_images = len(test_images)
        successful_pipeline = 0
        pipeline_times = []
        valid_plates_found = 0
        
        for i, (image, ground_truth) in enumerate(test_images):
            start_time = time.time()
            
            # Full pipeline
            detections = self.detector.detect_plates(image)
            
            if detections:
                for detection in detections:
                    reading = self.reader.read_plate(detection.plate_image)
                    validation = self.validator.validate(reading.plate_text)
                    
                    if validation.is_valid:
                        valid_plates_found += 1
                        
                        # Check if reading matches ground truth
                        if self._normalize_plate_text(reading.plate_text) == self._normalize_plate_text(ground_truth):
                            successful_pipeline += 1
                        break
            
            pipeline_time = time.time() - start_time
            pipeline_times.append(pipeline_time)
            
            if i % 20 == 0:
                logger.info(f"Processed {i}/{total_images} images")
        
        success_rate = successful_pipeline / total_images
        valid_rate = valid_plates_found / total_images
        avg_pipeline_time = statistics.mean(pipeline_times)
        fps = 1.0 / avg_pipeline_time
        
        results = {
            "test_name": "end_to_end_performance",
            "total_images": total_images,
            "successful_pipeline": successful_pipeline,
            "valid_plates_found": valid_plates_found,
            "success_rate": success_rate,
            "valid_plate_rate": valid_rate,
            "avg_pipeline_time_ms": avg_pipeline_time * 1000,
            "fps": fps,
            "pipeline_times_ms": [t * 1000 for t in pipeline_times]
        }
        
        logger.info(f"End-to-End Results:")
        logger.info(f"  Success rate: {success_rate:.2%}")
        logger.info(f"  Valid plate rate: {valid_rate:.2%}")
        logger.info(f"  Average time: {avg_pipeline_time*1000:.2f}ms")
        logger.info(f"  FPS: {fps:.1f}")
        
        return results
    
    def _is_partial_match(self, predicted: str, actual: str) -> bool:
        """Check if predicted text is a partial match."""
        if not predicted or not actual:
            return False
        
        # Check character-level similarity
        matches = sum(1 for p, a in zip(predicted, actual) if p == a)
        similarity = matches / max(len(predicted), len(actual))
        
        return similarity >= 0.7  # 70% character match threshold
    
    def _normalize_plate_text(self, text: str) -> str:
        """Normalize plate text for comparison."""
        return text.upper().replace('-', '').replace(' ', '')
    
    def run_all_benchmarks(self, image_count: int = 100) -> Dict[str, Any]:
        """Run all benchmark tests."""
        logger.info(f"Starting comprehensive plate recognition benchmarks with {image_count} images")
        
        # Generate test images
        test_images = self.generate_synthetic_plate_images(image_count)
        
        all_results = {
            "timestamp": time.time(),
            "test_image_count": image_count,
            "benchmarks": {}
        }
        
        # Detection benchmark
        try:
            detection_results = self.benchmark_detection_accuracy(test_images)
            all_results["benchmarks"]["detection"] = detection_results
        except Exception as e:
            logger.error(f"Detection benchmark failed: {e}")
            all_results["benchmarks"]["detection"] = {"error": str(e)}
        
        # OCR benchmark
        try:
            ocr_results = self.benchmark_ocr_accuracy(test_images)
            all_results["benchmarks"]["ocr"] = ocr_results
        except Exception as e:
            logger.error(f"OCR benchmark failed: {e}")
            all_results["benchmarks"]["ocr"] = {"error": str(e)}
        
        # Validation benchmark
        try:
            validation_results = self.benchmark_validation_accuracy()
            all_results["benchmarks"]["validation"] = validation_results
        except Exception as e:
            logger.error(f"Validation benchmark failed: {e}")
            all_results["benchmarks"]["validation"] = {"error": str(e)}
        
        # End-to-end benchmark
        try:
            e2e_results = self.benchmark_end_to_end_performance(test_images)
            all_results["benchmarks"]["end_to_end"] = e2e_results
        except Exception as e:
            logger.error(f"End-to-end benchmark failed: {e}")
            all_results["benchmarks"]["end_to_end"] = {"error": str(e)}
        
        return all_results
    
    def save_results(self, results: Dict[str, Any], output_file: str):
        """Save benchmark results to JSON file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to {output_path}")
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable report."""
        report = ["# License Plate Recognition Benchmark Report", ""]
        report.append(f"**Timestamp**: {time.ctime(results['timestamp'])}")
        report.append(f"**Test Images**: {results['test_image_count']}")
        report.append("")
        
        for benchmark_name, benchmark_results in results["benchmarks"].items():
            if "error" in benchmark_results:
                report.append(f"## {benchmark_name.title()} Benchmark")
                report.append(f"**ERROR**: {benchmark_results['error']}")
                report.append("")
                continue
            
            report.append(f"## {benchmark_name.title()} Benchmark")
            
            if benchmark_name == "detection":
                report.append(f"- **Detection Rate**: {benchmark_results['detection_rate']:.2%}")
                report.append(f"- **Average Time**: {benchmark_results['avg_detection_time_ms']:.2f}ms")
                report.append(f"- **Average Confidence**: {benchmark_results['avg_confidence']:.3f}")
                
            elif benchmark_name == "ocr":
                report.append(f"- **Exact Accuracy**: {benchmark_results['accuracy']:.2%}")
                report.append(f"- **Partial Accuracy**: {benchmark_results['partial_accuracy']:.2%}")
                report.append(f"- **Average Time**: {benchmark_results['avg_ocr_time_ms']:.2f}ms")
                
            elif benchmark_name == "validation":
                report.append(f"- **Overall Accuracy**: {benchmark_results['overall_accuracy']:.2%}")
                report.append(f"- **Valid Plate Accuracy**: {benchmark_results['valid_accuracy']:.2%}")
                report.append(f"- **Invalid Plate Accuracy**: {benchmark_results['invalid_accuracy']:.2%}")
                
            elif benchmark_name == "end_to_end":
                report.append(f"- **Success Rate**: {benchmark_results['success_rate']:.2%}")
                report.append(f"- **Average Time**: {benchmark_results['avg_pipeline_time_ms']:.2f}ms")
                report.append(f"- **FPS**: {benchmark_results['fps']:.1f}")
            
            report.append("")
        
        return "\n".join(report)

def main():
    """Main benchmark execution."""
    parser = argparse.ArgumentParser(description="License Plate Recognition Benchmark")
    parser.add_argument("--images", type=int, default=100, help="Number of test images")
    parser.add_argument("--output", type=str, default="plate_recognition_benchmark.json",
                       help="Output file for results")
    parser.add_argument("--report", type=str, default="plate_recognition_report.md",
                       help="Output file for report")
    
    args = parser.parse_args()
    
    # Create benchmark instance
    benchmark = PlateRecognitionBenchmark()
    
    # Run benchmarks
    results = benchmark.run_all_benchmarks(args.images)
    
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