#!/bin/bash

# Test FINAL - Validar detección de placas en VIDEO2 y VIDEO5
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 TEST FINAL - DETECCIÓN DE PLACAS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

docker exec -i traffic-inference python - <<'PYTHON'
import cv2
import asyncio
import sys
from app.services.model_service import ModelService

async def test_both_videos():
    print("🔄 Inicializando...")
    service = ModelService()
    await service.initialize()
    print("")
    
    videos = [
        {
            'name': 'VIDEO2.mp4',
            'path': '/app/test_videos/VIDEO2.mp4',
            'plate': 'B7J-482',
            'roi': {'x': 0, 'y': 0, 'w': 1, 'h': 1}  # Frame completo
        },
        {
            'name': 'VIDEO5.mp4',
            'path': '/app/test_videos/VIDEO5.mp4',
            'plate': 'ABC-123',
            'roi': {'x': 0.1, 'y': 0.4, 'w': 0.8, 'h': 0.4}  # ROI inferior (BOTTOM)
        }
    ]
    
    for video_info in videos:
        print(f"📹 {video_info['name']} - Buscando: {video_info['plate']}")
        print("─" * 70)
        
        cap = cv2.VideoCapture(video_info['path'])
        if not cap.isOpened():
            print(f"❌ Error abriendo video")
            continue
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calcular ROI
        roi = video_info['roi']
        x1 = int(width * roi['x'])
        y1 = int(height * roi['y'])
        w = int(width * roi['w'])
        h = int(height * roi['h'])
        
        all_plates = {}
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Procesar cada 3 frames
            if frame_count % 3 != 0:
                continue
            
            # Aplicar ROI
            roi_frame = frame[y1:y1+h, x1:x1+w]
            
            # Detectar vehículos
            detections = await service.detect_vehicles(
                frame=roi_frame,
                confidence_threshold=0.05
            )
            
            if detections:
                for det in detections:
                    bbox_coords = det.get('bbox', [])
                    if len(bbox_coords) == 4:
                        x1b, y1b, x2b, y2b = bbox_coords
                        bbox = {
                            'x': int(x1b),
                            'y': int(y1b),
                            'width': int(x2b - x1b),
                            'height': int(y2b - y1b)
                        }
                        
                        if bbox['width'] >= 40 and bbox['height'] >= 30:
                            plate_result = await service.detect_license_plate(
                                frame=roi_frame,
                                bbox=bbox
                            )
                            
                            if plate_result:
                                plate_text, plate_conf = plate_result
                                
                                if plate_text not in all_plates:
                                    all_plates[plate_text] = {
                                        'count': 1,
                                        'max_conf': plate_conf,
                                        'frame': frame_count
                                    }
                                else:
                                    all_plates[plate_text]['count'] += 1
                                    if plate_conf > all_plates[plate_text]['max_conf']:
                                        all_plates[plate_text]['max_conf'] = plate_conf
                                        all_plates[plate_text]['frame'] = frame_count
        
        cap.release()
        
        # Mostrar resultados
        expected_plate = video_info['plate']
        found = False
        best_match = None
        
        if expected_plate in all_plates:
            found = True
            best_match = all_plates[expected_plate]
        
        if found:
            print(f"✅ PLACA DETECTADA: {expected_plate}")
            print(f"   Apariciones: {best_match['count']}x")
            print(f"   Confianza máxima: {best_match['max_conf']:.2%}")
            print(f"   Mejor frame: {best_match['frame']}")
        else:
            print(f"❌ PLACA NO DETECTADA: {expected_plate}")
            if all_plates:
                print(f"   Placas similares encontradas:")
                similar = [p for p in all_plates.keys() if expected_plate[:3] in p or expected_plate[4:] in p]
                for p in sorted(similar, key=lambda x: all_plates[x]['max_conf'], reverse=True)[:5]:
                    info = all_plates[p]
                    print(f"      {p} - {info['max_conf']:.2%} ({info['count']}x)")
        
        print("")

asyncio.run(test_both_videos())
PYTHON

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ TEST COMPLETADO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
