#!/bin/bash

# Test INTENSIVO solo para VIDEO5 (ABC-123)
# Procesar TODOS los frames con múltiples técnicas

echo "🎯 TEST INTENSIVO - VIDEO5 (ABC-123)"
echo "======================================"
echo ""

docker exec -i traffic-inference python - <<'PYTHON'
import cv2
import asyncio
import sys
import numpy as np
from app.services.model_service import ModelService

async def analyze_video5():
    print("🔄 Inicializando...")
    service = ModelService()
    await service.initialize()
    print("✅ Listo")
    print("")
    
    video_path = "/app/test_videos/VIDEO5.mp4"
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"❌ Error abriendo video")
        sys.exit(1)
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"📹 VIDEO5.mp4")
    print(f"   {width}x{height} | {fps:.1f} FPS | {total_frames} frames | {total_frames/fps:.1f}s")
    print(f"   🎯 Buscando: ABC-123")
    print("")
    
    # Procesar TODO el video con diferentes ROIs
    frame_count = 0
    all_plates = {}
    
    print("🔍 PROCESANDO CADA FRAME:")
    print("─" * 80)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Procesar CADA frame (no saltar)
        # Probar 3 ROIs diferentes
        rois = [
            {'x': 0, 'y': 0, 'w': width, 'h': height, 'name': 'FULL'},  # Frame completo
            {'x': int(width*0.2), 'y': int(height*0.3), 'w': int(width*0.6), 'h': int(height*0.5), 'name': 'CENTER'},
            {'x': int(width*0.1), 'y': int(height*0.4), 'w': int(width*0.8), 'h': int(height*0.4), 'name': 'BOTTOM'},
        ]
        
        for roi_info in rois:
            x, y, w, h = roi_info['x'], roi_info['y'], roi_info['w'], roi_info['h']
            roi_frame = frame[y:y+h, x:x+w]
            
            # Detectar vehículos con umbral MUY bajo
            detections = await service.detect_vehicles(
                frame=roi_frame,
                confidence_threshold=0.05  # Umbral muy bajo
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
                        
                        # Procesar TODO vehículo (sin filtro de tamaño)
                        if bbox['width'] >= 40 and bbox['height'] >= 30:
                            plate_result = await service.detect_license_plate(
                                frame=roi_frame,
                                bbox=bbox
                            )
                            
                            if plate_result:
                                plate_text, plate_conf = plate_result
                                
                                symbol = "✅" if "ABC" in plate_text or "123" in plate_text else "🔍"
                                print(f"F{frame_count:3d} | {roi_info['name']:6s} | {symbol} {plate_text:10s} | {plate_conf:6.2%}")
                                
                                if plate_text not in all_plates:
                                    all_plates[plate_text] = {
                                        'count': 1,
                                        'max_conf': plate_conf,
                                        'frame': frame_count,
                                        'roi': roi_info['name']
                                    }
                                else:
                                    all_plates[plate_text]['count'] += 1
                                    if plate_conf > all_plates[plate_text]['max_conf']:
                                        all_plates[plate_text]['max_conf'] = plate_conf
                                        all_plates[plate_text]['frame'] = frame_count
    
    cap.release()
    
    print("─" * 80)
    print("")
    print("📊 RESULTADOS:")
    print("")
    
    if all_plates:
        print(f"Total placas detectadas: {len(all_plates)}")
        print("")
        
        # Buscar ABC-123 o variantes
        abc_variants = [p for p in all_plates.keys() if 'ABC' in p or 'A8C' in p or 'A3C' in p]
        
        if abc_variants:
            print("🎯 VARIANTES DE ABC ENCONTRADAS:")
            for p in abc_variants:
                info = all_plates[p]
                print(f"   ✅ {p:10s} | {info['count']:2d}x | {info['max_conf']:6.2%} | Frame {info['frame']}")
        
        print("")
        print("TODAS LAS PLACAS (ordenadas por confianza):")
        for plate, info in sorted(all_plates.items(), key=lambda x: x[1]['max_conf'], reverse=True)[:20]:
            match = "✅" if plate == "ABC-123" else ""
            print(f"   {plate:10s} | {info['count']:3d}x | {info['max_conf']:6.2%} | F{info['frame']:3d} | {info['roi']} {match}")
    else:
        print("❌ NO SE DETECTÓ NINGUNA PLACA")
        print("")
        print("🔧 DIAGNÓSTICO:")
        print("   1. Verifica que el video contenga vehículos con placas visibles")
        print("   2. La placa ABC-123 podría estar:")
        print("      - Muy borrosa/pixelada")
        print("      - En ángulo no frontal/trasero")
        print("      - Tapada parcialmente")
        print("      - Con texto muy pequeño")

asyncio.run(analyze_video5())
PYTHON

echo ""
echo "✅ Análisis completado"
