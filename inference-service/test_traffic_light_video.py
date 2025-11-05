#!/usr/bin/env python3
"""
Script para probar detección de semáforos con YOLO en un video
Uso: python3 test_traffic_light_video.py <ruta_al_video.mp4>
"""

import sys
import cv2
import numpy as np
from ultralytics import YOLO
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_traffic_light_detection(video_path: str):
    """Probar detección de semáforos en un video"""
    
    # Cargar modelo YOLO
    logger.info("🔄 Cargando modelo YOLOv8n...")
    model = YOLO('yolov8n.pt')
    
    # Verificar que la clase 'traffic light' existe
    logger.info(f"📋 Clases disponibles en YOLO: {len(model.names)}")
    logger.info(f"🚦 Clase 9 (traffic light): {model.names.get(9, 'NO ENCONTRADA')}")
    
    # Abrir video
    logger.info(f"📹 Abriendo video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        logger.error(f"❌ No se pudo abrir el video: {video_path}")
        return
    
    # Obtener info del video
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    logger.info(f"📊 Video info: {width}x{height}, {fps} FPS, {total_frames} frames")
    
    frame_count = 0
    traffic_light_frames = []
    all_detections_summary = {}
    
    # Procesar video
    logger.info("🎬 Procesando video...")
    logger.info("   (Procesando 1 de cada 10 frames para velocidad)")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Solo procesar 1 de cada 10 frames para velocidad
        if frame_count % 10 != 0:
            continue
        
        # Ejecutar YOLO con diferentes configuraciones
        results = model(frame, verbose=False, imgsz=640, conf=0.15)  # Umbral muy bajo
        
        # Analizar detecciones
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                cls_id = int(box.cls[0])
                class_name = result.names[cls_id]
                confidence = float(box.conf[0])
                
                # Contar todas las clases detectadas
                if class_name not in all_detections_summary:
                    all_detections_summary[class_name] = {
                        'count': 0,
                        'max_conf': 0.0,
                        'frames': []
                    }
                
                all_detections_summary[class_name]['count'] += 1
                all_detections_summary[class_name]['max_conf'] = max(
                    all_detections_summary[class_name]['max_conf'],
                    confidence
                )
                if frame_count not in all_detections_summary[class_name]['frames']:
                    all_detections_summary[class_name]['frames'].append(frame_count)
                
                # Buscar semáforos específicamente
                if class_name == 'traffic light':
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    bbox_width = x2 - x1
                    bbox_height = y2 - y1
                    
                    traffic_light_frames.append({
                        'frame': frame_count,
                        'bbox': (int(x1), int(y1), int(x2), int(y2)),
                        'size': (int(bbox_width), int(bbox_height)),
                        'confidence': confidence
                    })
                    
                    logger.info(f"🚦 Frame {frame_count}: Traffic light detectado! "
                              f"bbox=({x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f}) "
                              f"size={bbox_width:.0f}x{bbox_height:.0f} "
                              f"conf={confidence:.3f}")
        
        # Mostrar progreso cada 100 frames
        if frame_count % 100 == 0:
            progress = (frame_count / total_frames) * 100
            logger.info(f"⏳ Progreso: {frame_count}/{total_frames} ({progress:.1f}%)")
    
    cap.release()
    
    # Mostrar resumen
    logger.info("\n" + "="*70)
    logger.info("📊 RESUMEN DE DETECCIONES")
    logger.info("="*70)
    
    logger.info(f"\n🎬 Frames procesados: {frame_count // 10} de {total_frames}")
    
    if len(traffic_light_frames) > 0:
        logger.info(f"\n✅ SEMÁFOROS DETECTADOS: {len(traffic_light_frames)} detecciones en {len(set([d['frame'] for d in traffic_light_frames]))} frames diferentes")
        logger.info("\n📍 Detecciones de semáforos:")
        for detection in traffic_light_frames[:10]:  # Mostrar primeras 10
            logger.info(f"   Frame {detection['frame']:5d}: "
                       f"bbox={detection['bbox']} "
                       f"size={detection['size'][0]}x{detection['size'][1]}px "
                       f"conf={detection['confidence']:.3f}")
        if len(traffic_light_frames) > 10:
            logger.info(f"   ... y {len(traffic_light_frames) - 10} más")
    else:
        logger.error("\n❌ NO SE DETECTARON SEMÁFOROS EN EL VIDEO")
        logger.info("\n💡 Posibles razones:")
        logger.info("   1. Los semáforos son muy pequeños (< 15x15 píxeles)")
        logger.info("   2. Los semáforos están muy borrosos o mal iluminados")
        logger.info("   3. El ángulo de la cámara no es óptimo")
        logger.info("   4. El modelo YOLO estándar no reconoce ese tipo de semáforo")
    
    # Mostrar todas las clases detectadas
    logger.info(f"\n📋 TODAS LAS CLASES DETECTADAS EN EL VIDEO:")
    sorted_classes = sorted(all_detections_summary.items(), 
                           key=lambda x: x[1]['count'], 
                           reverse=True)
    
    for class_name, stats in sorted_classes[:15]:  # Top 15
        frames_with_class = len(stats['frames'])
        logger.info(f"   {class_name:15s}: {stats['count']:4d} detecciones, "
                   f"{frames_with_class:3d} frames, "
                   f"max_conf={stats['max_conf']:.3f}")
    
    if len(sorted_classes) > 15:
        logger.info(f"   ... y {len(sorted_classes) - 15} clases más")
    
    # Recomendaciones
    logger.info("\n" + "="*70)
    logger.info("💡 RECOMENDACIONES")
    logger.info("="*70)
    
    if len(traffic_light_frames) == 0:
        logger.info("\n🔍 Sugerencias para mejorar la detección:")
        logger.info("   1. Usa un video donde los semáforos sean más grandes (> 30x30 px)")
        logger.info("   2. Asegúrate de que los semáforos estén enfocados")
        logger.info("   3. Prueba con un video de día con buena iluminación")
        logger.info("   4. Los semáforos deben ser de estilo estándar (no señales raras)")
        logger.info("   5. Considera usar un modelo YOLO personalizado entrenado con tus semáforos")
    else:
        avg_size = np.mean([d['size'][0] * d['size'][1] for d in traffic_light_frames])
        avg_conf = np.mean([d['confidence'] for d in traffic_light_frames])
        
        logger.info(f"\n✅ Detección exitosa!")
        logger.info(f"   Tamaño promedio: {avg_size:.0f} px²")
        logger.info(f"   Confianza promedio: {avg_conf:.3f}")
        
        if avg_size < 900:  # < 30x30
            logger.info("   ⚠️ Los semáforos son pequeños, considera aumentar la resolución")
        if avg_conf < 0.3:
            logger.info("   ⚠️ Confianza baja, puede haber falsos positivos")
    
    logger.info("\n" + "="*70 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 test_traffic_light_video.py <ruta_al_video.mp4>")
        print("\nEjemplo:")
        print("  python3 test_traffic_light_video.py /mnt/c/Users/usuario/Videos/semaforo.mp4")
        sys.exit(1)
    
    video_path = sys.argv[1]
    test_traffic_light_detection(video_path)
