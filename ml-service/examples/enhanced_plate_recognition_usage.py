"""
Example usage of enhanced plate recognition pipeline.

This script demonstrates how to use the complete plate recognition system
for traffic infraction detection.
"""

import cv2
import numpy as np
from pathlib import Path
import logging
import argparse
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import pipeline
from ml_service.src.recognition.plate_recognition_pipeline import (
    PlateRecognitionPipeline,
    PlateRecognitionResult
)


def process_video_file(
    video_path: str,
    output_path: str = None,
    save_annotations: bool = True,
    use_trocr: bool = True,
    gpu: bool = True
):
    """
    Process video file for plate recognition.
    
    Args:
        video_path: Path to input video
        output_path: Path to save annotated video
        save_annotations: Whether to save annotated video
        use_trocr: Use TrOCR in addition to EasyOCR
        gpu: Enable GPU acceleration
    """
    logger.info("=" * 80)
    logger.info("ENHANCED PLATE RECOGNITION SYSTEM")
    logger.info("=" * 80)
    
    # Initialize pipeline
    logger.info("Initializing pipeline...")
    pipeline = PlateRecognitionPipeline(
        use_trocr=use_trocr,
        gpu=gpu,
        confidence_threshold=0.5
    )
    
    # Process video
    logger.info(f"Processing video: {video_path}")
    results = pipeline.process_video(
        video_path=video_path,
        output_path=output_path,
        save_annotations=save_annotations
    )
    
    # Display results
    logger.info("\n" + "=" * 80)
    logger.info("RECOGNITION RESULTS")
    logger.info("=" * 80)
    
    unique_plates = {}
    for result in results:
        plate = result.plate_text
        if plate not in unique_plates or result.plate_confidence > unique_plates[plate].plate_confidence:
            unique_plates[plate] = result
    
    logger.info(f"\nTotal detections: {len(results)}")
    logger.info(f"Unique plates: {len(unique_plates)}")
    logger.info("\nDetected Plates:")
    logger.info("-" * 80)
    
    for plate, result in sorted(unique_plates.items()):
        logger.info(
            f"  {plate:12} | Track: {result.track_id:3} | "
            f"Vehicle: {result.vehicle_class:10} | "
            f"Confidence: {result.plate_confidence:.2f} | "
            f"Frame: {result.frame_number}"
        )
    
    # Display statistics
    logger.info("\n" + "=" * 80)
    logger.info("PIPELINE STATISTICS")
    logger.info("=" * 80)
    
    stats = pipeline.get_stats()
    logger.info(f"\nFrames processed: {stats['frames_processed']}")
    logger.info(f"Vehicles detected: {stats['total_vehicles_detected']}")
    logger.info(f"Plates recognized: {stats['total_plates_recognized']}")
    logger.info(f"Average FPS: {stats['avg_fps']:.2f}")
    logger.info(f"Average processing time: {stats['avg_processing_time_ms']:.1f} ms")
    
    # Component statistics
    logger.info("\nComponent Performance:")
    logger.info(f"  Vehicle Detector: {stats['vehicle_detector_stats']['avg_fps']:.2f} FPS")
    logger.info(f"  Plate Segmenter: {stats['plate_segmenter_stats']['avg_fps']:.2f} FPS")
    logger.info(f"  Text Extractor: {stats['text_extractor_stats']['success_rate']:.2%} success rate")
    logger.info(f"  Tracker: {stats['tracker_stats']['total_tracks_created']} tracks created")
    
    # Save results to JSON
    output_json = Path(video_path).stem + '_results.json'
    save_results_to_json(list(unique_plates.values()), output_json)
    logger.info(f"\nResults saved to: {output_json}")
    
    return results


