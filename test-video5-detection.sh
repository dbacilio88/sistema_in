#!/bin/bash

# Script para probar detección con VIDEO5.mp4

VIDEO_PATH="/app/test_videos/VIDEO5.mp4"
CONFIG_FILE="/tmp/test_config.json"

echo "🎬 Probando detección de placas con VIDEO5.mp4"
echo "=============================================="

# Crear configuración de prueba
cat > "$CONFIG_FILE" << 'EOF'
{
  "confidence_threshold": 0.15,
  "enable_ocr": true,
  "simulate_infractions": true,
  "infractions": ["speeding", "red_light"],
  "speed_limit": 60,
  "enable_traffic_light": true,
  "stop_line_y": 120,
  "yolo_confidence_threshold": 0.15,
  "ocr_confidence_threshold": 0.15
}
EOF

echo ""
echo "📋 Configuración:"
cat "$CONFIG_FILE"
echo ""

# Ejecutar test
docker exec -i traffic-inference python - <<PYTHON
import cv2
import asyncio
import json
import sys
from app.services.model_service import ModelService

async def test_video():
    print("🔄 Inicializando servicio...")
    service = ModelService()
    await service.initialize()
    
    print("✅ Servicio inicializado")
    print("")
    
    video_path = "$VIDEO_PATH"
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"❌ Error abriendo video: {video_path}")
        sys.exit(1)
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"📹 Video: {video_path}")
    print(f"   Frames: {total_frames}")
    print(f"   FPS: {fps:.2f}")
    print(f"   Resolución: {width}x{height}")
    print("")
    
    frame_count = 0
    plates_detected = []
    vehicles_detected = 0
    
    # Procesar cada 5 frames para velocidad
    skip_frames = 4
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Solo procesar cada N frames
        if frame_count % skip_frames != 0:
            continue
        
        # Detectar vehículos
        detections = await service.detect_vehicles(
            frame=frame,
            confidence_threshold=0.15
        )
        
        if detections:
            vehicles_detected += len(detections)
            print(f"🚗 Frame {frame_count}: {len(detections)} vehículos detectados")
            
            # Intentar OCR en cada vehículo
            for idx, det in enumerate(detections):
                vehicle_type = det.get('vehicle_type', 'unknown')
                confidence = det.get('confidence', 0)
                bbox_coords = det.get('bbox', [])
                
                print(f"   [{idx+1}] {vehicle_type} (conf: {confidence:.2f})")
                
                # Convertir bbox a formato dict
                if len(bbox_coords) == 4:
                    x1, y1, x2, y2 = bbox_coords
                    bbox_dict = {
                        'x': int(x1),
                        'y': int(y1),
                        'width': int(x2 - x1),
                        'height': int(y2 - y1)
                    }
                    
                    # Intentar OCR
                    plate_result = await service.detect_license_plate(
                        frame=frame,
                        bbox=bbox_dict
                    )
                    
                    if plate_result:
                        plate_text, plate_conf = plate_result
                        print(f"       ✅ PLACA: {plate_text} (conf: {plate_conf:.2f})")
                        plates_detected.append({
                            'frame': frame_count,
                            'plate': plate_text,
                            'confidence': plate_conf,
                            'vehicle_type': vehicle_type
                        })
                    else:
                        print(f"       ❌ Sin placa detectada")
        
        # Solo procesar primeros 200 frames para prueba rápida
        if frame_count >= 200:
            print(f"\n⏭️  Deteniendo en frame {frame_count} (prueba rápida)")
            break
    
    cap.release()
    
    print("")
    print("=" * 50)
    print("📊 RESUMEN")
    print("=" * 50)
    print(f"Frames procesados: {frame_count}")
    print(f"Vehículos detectados: {vehicles_detected}")
    print(f"Placas detectadas: {len(plates_detected)}")
    print("")
    
    if plates_detected:
        print("🎯 PLACAS ENCONTRADAS:")
        for p in plates_detected:
            print(f"   Frame {p['frame']:4d}: {p['plate']:10s} | {p['vehicle_type']:10s} | conf: {p['confidence']:.2f}")
    else:
        print("⚠️  NO SE DETECTARON PLACAS")
        print("")
        print("💡 Sugerencias:")
        print("   1. Verifica que el video tenga vehículos con placas visibles")
        print("   2. Aumenta el tiempo de procesamiento (quita límite de 200 frames)")
        print("   3. Reduce skip_frames de 4 a 2 o 1")
        print("   4. Verifica iluminación y calidad del video")

# Ejecutar
asyncio.run(test_video())
PYTHON

echo ""
echo "✅ Test completado"
