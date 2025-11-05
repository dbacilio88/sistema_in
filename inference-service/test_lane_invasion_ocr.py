#!/usr/bin/env python3
"""
Test script para detección de invasión de carril con OCR
Detecta infracciones de carril y placas de vehículos
"""

import sys
import os
import cv2
import numpy as np
from ultralytics import YOLO
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def detect_lane_lines(frame):
    """Detectar líneas de carril simples usando Canny y HoughLines"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    
    # Región de interés (mitad inferior de la imagen)
    height = frame.shape[0]
    roi = edges[height//2:, :]
    
    # Detectar líneas
    lines = cv2.HoughLinesP(roi, 1, np.pi/180, 50, minLineLength=50, maxLineGap=150)
    
    lane_lines = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Ajustar coordenadas a la imagen completa
            y1 += height//2
            y2 += height//2
            
            # Calcular ángulo
            angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
            
            # Filtrar líneas verticales (carriles)
            if 60 < angle < 120 or angle < 30 or angle > 150:
                lane_lines.append([(x1, y1), (x2, y2)])
    
    return lane_lines

def check_lane_invasion(vehicle_bbox, lane_lines, frame_width):
    """Verificar si un vehículo invade carril"""
    x1, y1, x2, y2 = vehicle_bbox
    vehicle_center_x = (x1 + x2) / 2
    vehicle_center_y = (y1 + y2) / 2
    vehicle_bottom_y = y2
    
    # Definir carril izquierdo/derecho basado en el centro del frame
    center_x = frame_width / 2
    
    for line in lane_lines:
        (lx1, ly1), (lx2, ly2) = line
        
        # Verificar si el vehículo cruza esta línea
        # Simplificación: verificar si el centro del vehículo está cerca de la línea
        if ly1 <= vehicle_center_y <= ly2 or ly2 <= vehicle_center_y <= ly1:
            # Interpolar X en la posición Y del vehículo
            if ly2 != ly1:
                line_x_at_vehicle = lx1 + (lx2 - lx1) * (vehicle_center_y - ly1) / (ly2 - ly1)
                
                # Verificar si el vehículo cruza la línea
                distance = abs(vehicle_center_x - line_x_at_vehicle)
                vehicle_width = x2 - x1
                
                if distance < vehicle_width * 0.3:  # 30% del ancho del vehículo
                    invasion_side = "left" if vehicle_center_x < center_x else "right"
                    return {
                        'invaded': True,
                        'side': invasion_side,
                        'distance': distance,
                        'line': line
                    }
    
    return {'invaded': False}

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 test_lane_invasion_ocr.py <video.mp4>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        logger.error(f"❌ No existe el archivo: {video_path}")
        sys.exit(1)
    
    logger.info(f"🎬 Analizando video: {video_path}")
    
    # Cargar modelo YOLO
    logger.info("🔄 Cargando modelo YOLOv8n...")
    model = YOLO('yolov8n.pt')
    
    # Cargar OCR
    logger.info("🔄 Cargando EasyOCR...")
    try:
        import easyocr
        reader = easyocr.Reader(['en'], gpu=False)
        logger.info("✅ OCR cargado")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo cargar OCR: {e}")
        reader = None
    
    # Abrir video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"❌ No se pudo abrir el video")
        sys.exit(1)
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    logger.info(f"📊 Total frames: {total_frames}, FPS: {fps:.2f}")
    
    # Classes de vehículos
    vehicle_classes = {
        2: 'car',
        3: 'motorcycle',
        5: 'bus',
        7: 'truck'
    }
    
    detected_infractions = []
    plates_detected = set()
    frame_count = 0
    
    logger.info(f"\n{'='*70}")
    logger.info("🚦 INICIANDO DETECCIÓN DE INVASIÓN DE CARRIL")
    logger.info(f"{'='*70}\n")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Procesar cada 5 frames
        if frame_count % 5 != 0:
            continue
        
        height, width = frame.shape[:2]
        
        # Detectar líneas de carril
        lane_lines = detect_lane_lines(frame)
        
        # Detectar vehículos
        results = model(frame, conf=0.3, verbose=False)
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                if cls in vehicle_classes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    vehicle_type = vehicle_classes[cls]
                    
                    # Verificar invasión de carril
                    invasion = check_lane_invasion([x1, y1, x2, y2], lane_lines, width)
                    
                    if invasion['invaded']:
                        logger.info(f"\n🚨 INVASIÓN DETECTADA (Frame {frame_count})")
                        logger.info(f"   Vehículo: {vehicle_type}")
                        logger.info(f"   Lado: {invasion['side']}")
                        logger.info(f"   Distancia: {invasion['distance']:.1f}px")
                        
                        # Intentar OCR
                        license_plate = None
                        if reader:
                            # Crop del vehículo con padding
                            padding = 10
                            crop_x1 = max(0, x1 - padding)
                            crop_y1 = max(0, y1 - padding)
                            crop_x2 = min(width, x2 + padding)
                            crop_y2 = min(height, y2 + padding)
                            vehicle_crop = frame[crop_y1:crop_y2, crop_x1:crop_x2]
                            
                            try:
                                ocr_results = reader.readtext(vehicle_crop)
                                for (bbox, text, conf_ocr) in ocr_results:
                                    # Limpiar texto
                                    text = text.replace(' ', '').upper()
                                    text = ''.join(c for c in text if c.isalnum() or c == '-')
                                    
                                    if len(text) >= 5 and conf_ocr > 0.5:
                                        license_plate = text
                                        logger.info(f"   📋 Placa: {license_plate} (conf: {conf_ocr:.2f})")
                                        break
                            except Exception as e:
                                logger.warning(f"   ⚠️ Error en OCR: {e}")
                        
                        if not license_plate:
                            logger.warning(f"   ⚠️ No se pudo detectar placa")
                            license_plate = f"UNKNOWN-{frame_count}"
                        
                        # Verificar duplicados
                        if license_plate not in plates_detected:
                            plates_detected.add(license_plate)
                            detected_infractions.append({
                                'frame': frame_count,
                                'type': 'lane_invasion',
                                'vehicle_type': vehicle_type,
                                'license_plate': license_plate,
                                'side': invasion['side'],
                                'distance': invasion['distance'],
                                'bbox': [x1, y1, x2, y2]
                            })
                            logger.info(f"   ✅ NUEVA INFRACCIÓN REGISTRADA (#{len(detected_infractions)})")
                        else:
                            logger.info(f"   ⏭️  DUPLICADO: Placa {license_plate} ya registrada")
    
    cap.release()
    
    # Resumen
    logger.info(f"\n{'='*70}")
    logger.info("📊 RESUMEN DE INFRACCIONES DETECTADAS")
    logger.info(f"{'='*70}\n")
    logger.info(f"Total frames procesados: {frame_count}")
    logger.info(f"Infracciones únicas detectadas: {len(detected_infractions)}")
    logger.info(f"Placas únicas: {len(plates_detected)}\n")
    
    if detected_infractions:
        logger.info("Detalles de infracciones:")
        for i, infraction in enumerate(detected_infractions, 1):
            logger.info(f"\n{i}. Frame {infraction['frame']}")
            logger.info(f"   Tipo: {infraction['type']}")
            logger.info(f"   Vehículo: {infraction['vehicle_type']}")
            logger.info(f"   Placa: {infraction['license_plate']}")
            logger.info(f"   Lado invadido: {infraction['side']}")
            logger.info(f"   Distancia: {infraction['distance']:.1f}px")
    else:
        logger.info("❌ No se detectaron infracciones de invasión de carril")
    
    logger.info(f"\n{'='*70}")
    logger.info("✅ Análisis completado")
    logger.info(f"{'='*70}\n")

if __name__ == "__main__":
    main()
