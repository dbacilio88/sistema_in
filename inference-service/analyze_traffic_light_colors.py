#!/usr/bin/env python3
"""
Script para analizar colores HSV de semáforos detectados en video
Uso: python3 analyze_traffic_light_colors.py <video.mp4>
"""

import sys
import cv2
import numpy as np
from ultralytics import YOLO
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_traffic_light_colors(video_path: str):
    """Analizar colores HSV de semáforos en video"""
    
    # Cargar modelo YOLO
    logger.info("🔄 Cargando modelo YOLOv8n...")
    model = YOLO('yolov8n.pt')
    
    # Abrir video
    logger.info(f"📹 Abriendo video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        logger.error(f"❌ No se pudo abrir el video: {video_path}")
        return
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    logger.info(f"📊 Total frames: {total_frames}")
    
    frame_count = 0
    analyzed_count = 0
    max_analyses = 5  # Solo analizar 5 semáforos para ser rápido
    
    # Rangos HSV actuales
    red_lower1 = np.array([0, 80, 40])
    red_upper1 = np.array([10, 255, 255])
    red_lower2 = np.array([160, 80, 40])
    red_upper2 = np.array([180, 255, 255])
    
    yellow_lower = np.array([15, 60, 60])
    yellow_upper = np.array([45, 255, 255])
    
    green_lower = np.array([40, 50, 40])
    green_upper = np.array([95, 255, 255])
    
    logger.info("\n" + "="*70)
    logger.info("🎨 ANÁLISIS DE COLORES HSV")
    logger.info("="*70)
    
    while analyzed_count < max_analyses:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Solo procesar 1 de cada 20 frames
        if frame_count % 20 != 0:
            continue
        
        # Detectar semáforos con YOLO
        results = model(frame, verbose=False, imgsz=640, conf=0.15)
        
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                cls_id = int(box.cls[0])
                class_name = result.names[cls_id]
                confidence = float(box.conf[0])
                
                # Solo semáforos
                if class_name != 'traffic light' or confidence < 0.3:
                    continue
                
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # Validar bbox
                if x2 <= x1 or y2 <= y1 or x1 < 0 or y1 < 0:
                    continue
                
                bbox_width = x2 - x1
                bbox_height = y2 - y1
                
                # Semáforos muy pequeños, saltar
                if bbox_width < 20 or bbox_height < 20:
                    continue
                
                # Extraer ROI
                roi = frame[y1:y2, x1:x2]
                
                if roi.size == 0:
                    continue
                
                analyzed_count += 1
                
                logger.info(f"\n🚦 Semáforo #{analyzed_count} (Frame {frame_count})")
                logger.info(f"   📏 Tamaño: {bbox_width}x{bbox_height}px")
                logger.info(f"   📍 Posición: ({x1}, {y1}) - ({x2}, {y2})")
                logger.info(f"   🎯 Confianza YOLO: {confidence:.3f}")
                
                # Convertir a HSV
                hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                
                # Calcular píxeles de cada color
                mask_red1 = cv2.inRange(hsv, red_lower1, red_upper1)
                mask_red2 = cv2.inRange(hsv, red_lower2, red_upper2)
                mask_red = cv2.bitwise_or(mask_red1, mask_red2)
                red_pixels = cv2.countNonZero(mask_red)
                
                mask_yellow = cv2.inRange(hsv, yellow_lower, yellow_upper)
                yellow_pixels = cv2.countNonZero(mask_yellow)
                
                mask_green = cv2.inRange(hsv, green_lower, green_upper)
                green_pixels = cv2.countNonZero(mask_green)
                
                total_pixels = bbox_width * bbox_height
                
                red_pct = (red_pixels / total_pixels) * 100
                yellow_pct = (yellow_pixels / total_pixels) * 100
                green_pct = (green_pixels / total_pixels) * 100
                
                logger.info(f"\n   🎨 Análisis de color:")
                logger.info(f"      🔴 Rojo:     {red_pixels:5d} píxeles ({red_pct:5.2f}%)")
                logger.info(f"      🟡 Amarillo: {yellow_pixels:5d} píxeles ({yellow_pct:5.2f}%)")
                logger.info(f"      🟢 Verde:    {green_pixels:5d} píxeles ({green_pct:5.2f}%)")
                logger.info(f"      ⚪ Total:    {total_pixels:5d} píxeles")
                
                # Determinar color dominante
                max_color = max(red_pct, yellow_pct, green_pct)
                
                if max_color < 3.0:
                    logger.info(f"   ⚪ Estado: DESCONOCIDO (ningún color > 3%)")
                elif max_color == red_pct:
                    logger.info(f"   🔴 Estado: ROJO detectado ({red_pct:.2f}%)")
                elif max_color == yellow_pct:
                    logger.info(f"   🟡 Estado: AMARILLO detectado ({yellow_pct:.2f}%)")
                else:
                    logger.info(f"   🟢 Estado: VERDE detectado ({green_pct:.2f}%)")
                
                # Analizar distribución HSV
                h, s, v = cv2.split(hsv)
                
                h_mean = np.mean(h)
                s_mean = np.mean(s)
                v_mean = np.mean(v)
                
                logger.info(f"\n   📊 Valores HSV promedio:")
                logger.info(f"      H (Hue):        {h_mean:6.1f} (0-180)")
                logger.info(f"      S (Saturation): {s_mean:6.1f} (0-255)")
                logger.info(f"      V (Value):      {v_mean:6.1f} (0-255)")
                
                # Interpretar valores H
                if 0 <= h_mean <= 10 or 160 <= h_mean <= 180:
                    color_name = "Rojo"
                elif 15 <= h_mean <= 45:
                    color_name = "Amarillo/Naranja"
                elif 40 <= h_mean <= 95:
                    color_name = "Verde"
                else:
                    color_name = "Otro"
                
                logger.info(f"      Interpretación H: {color_name}")
                
                # Recomendaciones
                if s_mean < 60:
                    logger.info(f"   ⚠️  Saturación baja ({s_mean:.1f}) - Color poco saturado/apagado")
                if v_mean < 40:
                    logger.info(f"   ⚠️  Valor bajo ({v_mean:.1f}) - Imagen muy oscura")
                
                if analyzed_count >= max_analyses:
                    break
            
            if analyzed_count >= max_analyses:
                break
    
    cap.release()
    
    logger.info("\n" + "="*70)
    logger.info("💡 RECOMENDACIONES")
    logger.info("="*70)
    logger.info("""
Si la mayoría de semáforos muestran:

🔴 ROJO con bajo %:
   - Los rangos HSV actuales funcionan pero son estrictos
   - Considera reducir los umbrales S y V si % < 3%
   
🟡 AMARILLO cuando debería ser ROJO:
   - Ajusta rangos HSV de rojo para incluir más naranjas
   - Verifica el valor H promedio de los semáforos rojos
   
🟢 VERDE cuando debería ser ROJO:
   - Problema de iluminación o semáforo apagado
   - Verifica valores HSV promedio
   
⚪ DESCONOCIDO (todos < 3%):
   - Semáforos muy oscuros/apagados
   - Reduce umbral de min_color_percentage a 1-2%
   - Reduce umbrales S y V en rangos HSV

📊 Valores HSV típicos:
   Rojo:     H=[0-10, 160-180], S=[80+], V=[40+]
   Amarillo: H=[15-45],          S=[60+], V=[60+]
   Verde:    H=[40-95],          S=[50+], V=[40+]
""")
    
    logger.info("="*70 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 analyze_traffic_light_colors.py <video.mp4>")
        print("\nEjemplo:")
        print("  python3 analyze_traffic_light_colors.py /app/VIDEO1.mp4")
        sys.exit(1)
    
    video_path = sys.argv[1]
    analyze_traffic_light_colors(video_path)
