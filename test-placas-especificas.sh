#!/bin/bash

# Test ESPECÍFICO para VIDEO2 (B7J-482) y VIDEO5 (ABC-123)
# Con corrección de caracteres y umbral reducido a 10%

echo "🎯 TEST ESPECÍFICO - VIDEO2 y VIDEO5"
echo "====================================="
echo ""
echo "✅ Mejoras implementadas:"
echo "   - Umbral de confianza: 15% → 10%"
echo "   - Corrección de caracteres OCR (0→O, 4→A, E→3, Z→2, etc.)"
echo "   - Threshold binario adaptativo agregado"
echo "   - Calidad de imagen: 80% → 95%"
echo "   - Escala de video: 0.5 → 0.6"
echo ""

for VIDEO in VIDEO2.mp4 VIDEO5.mp4; do
    if [ "$VIDEO" == "VIDEO2.mp4" ]; then
        EXPECTED="B7J-482"
    else
        EXPECTED="ABC-123"
    fi
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📹 $VIDEO - Placa esperada: $EXPECTED"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    docker exec -i traffic-inference python - <<PYTHON
import cv2
import asyncio
import sys
import numpy as np
from app.services.model_service import ModelService

async def test_video():
    print("")
    print("🔄 Inicializando servicio...")
    service = ModelService()
    await service.initialize()
    print("✅ Servicio listo")
    print("")
    
    video_path = "/app/test_videos/$VIDEO"
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"❌ Error: No se pudo abrir {video_path}")
        sys.exit(1)
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"📹 Video: $VIDEO")
    print(f"   Resolución: {width}x{height} | FPS: {fps:.1f} | Frames: {total_frames}")
    print(f"   Placa esperada: $EXPECTED")
    print("")
    
    # ROI optimizado para placas
    roi_x = int(width * 0.1)
    roi_y = int(height * 0.3)
    roi_w = int(width * 0.8)
    roi_h = int(height * 0.6)
    
    frame_count = 0
    plates_found = {}
    best_match = None
    best_confidence = 0
    
    print("🔍 ANÁLISIS FRAME POR FRAME:")
    print("─" * 80)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Procesar cada 3 frames para mayor cobertura
        if frame_count % 3 != 0:
            continue
        
        # Aplicar ROI
        roi_frame = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
        
        # Detectar vehículos
        detections = await service.detect_vehicles(
            frame=roi_frame,
            confidence_threshold=0.10  # Umbral bajo
        )
        
        if detections:
            for det in detections:
                bbox_coords = det.get('bbox', [])
                if len(bbox_coords) == 4:
                    x1, y1, x2, y2 = bbox_coords
                    bbox = {
                        'x': int(x1),
                        'y': int(y1),
                        'width': int(x2 - x1),
                        'height': int(y2 - y1)
                    }
                    
                    # Solo procesar vehículos grandes
                    if bbox['width'] >= 50 and bbox['height'] >= 35:
                        plate_result = await service.detect_license_plate(
                            frame=roi_frame,
                            bbox=bbox
                        )
                        
                        if plate_result:
                            plate_text, plate_conf = plate_result
                            
                            # Mostrar TODAS las detecciones
                            match_symbol = "✅" if plate_text == "$EXPECTED" else "🔍"
                            print(f"Frame {frame_count:4d} | {match_symbol} {plate_text:10s} | Conf: {plate_conf:6.2%}")
                            
                            # Acumular
                            if plate_text not in plates_found:
                                plates_found[plate_text] = {
                                    'count': 1,
                                    'max_conf': plate_conf,
                                    'first_frame': frame_count
                                }
                            else:
                                plates_found[plate_text]['count'] += 1
                                if plate_conf > plates_found[plate_text]['max_conf']:
                                    plates_found[plate_text]['max_conf'] = plate_conf
                            
                            # Mejor match
                            if plate_conf > best_confidence:
                                best_confidence = plate_conf
                                best_match = plate_text
        
        # Procesar hasta 150 frames
        if frame_count >= 150:
            break
    
    cap.release()
    
    print("─" * 80)
    print("")
    print("📊 RESULTADOS:")
    print("")
    
    if plates_found:
        print(f"🎯 Placas detectadas: {len(plates_found)}")
        print("")
        
        # Ordenar por confianza
        sorted_plates = sorted(plates_found.items(), key=lambda x: x[1]['max_conf'], reverse=True)
        
        for plate, info in sorted_plates:
            is_match = "✅ CORRECTO" if plate == "$EXPECTED" else ""
            print(f"   📋 {plate:10s} | Apariciones: {info['count']:3d} | "
                  f"Confianza máx: {info['max_conf']:6.2%} | Frame: {info['first_frame']:4d} {is_match}")
        
        print("")
        
        if "$EXPECTED" in plates_found:
            conf = plates_found["$EXPECTED"]['max_conf']
            count = plates_found["$EXPECTED"]['count']
            print(f"🎉 ÉXITO: Placa esperada '$EXPECTED' detectada {count} veces (máx conf: {conf:.2%})")
        else:
            print(f"⚠️  Placa esperada '$EXPECTED' NO detectada")
            print(f"   Mejor match: {best_match} ({best_confidence:.2%})")
    else:
        print("❌ NO SE DETECTARON PLACAS")
        print("")
        print("💡 Posibles causas:")
        print("   - Placa muy pequeña o borrosa en el video")
        print("   - Ángulo de cámara no captura la placa")
        print("   - Iluminación insuficiente")

asyncio.run(test_video())
PYTHON

    echo ""
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ TEST COMPLETADO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
