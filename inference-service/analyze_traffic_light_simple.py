#!/usr/bin/env python3
"""
Script simplificado para analizar colores HSV de semáforos
Usa ffmpeg para extraer frames si OpenCV falla
Uso: python3 analyze_traffic_light_simple.py <video.mp4>
"""

import sys
import os
import cv2
import numpy as np
from ultralytics import YOLO
import logging
import subprocess
import tempfile
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_frames_with_ffmpeg(video_path: str, output_dir: str, num_frames: int = 10):
    """Extraer frames usando ffmpeg como alternativa"""
    logger.info(f"📹 Extrayendo {num_frames} frames con ffmpeg...")
    
    # Obtener duración del video
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        duration = float(result.stdout.strip())
        logger.info(f"⏱️ Duración del video: {duration:.2f} segundos")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo obtener duración: {e}")
        duration = 60  # Asumir 60 segundos
    
    # Extraer frames espaciados uniformemente
    interval = duration / (num_frames + 1)
    frames_extracted = []
    
    for i in range(1, num_frames + 1):
        timestamp = i * interval
        output_file = os.path.join(output_dir, f"frame_{i:03d}.jpg")
        
        cmd = [
            'ffmpeg', '-ss', str(timestamp),
            '-i', video_path,
            '-frames:v', '1',
            '-q:v', '2',
            output_file,
            '-y'
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, timeout=10, check=True)
            if os.path.exists(output_file):
                frames_extracted.append(output_file)
                logger.info(f"✅ Frame extraído: {output_file} (t={timestamp:.2f}s)")
        except Exception as e:
            logger.warning(f"⚠️ Error extrayendo frame {i}: {e}")
    
    return frames_extracted

def analyze_image(image_path: str, model, frame_num: int):
    """Analizar una imagen en busca de semáforos"""
    
    # Leer imagen
    img = cv2.imread(image_path)
    if img is None:
        logger.error(f"❌ No se pudo leer: {image_path}")
        return None
    
    height, width = img.shape[:2]
    logger.info(f"📐 Frame #{frame_num}: {width}x{height}")
    
    # Detectar con YOLO
    results = model(img, conf=0.3, verbose=False)
    
    traffic_lights_found = []
    
    for result in results:
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
                
                traffic_lights_found.append({
                    'bbox': (x1, y1, x2, y2),
                    'conf': conf,
                    'size': (w, h)
                })
    
    return {
        'image': img,
        'traffic_lights': traffic_lights_found,
        'frame_num': frame_num
    }

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
        'v_mean': v_mean
    }

def interpret_hsv(h, s, v):
    """Interpretar valores HSV"""
    color = "Desconocido"
    
    if h <= 10 or h >= 160:
        color = "Rojo"
    elif 15 <= h <= 45:
        color = "Amarillo/Naranja"
    elif 40 <= h <= 95:
        color = "Verde"
    
    saturation = "Alta" if s > 100 else "Media" if s > 60 else "Baja"
    brightness = "Brillante" if v > 150 else "Normal" if v > 100 else "Oscuro"
    
    return f"{color} (Saturación: {saturation}, Brillo: {brightness})"

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 analyze_traffic_light_simple.py <video.mp4>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        logger.error(f"❌ No existe el archivo: {video_path}")
        sys.exit(1)
    
    logger.info(f"🎬 Analizando video: {video_path}")
    
    # Cargar modelo YOLO
    logger.info("🔄 Cargando modelo YOLOv8n...")
    model = YOLO('yolov8n.pt')
    
    # Crear directorio temporal para frames
    temp_dir = tempfile.mkdtemp(prefix="traffic_light_")
    logger.info(f"📁 Directorio temporal: {temp_dir}")
    
    try:
        # Extraer frames con ffmpeg
        frame_files = extract_frames_with_ffmpeg(video_path, temp_dir, num_frames=10)
        
        if not frame_files:
            logger.error("❌ No se pudo extraer ningún frame del video")
            return
        
        logger.info(f"\n{'='*70}")
        logger.info("🔍 ANÁLISIS DE SEMÁFOROS DETECTADOS")
        logger.info(f"{'='*70}\n")
        
        analyzed_count = 0
        max_analyses = 5
        
        # Analizar cada frame
        for i, frame_file in enumerate(frame_files, 1):
            if analyzed_count >= max_analyses:
                break
            
            result = analyze_image(frame_file, model, i)
            
            if result and result['traffic_lights']:
                img = result['image']
                
                for j, tl in enumerate(result['traffic_lights'], 1):
                    if analyzed_count >= max_analyses:
                        break
                    
                    analyzed_count += 1
                    bbox = tl['bbox']
                    conf = tl['conf']
                    size = tl['size']
                    
                    logger.info(f"\n🚦 Semáforo #{analyzed_count} (Frame {i})")
                    logger.info(f"   📍 Posición: {bbox}")
                    logger.info(f"   📏 Tamaño: {size[0]}x{size[1]} píxeles")
                    logger.info(f"   🎯 Confianza YOLO: {conf:.3f}")
                    
                    # Analizar colores HSV
                    hsv_data = analyze_hsv_colors(img, bbox)
                    
                    if hsv_data:
                        logger.info(f"\n   🎨 Análisis de color:")
                        logger.info(f"      🔴 Rojo:     {hsv_data['red_pixels']:4d} píxeles ({hsv_data['red_pct']:.1f}%)")
                        logger.info(f"      🟡 Amarillo: {hsv_data['yellow_pixels']:4d} píxeles ({hsv_data['yellow_pct']:.1f}%)")
                        logger.info(f"      🟢 Verde:    {hsv_data['green_pixels']:4d} píxeles ({hsv_data['green_pct']:.1f}%)")
                        
                        logger.info(f"\n   📊 Valores HSV promedio:")
                        logger.info(f"      H (Hue):        {hsv_data['h_mean']:.1f} (0-180)")
                        logger.info(f"      S (Saturation): {hsv_data['s_mean']:.1f} (0-255)")
                        logger.info(f"      V (Value):      {hsv_data['v_mean']:.1f} (0-255)")
                        
                        interpretation = interpret_hsv(
                            hsv_data['h_mean'],
                            hsv_data['s_mean'],
                            hsv_data['v_mean']
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
                        
                        # Recomendaciones
                        if hsv_data['s_mean'] < 60:
                            logger.info(f"\n   ⚠️ ADVERTENCIA: Saturación baja ({hsv_data['s_mean']:.1f})")
                            logger.info(f"      → Considerar reducir umbral S en rangos HSV")
                        
                        if hsv_data['v_mean'] < 40:
                            logger.info(f"\n   ⚠️ ADVERTENCIA: Brillo muy bajo ({hsv_data['v_mean']:.1f})")
                            logger.info(f"      → Considerar reducir umbral V en rangos HSV")
                        
                        if max_pct < 3.0:
                            logger.info(f"\n   ⚠️ ADVERTENCIA: Ningún color supera 3% de píxeles")
                            logger.info(f"      → Considerar ampliar rangos HSV o reducir umbrales")
        
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ Análisis completado: {analyzed_count} semáforos analizados")
        logger.info(f"{'='*70}\n")
        
    finally:
        # Limpiar directorio temporal
        shutil.rmtree(temp_dir)
        logger.info(f"🧹 Directorio temporal eliminado")

if __name__ == "__main__":
    main()
