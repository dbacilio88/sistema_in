#!/usr/bin/env python3
"""
Script para analizar colores HSV de semáforos - versión con mejor manejo de video
Uso: python3 analyze_traffic_light_direct.py <video.mp4>
"""

import sys
import os
import cv2
import numpy as np
from ultralytics import YOLO
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_hsv_colors(img, bbox):
    """Analizar colores HSV en un bounding box"""
    x1, y1, x2, y2 = bbox
    
    # Extraer ROI
    roi = img[y1:y2, x1:x2]
    
    if roi.size == 0:
        return None
    
    # Convertir a HSV
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # Rangos HSV actuales
    red_lower1 = np.array([0, 80, 40])
    red_upper1 = np.array([10, 255, 255])
    red_lower2 = np.array([160, 80, 40])
    red_upper2 = np.array([180, 255, 255])
    
    yellow_lower = np.array([15, 60, 60])
    yellow_upper = np.array([45, 255, 255])
    
    green_lower = np.array([40, 50, 40])
    green_upper = np.array([95, 255, 255])
    
    # Contar píxeles de cada color
    red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
    red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)
    red_pixels = cv2.countNonZero(red_mask)
    
    yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
    yellow_pixels = cv2.countNonZero(yellow_mask)
    
    green_mask = cv2.inRange(hsv, green_lower, green_upper)
    green_pixels = cv2.countNonZero(green_mask)
    
    total_pixels = roi.shape[0] * roi.shape[1]
    
    # Calcular promedios HSV
    h_mean = np.mean(hsv[:, :, 0])
    s_mean = np.mean(hsv[:, :, 1])
    v_mean = np.mean(hsv[:, :, 2])
    
    # También calcular promedios solo de píxeles con saturación alta (>50)
    high_sat_mask = hsv[:, :, 1] > 50
    if np.any(high_sat_mask):
        h_mean_sat = np.mean(hsv[high_sat_mask, 0])
        s_mean_sat = np.mean(hsv[high_sat_mask, 1])
        v_mean_sat = np.mean(hsv[high_sat_mask, 2])
    else:
        h_mean_sat = h_mean
        s_mean_sat = s_mean
        v_mean_sat = v_mean
    
    return {
        'red_pixels': red_pixels,
        'red_pct': (red_pixels / total_pixels * 100),
        'yellow_pixels': yellow_pixels,
        'yellow_pct': (yellow_pixels / total_pixels * 100),
        'green_pixels': green_pixels,
        'green_pct': (green_pixels / total_pixels * 100),
        'total_pixels': total_pixels,
        'h_mean': h_mean,
        's_mean': s_mean,
        'v_mean': v_mean,
        'h_mean_sat': h_mean_sat,
        's_mean_sat': s_mean_sat,
        'v_mean_sat': v_mean_sat
    }

def interpret_hsv(h, s, v):
    """Interpretar valores HSV"""
    color = "Desconocido"
    
    if h <= 10 or h >= 160:
        color = "Rojo"
    elif 11 <= h <= 25:
        color = "Naranja/Rojo-Amarillo"
    elif 26 <= h <= 45:
        color = "Amarillo"
    elif 46 <= h <= 95:
        color = "Verde"
    
    saturation = "Alta" if s > 100 else "Media" if s > 60 else "Baja"
    brightness = "Brillante" if v > 150 else "Normal" if v > 100 else "Oscuro"
    
    return f"{color} (Saturación: {saturation}, Brillo: {brightness})"

