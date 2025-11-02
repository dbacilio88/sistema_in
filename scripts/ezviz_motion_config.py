#!/usr/bin/env python3
"""
Script para configurar detección de movimiento y visión nocturna en EZVIZ H6C Pro 2K
Incluye calibración automática de sensibilidad y tests de funcionamiento
"""

import cv2
import numpy as np
import time
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class MotionEvent:
    """Evento de detección de movimiento"""
    timestamp: datetime
    motion_percentage: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float

class EzvizMotionDetector:
    """Detector de movimiento optimizado para EZVIZ H6C Pro 2K"""
    
    def __init__(self, rtsp_url: str = None):
        self.rtsp_url = rtsp_url or "rtsp://admin:Abc123456@192.168.1.100:554/h264/ch1/main/av_stream"
        
        # Parámetros de detección configurables
        self.sensitivity = 0.5  # 0.1 (baja) - 1.0 (alta)
        self.min_contour_area = 500  # Área mínima del objeto en movimiento
        self.gaussian_blur_size = 21  # Tamaño del filtro Gaussiano
        self.threshold_value = 25  # Umbral de diferencia
        self.history_frames = 5  # Frames de historia para estabilidad
        
        # Variables internas
        self.background_subtractor = None
        self.frame_history = []
        self.motion_events = []
        self.calibration_data = {}
        
    def initialize_background_subtractor(self):
        """Inicializar sustractor de fondo"""
        # Usar MOG2 para mejor detección en exteriores
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=50,
            detectShadows=True
        )
    
    def calibrate_sensitivity(self, duration_seconds: int = 60) -> Dict[str, Any]:
        """
        Calibrar sensibilidad automáticamente observando la escena
        
        Args:
            duration_seconds: Duración de la calibración en segundos
            
        Returns:
            Dict con parámetros calibrados y estadísticas
        """
        print(f"🔧 Iniciando calibración automática ({duration_seconds}s)...")
        print("   ℹ️ Evitar movimiento durante la calibración para mejor resultado")
        
        cap = cv2.VideoCapture(self.rtsp_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not cap.isOpened():
            raise Exception("No se pudo conectar al stream RTSP")
        
        # Inicializar sustractor de fondo
        self.initialize_background_subtractor()
        
        # Estadísticas de calibración
        noise_levels = []
        light_changes = []
        frame_differences = []
        
        calibration_start = time.time()
        frame_count = 0
        prev_frame = None
        
        while (time.time() - calibration_start) < duration_seconds:
            ret, frame = cap.read()
            if not ret:
                continue
                
            frame_count += 1
            
            # Convertir a escala de grises
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (self.gaussian_blur_size, self.gaussian_blur_size), 0)
            
            # Aplicar sustractor de fondo
            fg_mask = self.background_subtractor.apply(gray)
            
            # Medir nivel de ruido (píxeles en movimiento sin movimiento real)
            noise_pixel_count = cv2.countNonZero(fg_mask)
            total_pixels = fg_mask.shape[0] * fg_mask.shape[1]
            noise_percentage = (noise_pixel_count / total_pixels) * 100
            noise_levels.append(noise_percentage)
            
            # Medir cambios de iluminación
            if prev_frame is not None:
                frame_diff = cv2.absdiff(gray, prev_frame)
                avg_diff = np.mean(frame_diff)
                frame_differences.append(avg_diff)
                
                # Detectar cambios bruscos de luz
                if avg_diff > 20:  # Umbral para cambio de luz
                    light_changes.append({
                        'timestamp': time.time() - calibration_start,
                        'difference': avg_diff
                    })
            
            prev_frame = gray.copy()
            
            # Mostrar progreso cada 10 segundos
            elapsed = time.time() - calibration_start
            if frame_count % 300 == 0:  # ~10s a 30fps
                print(f"   📊 {elapsed:.0f}s - Ruido promedio: {np.mean(noise_levels[-300:]):.2f}%")
        
        cap.release()
        
        # Analizar estadísticas para calibrar parámetros
        avg_noise = np.mean(noise_levels)
        max_noise = np.max(noise_levels)
        std_noise = np.std(noise_levels)
        avg_light_change = np.mean(frame_differences) if frame_differences else 0
        
        # Calibrar sensibilidad basada en ruido ambiente
        if avg_noise < 0.1:  # Muy poco ruido
            self.sensitivity = 0.2
            self.threshold_value = 15
        elif avg_noise < 0.5:  # Ruido bajo
            self.sensitivity = 0.3
            self.threshold_value = 20
        elif avg_noise < 1.0:  # Ruido moderado
            self.sensitivity = 0.5
            self.threshold_value = 25
        else:  # Ruido alto
            self.sensitivity = 0.7
            self.threshold_value = 35
        
        # Ajustar área mínima basada en resolución
        self.min_contour_area = max(300, int(2560 * 1440 * 0.0001))  # 0.01% de la imagen
        
        self.calibration_data = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration_seconds,
            'frames_analyzed': frame_count,
            'statistics': {
                'avg_noise_percentage': round(avg_noise, 3),
                'max_noise_percentage': round(max_noise, 3),
                'noise_std': round(std_noise, 3),
                'avg_light_change': round(avg_light_change, 2),
                'light_change_events': len(light_changes)
            },
            'calibrated_parameters': {
                'sensitivity': self.sensitivity,
                'threshold_value': self.threshold_value,
                'min_contour_area': self.min_contour_area,
                'gaussian_blur_size': self.gaussian_blur_size
            }
        }
        
        print(f"✅ Calibración completada:")
        print(f"   📈 Sensibilidad: {self.sensitivity}")
        print(f"   🎚️ Umbral: {self.threshold_value}")
        print(f"   📐 Área mínima: {self.min_contour_area}")
        print(f"   🔊 Ruido promedio: {avg_noise:.2f}%")
        
        return self.calibration_data
    
    def detect_motion_realtime(self, duration_seconds: int = 300) -> List[MotionEvent]:
        """
        Detectar movimiento en tiempo real
        
        Args:
            duration_seconds: Duración del monitoreo en segundos
            
        Returns:
            Lista de eventos de movimiento detectados
        """
        print(f"🚨 Iniciando detección de movimiento ({duration_seconds}s)...")
        
        cap = cv2.VideoCapture(self.rtsp_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not cap.isOpened():
            raise Exception("No se pudo conectar al stream RTSP")
        
        # Inicializar sustractor de fondo si no existe
        if self.background_subtractor is None:
            self.initialize_background_subtractor()
        
        detection_start = time.time()
        self.motion_events = []
        last_motion_time = 0
        motion_cooldown = 2  # Segundos entre detecciones para evitar spam
        
        while (time.time() - detection_start) < duration_seconds:
            ret, frame = cap.read()
            if not ret:
                continue
            
            current_time = time.time()
            
            # Procesar frame para detección
            motion_data = self._process_frame_for_motion(frame)
            
            # Detectar movimiento significativo
            if (motion_data['motion_detected'] and 
                current_time - last_motion_time > motion_cooldown):
                
                event = MotionEvent(
                    timestamp=datetime.now(),
                    motion_percentage=motion_data['motion_percentage'],
                    bbox=motion_data['largest_bbox'],
                    confidence=motion_data['confidence']
                )
                
                self.motion_events.append(event)
                last_motion_time = current_time
                
                elapsed = current_time - detection_start
                print(f"   🎯 Movimiento detectado a los {elapsed:.1f}s - "
                      f"{motion_data['motion_percentage']:.1f}% de cambio")
        
        cap.release()
        
        print(f"✅ Detección completada - {len(self.motion_events)} eventos detectados")
        return self.motion_events
    
    def _process_frame_for_motion(self, frame: np.ndarray) -> Dict[str, Any]:
        """Procesar un frame individual para detección de movimiento"""
        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (self.gaussian_blur_size, self.gaussian_blur_size), 0)
        
        # Aplicar sustractor de fondo
        fg_mask = self.background_subtractor.apply(gray)
        
        # Operaciones morfológicas para limpiar la máscara
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar contornos por área
        valid_contours = [c for c in contours if cv2.contourArea(c) > self.min_contour_area]
        
        motion_data = {
            'motion_detected': False,
            'motion_percentage': 0.0,
            'contour_count': len(valid_contours),
            'largest_bbox': (0, 0, 0, 0),
            'confidence': 0.0
        }
        
        if valid_contours:
            # Calcular porcentaje de movimiento
            total_motion_area = sum(cv2.contourArea(c) for c in valid_contours)
            frame_area = frame.shape[0] * frame.shape[1]
            motion_percentage = (total_motion_area / frame_area) * 100
            
            # Encontrar el contorno más grande
            largest_contour = max(valid_contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Calcular confianza basada en área y estabilidad
            confidence = min(1.0, motion_percentage / 5.0)  # Máximo 5% para confianza 100%
            
            # Determinar si hay movimiento significativo
            motion_detected = motion_percentage > (self.sensitivity * 2)  # Ajustar por sensibilidad
            
            motion_data.update({
                'motion_detected': motion_detected,
                'motion_percentage': motion_percentage,
                'largest_bbox': (x, y, w, h),
                'confidence': confidence
            })
        
        return motion_data
    
    def test_night_vision_transition(self, test_duration: int = 120) -> Dict[str, Any]:
        """
        Probar transición automática de visión nocturna
        
        Args:
            test_duration: Duración del test en segundos
            
        Returns:
            Análisis de la transición de visión nocturna
        """
        print(f"🌙 Probando transición de visión nocturna ({test_duration}s)...")
        
        cap = cv2.VideoCapture(self.rtsp_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not cap.isOpened():
            raise Exception("No se pudo conectar al stream RTSP")
        
        brightness_history = []
        color_saturation_history = []
        test_start = time.time()
        
        while (time.time() - test_start) < test_duration:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Analizar brillo
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            brightness_history.append(brightness)
            
            # Analizar saturación de color (para detectar modo IR)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            saturation = np.mean(hsv[:,:,1])
            color_saturation_history.append(saturation)
            
            time.sleep(1)  # Muestrear cada segundo
        
        cap.release()
        
        # Analizar resultados
        avg_brightness = np.mean(brightness_history)
        brightness_std = np.std(brightness_history)
        avg_saturation = np.mean(color_saturation_history)
        
        # Detectar si está en modo IR (baja saturación + patrón de brillo)
        ir_mode_detected = avg_saturation < 30 and avg_brightness < 100
        
        # Detectar transiciones (cambios bruscos de brillo)
        brightness_diff = np.diff(brightness_history)
        transitions = []
        
        for i, diff in enumerate(brightness_diff):
            if abs(diff) > 20:  # Cambio significativo de brillo
                transitions.append({
                    'time': i,
                    'brightness_change': diff,
                    'type': 'to_ir' if diff < 0 else 'to_color'
                })
        
        night_vision_data = {
            'timestamp': datetime.now().isoformat(),
            'test_duration': test_duration,
            'samples_collected': len(brightness_history),
            'analysis': {
                'avg_brightness': round(avg_brightness, 2),
                'brightness_std': round(brightness_std, 2),
                'avg_color_saturation': round(avg_saturation, 2),
                'ir_mode_detected': ir_mode_detected,
                'transitions_detected': len(transitions),
                'transitions': transitions
            }
        }
        
        print(f"✅ Test de visión nocturna completado:")
        print(f"   💡 Brillo promedio: {avg_brightness:.1f}")
        print(f"   🎨 Saturación promedio: {avg_saturation:.1f}")
        print(f"   🌙 Modo IR detectado: {'Sí' if ir_mode_detected else 'No'}")
        print(f"   🔄 Transiciones: {len(transitions)}")
        
        return night_vision_data
    
    def save_configuration(self, filename: str = None) -> str:
        """Guardar configuración actual"""
        if filename is None:
            filename = f"ezviz_motion_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        config = {
            'timestamp': datetime.now().isoformat(),
            'rtsp_url': self.rtsp_url,
            'motion_detection_params': {
                'sensitivity': self.sensitivity,
                'min_contour_area': self.min_contour_area,
                'gaussian_blur_size': self.gaussian_blur_size,
                'threshold_value': self.threshold_value,
                'history_frames': self.history_frames
            },
            'calibration_data': self.calibration_data,
            'motion_events_count': len(self.motion_events)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Configuración guardada: {filename}")
        return filename
    
    def load_configuration(self, filename: str):
        """Cargar configuración desde archivo"""
        with open(filename, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        params = config['motion_detection_params']
        self.sensitivity = params['sensitivity']
        self.min_contour_area = params['min_contour_area']
        self.gaussian_blur_size = params['gaussian_blur_size']
        self.threshold_value = params['threshold_value']
        self.history_frames = params['history_frames']
        
        print(f"📁 Configuración cargada desde: {filename}")

def main():
    """Función principal con CLI"""
    parser = argparse.ArgumentParser(description='Configurador de detección de movimiento EZVIZ')
    parser.add_argument('--rtsp-url', help='URL RTSP personalizada')
    parser.add_argument('--calibrate', action='store_true', 
                       help='Ejecutar calibración automática')
    parser.add_argument('--calibration-duration', type=int, default=60,
                       help='Duración de calibración en segundos (default: 60)')
    parser.add_argument('--test-motion', action='store_true',
                       help='Probar detección de movimiento')
    parser.add_argument('--motion-duration', type=int, default=300,
                       help='Duración de test de movimiento en segundos (default: 300)')
    parser.add_argument('--test-night-vision', action='store_true',
                       help='Probar transición de visión nocturna')
    parser.add_argument('--night-duration', type=int, default=120,
                       help='Duración de test nocturno en segundos (default: 120)')
    parser.add_argument('--save-config', action='store_true',
                       help='Guardar configuración en archivo JSON')
    parser.add_argument('--load-config', help='Cargar configuración desde archivo')
    
    args = parser.parse_args()
    
    # Crear detector
    detector = EzvizMotionDetector(rtsp_url=args.rtsp_url)
    
    print("🚀 Configurador EZVIZ H6C Pro 2K - Detección de Movimiento")
    print("=" * 70)
    
    # Cargar configuración si se especifica
    if args.load_config:
        detector.load_configuration(args.load_config)
    
    # Ejecutar calibración
    if args.calibrate:
        calibration_result = detector.calibrate_sensitivity(args.calibration_duration)
        print(f"\n📊 Datos de calibración: {json.dumps(calibration_result, indent=2)}")
    
    # Probar detección de movimiento
    if args.test_motion:
        print("\n🚨 INSTRUCCIONES PARA TEST DE MOVIMIENTO:")
        print("   1. Posicione la cámara hacia la zona de tráfico")
        print("   2. Durante el test, haga que vehículos pasen por el campo de visión")
        print("   3. El detector reportará cada evento de movimiento significativo")
        input("\nPresione Enter para iniciar el test de movimiento...")
        
        motion_events = detector.detect_motion_realtime(args.motion_duration)
        
        print(f"\n📋 RESUMEN DE DETECCIÓN:")
        print(f"   Total eventos: {len(motion_events)}")
        for i, event in enumerate(motion_events[-5:], 1):  # Mostrar últimos 5
            print(f"   {i}. {event.timestamp.strftime('%H:%M:%S')} - "
                  f"{event.motion_percentage:.1f}% - "
                  f"Confianza: {event.confidence:.2f}")
    
    # Probar visión nocturna
    if args.test_night_vision:
        print("\n🌙 INSTRUCCIONES PARA TEST DE VISIÓN NOCTURNA:")
        print("   1. Si es de día, cubrir parcialmente la cámara para simular oscuridad")
        print("   2. Durante el test, variar la iluminación si es posible")
        print("   3. Observar si la cámara cambia automáticamente a modo IR")
        input("\nPresione Enter para iniciar el test de visión nocturna...")
        
        night_result = detector.test_night_vision_transition(args.night_duration)
        print(f"\n📊 Análisis de visión nocturna: {json.dumps(night_result, indent=2)}")
    
    # Guardar configuración
    if args.save_config:
        config_file = detector.save_configuration()
        print(f"\n💾 Configuración guardada en: {config_file}")
    
    print("\n✅ Configuración completada")
    
    # Mostrar parámetros finales
    print(f"\n🔧 PARÁMETROS FINALES:")
    print(f"   Sensibilidad: {detector.sensitivity}")
    print(f"   Umbral: {detector.threshold_value}")
    print(f"   Área mínima: {detector.min_contour_area}")
    print(f"   Filtro Gaussiano: {detector.gaussian_blur_size}")

if __name__ == "__main__":
    main()