def process_rtsp_stream(
    rtsp_url: str,
    duration: int = 60,
    use_trocr: bool = True,
    gpu: bool = True
):
    """
    Process RTSP stream for plate recognition.
    
    Args:
        rtsp_url: RTSP stream URL
        duration: Duration to process (seconds)
        use_trocr: Use TrOCR in addition to EasyOCR
        gpu: Enable GPU acceleration
    """
    logger.info("Processing RTSP stream...")
    
    # Initialize pipeline
    pipeline = PlateRecognitionPipeline(
        use_trocr=use_trocr,
        gpu=gpu,
        confidence_threshold=0.5
    )
    
    # Open stream
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        logger.error(f"Failed to open stream: {rtsp_url}")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    max_frames = int(fps * duration)
    
    logger.info(f"Stream opened: {fps} FPS, processing for {duration}s ({max_frames} frames)")
    
    frame_count = 0
    all_results = []
    
    try:
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            results = pipeline.process_frame(frame)
            all_results.extend(results)
            
            # Display frame with annotations
            if results:
                annotated = pipeline._annotate_frame(frame, results)
                cv2.imshow('Plate Recognition', annotated)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            frame_count += 1
            
            if frame_count % 30 == 0:
                logger.info(f"Processed {frame_count}/{max_frames} frames...")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    # Display results
    logger.info(f"\nProcessed {frame_count} frames, {len(all_results)} plates detected")
    
    stats = pipeline.get_stats()
    logger.info(f"Average FPS: {stats['avg_fps']:.2f}")
    
    return all_results


def process_single_image(
    image_path: str,
    output_path: str = None,
    use_trocr: bool = True,
    gpu: bool = True
):
    """
    Process single image for plate recognition.
    
    Args:
        image_path: Path to input image
        output_path: Path to save annotated image
        use_trocr: Use TrOCR in addition to EasyOCR
        gpu: Enable GPU acceleration
    """
    logger.info(f"Processing image: {image_path}")
    
    # Initialize pipeline
    pipeline = PlateRecognitionPipeline(
        use_trocr=use_trocr,
        gpu=gpu,
        confidence_threshold=0.5
    )
    
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        logger.error(f"Failed to load image: {image_path}")
        return None
    
    # Process frame
    results = pipeline.process_frame(image)
    
    # Display results
    logger.info(f"\nDetected {len(results)} plates:")
    for result in results:
        logger.info(
            f"  {result.plate_text} | "
            f"Confidence: {result.plate_confidence:.2f} | "
            f"Vehicle: {result.vehicle_class}"
        )
    
    # Save annotated image
    if output_path and results:
        annotated = pipeline._annotate_frame(image, results)
        cv2.imwrite(output_path, annotated)
        logger.info(f"Annotated image saved to: {output_path}")
    
    return results


def save_results_to_json(results: list, output_path: str):
    """Save results to JSON file."""
    data = []
    for result in results:
        data.append({
            'track_id': result.track_id,
            'plate_text': result.plate_text,
            'plate_confidence': float(result.plate_confidence),
            'vehicle_class': result.vehicle_class,
            'detection_confidence': float(result.detection_confidence),
            'frame_number': result.frame_number,
            'timestamp': float(result.timestamp),
            'vehicle_bbox': list(result.vehicle_bbox),
            'plate_bbox': list(result.plate_bbox),
            'speed': float(result.speed) if result.speed else None
        })
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Enhanced Plate Recognition System for Traffic Infractions'
    )
    parser.add_argument('--video', type=str, help='Path to video file')
    parser.add_argument('--image', type=str, help='Path to image file')
    parser.add_argument('--rtsp', type=str, help='RTSP stream URL')
    parser.add_argument('--output', type=str, help='Output path')
    parser.add_argument('--duration', type=int, default=60, help='Duration for RTSP (seconds)')
    parser.add_argument('--no-trocr', action='store_true', help='Disable TrOCR')
    parser.add_argument('--cpu', action='store_true', help='Use CPU only')
    
    args = parser.parse_args()
    
    use_trocr = not args.no_trocr
    gpu = not args.cpu
    
    if args.video:
        process_video_file(
            video_path=args.video,
            output_path=args.output,
            save_annotations=True,
            use_trocr=use_trocr,
            gpu=gpu
        )
    elif args.image:
        process_single_image(
            image_path=args.image,
            output_path=args.output,
            use_trocr=use_trocr,
            gpu=gpu
        )
    elif args.rtsp:
        process_rtsp_stream(
            rtsp_url=args.rtsp,
            duration=args.duration,
            use_trocr=use_trocr,
            gpu=gpu
        )
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
