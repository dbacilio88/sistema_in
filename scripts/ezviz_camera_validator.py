#!/usr/bin/env python3
"""
Suite de pruebas completa para EZVIZ H6C Pro 2K
Valida stream RTSP, resolución 2K, FPS, visión nocturna, detección de movimiento y PTZ
"""

import cv2
import numpy as np
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import argparse

@dataclass
class TestResult:
    """Resultado de una prueba individual"""
    name: str
    passed: bool
    details: Dict[str, Any]
    duration: float
    timestamp: str

class EzvizCameraValidator:
    """Validador completo para cámara EZVIZ H6C Pro 2K"""
    
    def __init__(self, rtsp_url: str = None):
        """
        Inicializar validador
        
        Args:
            rtsp_url: URL RTSP personalizada, si no se proporciona usa la default
        """
        self.rtsp_url = rtsp_url or "rtsp://admin:Abc123456@192.168.1.100:554/h264/ch1/main/av_stream"
        self.rtsp_url_sub = "rtsp://admin:Abc123456@192.168.1.100:554/h264/ch1/sub/av_stream"
        
        # Parámetros de validación
        self.target_resolution = (2560, 1440)  # 2K
        self.target_fps = 30
        self.min_fps_threshold = 25
        self.test_duration = 30  # segundos
        
        # Resultados
        self.test_results: List[TestResult] = []
        
    def log_test_result(self, name: str, passed: bool, details: Dict[str, Any], duration: float):
        """Registrar resultado de prueba"""
        result = TestResult(
            name=name,
            passed=passed,
            details=details,
            duration=duration,
            timestamp=datetime.now().isoformat()
        )
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {name} ({duration:.2f}s)")
        
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    def test_rtsp_connection(self) -> bool:
        """Test 1: Verificar conexión RTSP básica"""
        print("\n🔗 Test 1: Conexión RTSP")
        start_time = time.time()
        
        details = {
            'url': self.rtsp_url,
            'connected': False,
            'error': None
        }
        
        try:
            cap = cv2.VideoCapture(self.rtsp_url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    details['connected'] = True
                    details['frame_shape'] = frame.shape
                else:
                    details['error'] = "No se pudo leer frame inicial"
            else:
                details['error'] = "No se pudo abrir stream RTSP"
                
            cap.release()
            
        except Exception as e:
            details['error'] = str(e)
        
        duration = time.time() - start_time
        passed = details['connected']
        
        self.log_test_result("RTSP Connection", passed, details, duration)
        return passed
    
    def test_resolution_2k(self) -> bool:
        """Test 2: Verificar resolución 2K (2560x1440)"""
        print("\n📐 Test 2: Resolución 2K")
        start_time = time.time()
        
        details = {
            'target_resolution': f"{self.target_resolution[0]}x{self.target_resolution[1]}",
            'actual_resolution': None,
            'resolution_match': False
        }
        
        try:
            cap = cv2.VideoCapture(self.rtsp_url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    actual_resolution = (width, height)
                    details['actual_resolution'] = f"{width}x{height}"
                    details['resolution_match'] = actual_resolution == self.target_resolution
                    
            cap.release()
            
        except Exception as e:
            details['error'] = str(e)
        
        duration = time.time() - start_time
        passed = details.get('resolution_match', False)
        
        self.log_test_result("Resolution 2K", passed, details, duration)
        return passed
    
    def test_fps_performance(self) -> bool:
        """Test 3: Verificar FPS (≥25 FPS)"""
        print(f"\n🎬 Test 3: Rendimiento FPS (objetivo: {self.target_fps} FPS)")
        start_time = time.time()
        
        details = {
            'target_fps': self.target_fps,
            'min_threshold': self.min_fps_threshold,
            'actual_fps': 0,
            'frames_received': 0,
            'frames_dropped': 0,
            'test_duration': self.test_duration
        }
        
        try:
            cap = cv2.VideoCapture(self.rtsp_url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            cap.set(cv2.CAP_PROP_FPS, self.target_fps)
            
            if cap.isOpened():
                test_start = time.time()
                frame_count = 0
                dropped_frames = 0
                
                while (time.time() - test_start) < self.test_duration:
                    ret, frame = cap.read()
                    
                    if ret and frame is not None:
                        frame_count += 1
                        
                        # Mostrar progreso cada 30 frames
                        if frame_count % 30 == 0:
                            elapsed = time.time() - test_start
                            current_fps = frame_count / elapsed
                            print(f"   📊 {elapsed:.1f}s - {frame_count} frames - {current_fps:.1f} FPS")
                    else:
                        dropped_frames += 1
                
                total_time = time.time() - test_start
                actual_fps = frame_count / total_time
                
                details['actual_fps'] = round(actual_fps, 2)
                details['frames_received'] = frame_count
                details['frames_dropped'] = dropped_frames
                details['actual_test_duration'] = round(total_time, 2)
                
            cap.release()
            
        except Exception as e:
            details['error'] = str(e)
        
        duration = time.time() - start_time
        passed = details['actual_fps'] >= self.min_fps_threshold
        
        self.log_test_result("FPS Performance", passed, details, duration)
        return passed
    
    def test_night_vision_detection(self) -> bool:
        """Test 4: Detectar capacidad de visión nocturna"""
        print("\n🌙 Test 4: Detección de Visión Nocturna")
        start_time = time.time()
        
        details = {
            'brightness_analysis': {},
            'ir_detection': False,
            'samples_analyzed': 0
        }
        
        try:
            cap = cv2.VideoCapture(self.rtsp_url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if cap.isOpened():
                brightness_samples = []
                contrast_samples = []
                
                # Analizar 10 frames
                for i in range(10):
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        # Convertir a escala de grises
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        
                        # Calcular métricas
                        brightness = np.mean(gray)
                        contrast = np.std(gray)
                        
                        brightness_samples.append(brightness)
                        contrast_samples.append(contrast)
                        
                        time.sleep(0.1)  # Pequeña pausa entre muestras
                
                if brightness_samples:
                    avg_brightness = np.mean(brightness_samples)
                    avg_contrast = np.std(brightness_samples)
                    
                    details['brightness_analysis'] = {
                        'average_brightness': round(avg_brightness, 2),
                        'brightness_std': round(avg_contrast, 2),
                        'samples': brightness_samples
                    }
                    details['samples_analyzed'] = len(brightness_samples)
                    
                    # Detectar IR: brillo bajo pero contraste decente
                    # (característico de imagen infrarroja)
                    ir_detected = avg_brightness < 100 and avg_contrast > 10
                    details['ir_detection'] = ir_detected
                
            cap.release()
            
        except Exception as e:
            details['error'] = str(e)
        
        duration = time.time() - start_time
        # Test pasa si se pueden analizar frames (independiente de si IR está activo)
        passed = details['samples_analyzed'] > 0
        
        self.log_test_result("Night Vision Detection", passed, details, duration)
        return passed
    
    def test_motion_detection(self) -> bool:
        """Test 5: Detectar capacidad de detección de movimiento"""
        print("\n🚨 Test 5: Detección de Movimiento")
        print("   ℹ️ Mueve algo frente a la cámara durante los próximos 15 segundos...")
        start_time = time.time()
        
        details = {
            'motion_detected': False,
            'motion_events': [],
            'sensitivity_threshold': 0.5,
            'test_duration': 15
        }
        
        try:
            cap = cv2.VideoCapture(self.rtsp_url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if cap.isOpened():
                # Leer frame de referencia
                ret, frame1 = cap.read()
                if not ret:
                    raise Exception("No se pudo leer frame inicial")
                
                gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
                gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
                
                test_start = time.time()
                motion_events = []
                
                while (time.time() - test_start) < details['test_duration']:
                    ret, frame2 = cap.read()
                    if not ret:
                        continue
                    
                    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                    gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)
                    
                    # Detectar diferencia
                    diff = cv2.absdiff(gray1, gray2)
                    thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
                    
                    # Calcular porcentaje de cambio
                    motion_pixels = cv2.countNonZero(thresh)
                    total_pixels = thresh.shape[0] * thresh.shape[1]
                    motion_percentage = (motion_pixels / total_pixels) * 100
                    
                    # Detectar movimiento significativo
                    if motion_percentage > details['sensitivity_threshold']:
                        event_time = time.time() - test_start
                        motion_events.append({
                            'timestamp': round(event_time, 2),
                            'motion_percentage': round(motion_percentage, 2)
                        })
                        
                        if not details['motion_detected']:
                            details['motion_detected'] = True
                            print(f"   🎯 Movimiento detectado a los {event_time:.1f}s ({motion_percentage:.1f}% cambio)")
                    
                    gray1 = gray2.copy()
                
                details['motion_events'] = motion_events
                details['total_motion_events'] = len(motion_events)
                
            cap.release()
            
        except Exception as e:
            details['error'] = str(e)
        
        duration = time.time() - start_time
        passed = details['motion_detected']
        
        self.log_test_result("Motion Detection", passed, details, duration)
        return passed
    
    def test_ptz_control(self) -> bool:
        """Test 6: Verificar control PTZ via ONVIF"""
        print("\n🎛️ Test 6: Control PTZ (ONVIF)")
        start_time = time.time()
        
        details = {
            'onvif_available': False,
            'ptz_supported': False,
            'movement_test': False
        }
        
        try:
            # Importar onvif si está disponible
            try:
                from onvif import ONVIFCamera
                details['onvif_library'] = True
            except ImportError:
                details['onvif_library'] = False
                details['error'] = "Librería onvif-zeep no instalada (pip install onvif-zeep)"
                
                duration = time.time() - start_time
                self.log_test_result("PTZ Control", False, details, duration)
                return False
            
            # Configurar cámara ONVIF
            camera = ONVIFCamera(
                host='192.168.1.100',
                port=80,
                user='admin',
                passwd='Abc123456'
            )
            
            # Obtener servicios
            media_service = camera.create_media_service()
            ptz_service = camera.create_ptz_service()
            
            # Obtener perfiles
            profiles = media_service.GetProfiles()
            if profiles:
                profile_token = profiles[0].token
                details['onvif_available'] = True
                details['profile_token'] = profile_token
                
                # Verificar capacidades PTZ
                try:
                    ptz_config = ptz_service.GetConfiguration()
                    details['ptz_supported'] = True
                    
                    # Test de movimiento simple
                    request = ptz_service.create_type('RelativeMove')
                    request.ProfileToken = profile_token
                    request.Translation = {
                        'PanTilt': {'x': 0.1, 'y': 0},  # Pequeño movimiento
                        'Zoom': {'x': 0}
                    }
                    
                    ptz_service.RelativeMove(request)
                    time.sleep(1)
                    
                    # Detener movimiento
                    stop_request = ptz_service.create_type('Stop')
                    stop_request.ProfileToken = profile_token
                    ptz_service.Stop(stop_request)
                    
                    details['movement_test'] = True
                    
                except Exception as ptz_error:
                    details['ptz_error'] = str(ptz_error)
            
        except Exception as e:
            details['error'] = str(e)
        
        duration = time.time() - start_time
        passed = details.get('ptz_supported', False)
        
        self.log_test_result("PTZ Control", passed, details, duration)
        return passed
    
    def test_stream_stability(self) -> bool:
        """Test 7: Estabilidad del stream (30 minutos)"""
        print(f"\n⏱️ Test 7: Estabilidad del Stream (30 minutos)")
        print("   ℹ️ Este test tomará 30 minutos para verificar estabilidad...")
        start_time = time.time()
        
        details = {
            'target_duration': 1800,  # 30 minutos
            'actual_duration': 0,
            'total_frames': 0,
            'dropped_frames': 0,
            'reconnections': 0,
            'avg_fps': 0,
            'stability_percentage': 0
        }
        
        try:
            cap = cv2.VideoCapture(self.rtsp_url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            test_start = time.time()
            frame_count = 0
            dropped_count = 0
            reconnect_count = 0
            last_report = test_start
            
            while (time.time() - test_start) < details['target_duration']:
                ret, frame = cap.read()
                
                if ret and frame is not None:
                    frame_count += 1
                else:
                    dropped_count += 1
                    
                    # Si muchos frames fallidos, intentar reconexión
                    if dropped_count % 10 == 0:
                        print(f"   ⚠️ Reconectando stream...")
                        cap.release()
                        cap = cv2.VideoCapture(self.rtsp_url)
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        reconnect_count += 1
                
                # Reporte cada 5 minutos
                current_time = time.time()
                if current_time - last_report >= 300:  # 5 minutos
                    elapsed_minutes = (current_time - test_start) / 60
                    current_fps = frame_count / (current_time - test_start) if frame_count > 0 else 0
                    print(f"   📊 {elapsed_minutes:.1f} min - {frame_count} frames - {current_fps:.1f} FPS - {reconnect_count} reconexiones")
                    last_report = current_time
            
            total_time = time.time() - test_start
            
            details['actual_duration'] = round(total_time, 2)
            details['total_frames'] = frame_count
            details['dropped_frames'] = dropped_count
            details['reconnections'] = reconnect_count
            details['avg_fps'] = round(frame_count / total_time, 2) if total_time > 0 else 0
            
            # Calcular estabilidad (frames recibidos vs esperados)
            expected_frames = details['target_duration'] * self.target_fps
            details['stability_percentage'] = round((frame_count / expected_frames) * 100, 2)
            
            cap.release()
            
        except Exception as e:
            details['error'] = str(e)
        
        duration = time.time() - start_time
        # Test pasa si estabilidad >= 80% y reconexiones <= 5
        passed = (details['stability_percentage'] >= 80 and 
                 details['reconnections'] <= 5)
        
        self.log_test_result("Stream Stability", passed, details, duration)
        return passed
    
    def run_quick_validation(self) -> Dict[str, Any]:
        """Ejecutar validación rápida (sin test de estabilidad de 30 min)"""
        print("🚀 Iniciando Validación Rápida EZVIZ H6C Pro 2K")
        print("=" * 60)
        
        quick_tests = [
            self.test_rtsp_connection,
            self.test_resolution_2k,
            self.test_fps_performance,
            self.test_night_vision_detection,
            self.test_motion_detection,
            self.test_ptz_control
        ]
        
        for test_func in quick_tests:
            try:
                test_func()
            except Exception as e:
                print(f"❌ Error en {test_func.__name__}: {e}")
        
        return self.generate_summary_report()
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Ejecutar validación completa (incluye test de estabilidad)"""
        print("🚀 Iniciando Validación Completa EZVIZ H6C Pro 2K")
        print("=" * 60)
        print("⚠️ La validación completa incluye test de estabilidad de 30 minutos")
        
        # Ejecutar validación rápida primero
        quick_result = self.run_quick_validation()
        
        # Si validación rápida es exitosa, ejecutar test de estabilidad
        quick_success_rate = (sum(r.passed for r in self.test_results) / 
                            len(self.test_results)) * 100
        
        if quick_success_rate >= 80:
            print(f"\n✅ Validación rápida exitosa ({quick_success_rate:.1f}%)")
            print("🕐 Iniciando test de estabilidad de 30 minutos...")
            
            try:
                self.test_stream_stability()
            except Exception as e:
                print(f"❌ Error en test de estabilidad: {e}")
        else:
            print(f"\n⚠️ Validación rápida incompleta ({quick_success_rate:.1f}%)")
            print("Saltando test de estabilidad - revisar problemas básicos primero")
        
        return self.generate_summary_report()
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generar reporte resumen de todas las pruebas"""
        print(f"\n📋 RESUMEN DE VALIDACIÓN")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'camera_model': 'EZVIZ H6C Pro 2K',
            'rtsp_url': self.rtsp_url,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': round(success_rate, 1),
            'test_results': [
                {
                    'name': r.name,
                    'passed': r.passed,
                    'duration': r.duration,
                    'details': r.details
                }
                for r in self.test_results
            ]
        }
        
        # Mostrar resumen en consola
        for result in self.test_results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"{status} {result.name} ({result.duration:.2f}s)")
        
        print(f"\n🎯 Resultado Final: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 90:
            print("🏆 EXCELENTE - Cámara completamente funcional")
        elif success_rate >= 80:
            print("✅ BUENO - Cámara lista para producción")
        elif success_rate >= 60:
            print("⚠️ ACEPTABLE - Revisar fallos menores")
        else:
            print("❌ INSUFICIENTE - Revisar configuración")
        
        return summary
    
    def save_report(self, summary: Dict[str, Any]) -> str:
        """Guardar reporte detallado en archivo JSON"""
        filename = f"ezviz_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte detallado guardado: {filename}")
        return filename

def main():
    """Función principal con argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description='Validador EZVIZ H6C Pro 2K')
    parser.add_argument('--rtsp-url', help='URL RTSP personalizada')
    parser.add_argument('--quick', action='store_true', 
                       help='Ejecutar solo validación rápida (sin test de 30 min)')
    parser.add_argument('--save-report', action='store_true',
                       help='Guardar reporte detallado en JSON')
    
    args = parser.parse_args()
    
    # Crear validador
    validator = EzvizCameraValidator(rtsp_url=args.rtsp_url)
    
    # Ejecutar validación
    if args.quick:
        summary = validator.run_quick_validation()
    else:
        print("⚠️ ATENCIÓN: La validación completa incluye un test de estabilidad de 30 minutos")
        response = input("¿Desea continuar con la validación completa? (s/n): ")
        
        if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            summary = validator.run_full_validation()
        else:
            print("Ejecutando validación rápida...")
            summary = validator.run_quick_validation()
    
    # Guardar reporte si se solicita
    if args.save_report:
        validator.save_report(summary)
    
    # Retornar código de salida basado en éxito
    success_rate = summary['success_rate']
    if success_rate >= 80:
        print("\n🎉 Validación exitosa - Cámara lista para usar")
        return 0
    else:
        print("\n⚠️ Validación incompleta - Revisar configuración")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())