def analyze_video_frames(video_path: str, model, num_samples: int = 10):
    """Analizar frames del video usando cv2.VideoCapture con backend alternativo"""
    
    # Intentar con diferentes backends
    backends = [
        cv2.CAP_FFMPEG,
        cv2.CAP_ANY,
        cv2.CAP_GSTREAMER,
        0  # Default
    ]
    
    cap = None
    for backend in backends:
        logger.info(f"🔄 Intentando abrir video con backend {backend}...")
        cap = cv2.VideoCapture(video_path, backend)
        if cap.isOpened():
            logger.info(f"✅ Video abierto exitosamente con backend {backend}")
            break
        cap.release()
    
    if cap is None or not cap.isOpened():
        logger.error(f"❌ No se pudo abrir el video con ningún backend")
        return []
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    logger.info(f"📊 Total frames: {total_frames}")
    logger.info(f"🎬 FPS: {fps:.2f}")
    
    # Calcular frames a muestrear
    if total_frames <= 0:
        logger.warning("⚠️ No se pudo determinar el total de frames, muestreando cada 30 frames")
        frame_indices = list(range(0, 300, 30))  # Primeros 10 segundos aprox
    else:
        step = max(1, total_frames // num_samples)
        frame_indices = list(range(0, total_frames, step))[:num_samples]
    
    logger.info(f"📍 Frames a analizar: {frame_indices}")
    
    results = []
    
    for frame_idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        
        if not ret or frame is None:
            logger.warning(f"⚠️ No se pudo leer frame {frame_idx}")
            continue
        
        height, width = frame.shape[:2]
        logger.info(f"\n📐 Frame #{frame_idx}: {width}x{height}")
        
        # Detectar con YOLO
        detections = model(frame, conf=0.3, verbose=False)
        
        traffic_lights = []
        for result in detections:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                # Clase 9 = traffic light
                if cls == 9 and conf > 0.3:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    w, h = x2 - x1, y2 - y1
                    
                    # Filtrar muy pequeños
                    if w < 10 or h < 10:
                        continue
                    
                    traffic_lights.append({
                        'frame': frame,
                        'frame_idx': frame_idx,
                        'bbox': (x1, y1, x2, y2),
                        'conf': conf,
                        'size': (w, h)
                    })
        
        results.extend(traffic_lights)
    
    cap.release()
    return results

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 analyze_traffic_light_direct.py <video.mp4>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        logger.error(f"❌ No existe el archivo: {video_path}")
        sys.exit(1)
    
    logger.info(f"🎬 Analizando video: {video_path}")
    
    # Cargar modelo YOLO
    logger.info("🔄 Cargando modelo YOLOv8n...")
    model = YOLO('yolov8n.pt')
    
    # Analizar frames
    traffic_lights = analyze_video_frames(video_path, model, num_samples=10)
    
    if not traffic_lights:
        logger.error("❌ No se detectaron semáforos en el video")
        return
    
    logger.info(f"\n{'='*70}")
    logger.info(f"🔍 ANÁLISIS DE SEMÁFOROS DETECTADOS")
    logger.info(f"{'='*70}\n")
    logger.info(f"Total semáforos detectados: {len(traffic_lights)}")
    
    # Analizar hasta 5 semáforos
    max_analyses = min(5, len(traffic_lights))
    
    for i, tl in enumerate(traffic_lights[:max_analyses], 1):
        frame = tl['frame']
        bbox = tl['bbox']
        conf = tl['conf']
        size = tl['size']
        frame_idx = tl['frame_idx']
        
        logger.info(f"\n🚦 Semáforo #{i} (Frame {frame_idx})")
        logger.info(f"   📍 Posición: {bbox}")
        logger.info(f"   📏 Tamaño: {size[0]}x{size[1]} píxeles")
        logger.info(f"   🎯 Confianza YOLO: {conf:.3f}")
        
        # Analizar colores HSV
        hsv_data = analyze_hsv_colors(frame, bbox)
        
        if hsv_data:
            logger.info(f"\n   🎨 Análisis de color:")
            logger.info(f"      🔴 Rojo:     {hsv_data['red_pixels']:4d} píxeles ({hsv_data['red_pct']:.1f}%)")
            logger.info(f"      🟡 Amarillo: {hsv_data['yellow_pixels']:4d} píxeles ({hsv_data['yellow_pct']:.1f}%)")
            logger.info(f"      🟢 Verde:    {hsv_data['green_pixels']:4d} píxeles ({hsv_data['green_pct']:.1f}%)")
            
            logger.info(f"\n   📊 Valores HSV promedio (todos los píxeles):")
            logger.info(f"      H (Hue):        {hsv_data['h_mean']:.1f} (0-180)")
            logger.info(f"      S (Saturation): {hsv_data['s_mean']:.1f} (0-255)")
            logger.info(f"      V (Value):      {hsv_data['v_mean']:.1f} (0-255)")
            
            logger.info(f"\n   📊 Valores HSV promedio (solo píxeles saturados S>50):")
            logger.info(f"      H (Hue):        {hsv_data['h_mean_sat']:.1f} (0-180)")
            logger.info(f"      S (Saturation): {hsv_data['s_mean_sat']:.1f} (0-255)")
            logger.info(f"      V (Value):      {hsv_data['v_mean_sat']:.1f} (0-255)")
            
            interpretation = interpret_hsv(
                hsv_data['h_mean_sat'],
                hsv_data['s_mean_sat'],
                hsv_data['v_mean_sat']
            )
            logger.info(f"\n   💡 Interpretación: {interpretation}")
            
            # Determinar color dominante
            max_pct = max(hsv_data['red_pct'], hsv_data['yellow_pct'], hsv_data['green_pct'])
            if max_pct < 3.0:
                dominant = "⚪ DESCONOCIDO (muy bajo porcentaje)"
            elif hsv_data['red_pct'] == max_pct:
                dominant = f"🔴 ROJO ({hsv_data['red_pct']:.1f}%)"
            elif hsv_data['yellow_pct'] == max_pct:
                dominant = f"🟡 AMARILLO ({hsv_data['yellow_pct']:.1f}%)"
            else:
                dominant = f"🟢 VERDE ({hsv_data['green_pct']:.1f}%)"
            
            logger.info(f"   🏆 Color dominante: {dominant}")
            
            # Recomendaciones basadas en los valores
            logger.info(f"\n   💡 Recomendaciones:")
            
            if hsv_data['s_mean'] < 60:
                logger.info(f"      ⚠️ Saturación baja ({hsv_data['s_mean']:.1f})")
                logger.info(f"         → Reducir umbral S mínimo de 80 a 50-60")
            
            if hsv_data['v_mean'] < 40:
                logger.info(f"      ⚠️ Brillo muy bajo ({hsv_data['v_mean']:.1f})")
                logger.info(f"         → Reducir umbral V mínimo de 40 a 20-30")
            
            if max_pct < 3.0:
                logger.info(f"      ⚠️ Ningún color supera 3% de píxeles")
                logger.info(f"         → Ampliar rangos HSV o reducir umbrales")
            
            # Recomendaciones específicas por color detectado
            h = hsv_data['h_mean_sat']
            if 11 <= h <= 25:
                logger.info(f"      💡 H={h:.1f} está en zona naranja/rojo-amarillo")
                logger.info(f"         → Considerar extender rango rojo hasta H=15 o 20")
            elif 26 <= h <= 35:
                logger.info(f"      💡 H={h:.1f} está en zona amarilla pero cerca del rojo")
                logger.info(f"         → Verificar visualmente si el semáforo es rojo o amarillo")
    
    logger.info(f"\n{'='*70}")
    logger.info(f"✅ Análisis completado: {max_analyses} semáforos analizados")
    logger.info(f"{'='*70}\n")

if __name__ == "__main__":
    main()
