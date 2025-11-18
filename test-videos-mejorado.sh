#!/bin/bash

# Script para probar detección mejorada de placas con VIDEO1, VIDEO2 y VIDEO5
# Con detección de píxeles blancos y ROI optimizado

echo "🎬 Probando detección MEJORADA de placas"
echo "=========================================="
echo ""
echo "✅ Mejoras implementadas:"
echo "   - Detección de píxeles blancos (placas blancas)"
echo "   - ROI (Region of Interest) enfocado"
echo "   - Canvas verde eliminado del frontend"
echo "   - Múltiples versiones de imagen para OCR"
echo ""

for VIDEO in VIDEO1.mp4 VIDEO2.mp4 VIDEO5.mp4; do
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📹 Procesando: $VIDEO"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    docker exec -i traffic-inference python - <<PYTHON
import cv2
import asyncio
import sys
import numpy as np
from app.services.model_service import ModelService

async def analyze_video():
    print("")
    print("🔄 Inicializando servicio...")
    service = ModelService()
    await service.initialize()
    
    print("✅ Servicio inicializado")
    print("")
    
    video_path = "/app/test_videos/$VIDEO"
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"❌ Error abriendo video: {video_path}")
        sys.exit(1)
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"📹 Video: $VIDEO")
    print(f"   Resolución: {width}x{height}")
    print(f"   Frames: {total_frames} ({total_frames/fps:.1f}s)")
    print("")
    
    # 🎯 ROI - Procesar solo la zona donde aparecen placas
    roi_x = int(width * 0.15)
    roi_y = int(height * 0.35)
    roi_w = int(width * 0.7)
    roi_h = int(height * 0.55)
    
    print(f"🎯 ROI configurado: x={roi_x}, y={roi_y}, w={roi_w}, h={roi_h}")
    print("")
    
    frame_count = 0
    plates_detected = {}
    vehicles_detected = 0
    
    print("🔍 PROCESANDO FRAMES (cada 5 frames):")
    print("─" * 80)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Procesar cada 5 frames
        if frame_count % 5 != 0:
            continue
        
        # Aplicar ROI al frame
        roi_frame = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
        
        # Detectar vehículos en ROI
        detections = await service.detect_vehicles(
            frame=roi_frame,
            confidence_threshold=0.15
        )
        
        if detections:
            vehicles_detected += len(detections)
            
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
                    
                    # Solo intentar OCR si vehículo es grande
                    if bbox_dict['width'] >= 50 and bbox_dict['height'] >= 35:
                        # OCR con detección de píxeles blancos
                        plate_result = await service.detect_license_plate(
                            frame=roi_frame,
                            bbox=bbox_dict
                        )
                        
                        if plate_result:
                            plate_text, plate_conf = plate_result
                            print(f"Frame {frame_count:4d} | ✅ PLACA: {plate_text:10s} | Conf: {plate_conf:.2%} | {vehicle_type}")
                            
                            # Acumular
                            if plate_text not in plates_detected:
                                plates_detected[plate_text] = {
                                    'frame': frame_count,
                                    'confidence': plate_conf,
                                    'type': vehicle_type
                                }
                            else:
                                if plate_conf > plates_detected[plate_text]['confidence']:
                                    plates_detected[plate_text]['confidence'] = plate_conf
        
        # Límite: 100 frames o 3 placas
        if frame_count >= 100 or len(plates_detected) >= 3:
            break
    
    cap.release()
    
    print("─" * 80)
    print("")
    print("📊 RESUMEN:")
    print(f"   Frames procesados: {frame_count}")
    print(f"   Vehículos detectados: {vehicles_detected}")
    print(f"   Placas detectadas: {len(plates_detected)}")
    print("")
    
    if plates_detected:
        print("🎯 PLACAS ENCONTRADAS:")
        for plate, info in sorted(plates_detected.items(), key=lambda x: x[1]['confidence'], reverse=True):
            print(f"   📋 {plate:10s} | Conf: {info['confidence']:.2%} | Frame: {info['frame']:4d} | {info['type']}")
    else:
        print("⚠️  NO SE DETECTARON PLACAS")
        print("")
        print("💡 Posibles causas:")
        print("   - Video sin placas visibles")
        print("   - Placas muy pequeñas o borrosas")
        print("   - Ángulo de cámara no adecuado")

asyncio.run(analyze_video())
PYTHON

    echo ""
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Análisis completado"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Para probar en el frontend:"
echo "   1. Recarga http://localhost:3000"
echo "   2. Sube VIDEO1, VIDEO2 o VIDEO5"
echo "   3. Verifica que NO aparezca el canvas verde"
echo "   4. Verifica los logs en consola"
