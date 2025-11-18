#!/bin/bash

# Script mejorado para probar detección con VIDEO5.mp4
# Con análisis detallado de placas y frames clave

VIDEO_PATH="/app/test_videos/VIDEO5.mp4"

echo "🎬 Probando detección de placas con VIDEO5.mp4"
echo "================================================"
echo ""

# Ejecutar test con análisis frame por frame
docker exec -i traffic-inference python - <<'PYTHON'
import cv2
import asyncio
import json
import sys
import numpy as np
from app.services.model_service import ModelService

async def analyze_video():
    print("🔄 Inicializando servicio...")
    service = ModelService()
    await service.initialize()
    
    print("✅ Servicio inicializado con OCR")
    print("")
    
    video_path = "/app/test_videos/VIDEO5.mp4"
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"❌ Error abriendo video: {video_path}")
        sys.exit(1)
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"📹 Video: VIDEO5.mp4")
    print(f"   Total frames: {total_frames}")
    print(f"   FPS: {fps:.2f}")
    print(f"   Resolución: {width}x{height}")
    print(f"   Duración: {total_frames/fps:.1f} segundos")
    print("")
    
    frame_count = 0
    plates_detected = {}  # Dict para acumular placas por frame
    vehicles_detected = 0
    frames_with_vehicles = 0
    ocr_attempts = 0
    
    # Procesar frames estratégicamente
    # - Primeros 50: análisis inicial
    # - Cada 10 frames después: mantener velocidad
    # - Últimos 50: análisis final
    
    print("🔍 ANÁLISIS DETALLADO:")
    print("=" * 80)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Estrategia de muestreo
        should_process = False
        if frame_count <= 50:  # Primeros 50 frames
            should_process = (frame_count % 3 == 0)
        elif frame_count >= total_frames - 50:  # Últimos 50 frames
            should_process = (frame_count % 3 == 0)
        else:  # Frames del medio
            should_process = (frame_count % 10 == 0)
        
        if not should_process:
            continue
        
        # Detectar vehículos con umbral bajo
        detections = await service.detect_vehicles(
            frame=frame,
            confidence_threshold=0.15  # Umbral bajo para capturar más
        )
        
        if detections:
            frames_with_vehicles += 1
            vehicles_detected += len(detections)
            
            print(f"\n📍 Frame {frame_count}/{total_frames} ({frame_count/fps:.1f}s):")
            print(f"   🚗 {len(detections)} vehículo(s) detectado(s)")
            
            # Intentar OCR en cada vehículo
            for idx, det in enumerate(detections):
                vehicle_type = det.get('vehicle_type', 'unknown')
                confidence = det.get('confidence', 0)
                bbox_coords = det.get('bbox', [])
                
                if len(bbox_coords) == 4:
                    x1, y1, x2, y2 = bbox_coords
                    bbox_dict = {
                        'x': int(x1),
                        'y': int(y1),
                        'width': int(x2 - x1),
                        'height': int(y2 - y1)
                    }
                    
                    # Info del vehículo
                    print(f"      [{idx+1}] {vehicle_type} | Conf: {confidence:.2%} | BBox: {bbox_dict['width']}x{bbox_dict['height']}")
                    
                    # Intentar OCR solo si el vehículo es suficientemente grande
                    if bbox_dict['width'] >= 50 and bbox_dict['height'] >= 35:
                        ocr_attempts += 1
                        
                        # OCR
                        plate_result = await service.detect_license_plate(
                            frame=frame,
                            bbox=bbox_dict
                        )
                        
                        if plate_result:
                            plate_text, plate_conf = plate_result
                            print(f"          ✅ PLACA: {plate_text} (conf: {plate_conf:.2%})")
                            
                            # Acumular en dict
                            if plate_text not in plates_detected:
                                plates_detected[plate_text] = {
                                    'first_frame': frame_count,
                                    'last_frame': frame_count,
                                    'count': 1,
                                    'max_confidence': plate_conf,
                                    'vehicle_type': vehicle_type
                                }
                            else:
                                plates_detected[plate_text]['last_frame'] = frame_count
                                plates_detected[plate_text]['count'] += 1
                                if plate_conf > plates_detected[plate_text]['max_confidence']:
                                    plates_detected[plate_text]['max_confidence'] = plate_conf
                        else:
                            print(f"          ❌ Sin placa detectada")
                    else:
                        print(f"          ⏭️  Vehículo muy pequeño para OCR ({bbox_dict['width']}x{bbox_dict['height']})")
        
        # Límite de procesamiento para no tardar demasiado
        if frame_count >= 300 and len(plates_detected) >= 3:
            print(f"\n⏭️  Deteniendo en frame {frame_count} (suficientes placas detectadas)")
            break
    
    cap.release()
    
    print("")
    print("=" * 80)
    print("📊 RESUMEN FINAL")
    print("=" * 80)
    print(f"Frames procesados: {frame_count}")
    print(f"Frames con vehículos: {frames_with_vehicles}")
    print(f"Vehículos detectados: {vehicles_detected}")
    print(f"Intentos de OCR: {ocr_attempts}")
    print(f"Placas únicas detectadas: {len(plates_detected)}")
    print("")
    
    if plates_detected:
        print("🎯 PLACAS ENCONTRADAS:")
        print("-" * 80)
        for plate, info in sorted(plates_detected.items(), key=lambda x: x[1]['max_confidence'], reverse=True):
            start_time = info['first_frame'] / fps
            end_time = info['last_frame'] / fps
            print(f"   📋 {plate:10s} | Apariciones: {info['count']:3d} | "
                  f"Confianza máx: {info['max_confidence']:.2%} | "
                  f"Frames: {info['first_frame']}-{info['last_frame']} ({start_time:.1f}s-{end_time:.1f}s)")
        print("")
        print(f"✅ ÉXITO: Se detectaron {len(plates_detected)} placa(s) en el video")
    else:
        print("⚠️  NO SE DETECTARON PLACAS")
        print("")
        print("💡 Posibles causas:")
        print("   1. El video no tiene vehículos con placas visibles")
        print("   2. Las placas están muy borrosas o pequeñas")
        print("   3. El ángulo de la cámara no permite ver las placas")
        print("   4. La iluminación es insuficiente")
        print("")
        print("💡 Sugerencias:")
        print("   1. Verifica manualmente el video en el frame indicado")
        print("   2. Prueba con otro video de mejor calidad")
        print("   3. Reduce skip_frames para procesar más frames")
        print("   4. Ajusta el ángulo de la cámara para capturar placas frontales/traseras")

# Ejecutar
asyncio.run(analyze_video())
PYTHON

echo ""
echo "✅ Análisis completado"
echo ""
echo "💡 Para ver el video manualmente:"
echo "   docker exec -it traffic-inference ls -lh /app/test_videos/VIDEO5.mp4"
