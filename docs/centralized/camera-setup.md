# 📹 EZVIZ H6C Pro 2K - Guía de Configuración

## 🎯 Objetivo
Configurar cámara EZVIZ H6C Pro 2K para obtener stream RTSP estable con resolución 2K @ 30fps, visión nocturna automática y control PTZ.

## 📋 Especificaciones Técnicas
- **Modelo**: EZVIZ H6C Pro 2K (CS-H6C-3M2WFR)
- **Resolución**: 2560x1440 (2K)
- **Frame Rate**: 30 fps
- **Conectividad**: Wi-Fi 2.4GHz/5GHz, Ethernet
- **Visión Nocturna**: IR automática hasta 30m
- **PTZ**: Pan 340°, Tilt 80°, Zoom 4x digital
- **Protocolos**: ONVIF, RTSP, HTTP

## 🔧 Configuración Inicial

### 1. Instalación App EZVIZ
```bash
# Android/iOS
Descargar: EZVIZ app desde App Store/Google Play
Crear cuenta: usuario@email.com
```

### 2. Emparejamiento de Cámara
```bash
# Pasos en la app
1. Conectar cámara a corriente (LED azul parpadeando)
2. Escanear QR code en base de cámara
3. Configurar Wi-Fi: SSID y password
4. Esperar LED azul fijo (conexión exitosa)
```

### 3. Configuración de Red

#### IP Estática en Router
```bash
# Acceder a router (ejemplo: 192.168.1.1)
# Configurar DHCP Reservation:
MAC Address: [Obtener de app EZVIZ]
IP Address: 192.168.1.100
Gateway: 192.168.1.1
DNS: 8.8.8.8, 8.8.4.4
```

#### Configuración Wi-Fi
```bash
Network: [Tu SSID]
Security: WPA2-PSK
Password: [Tu password WiFi]
Channel: Auto (recomendado canal 1, 6, o 11 para 2.4GHz)
```

## 🎥 Configuración RTSP

### 1. Habilitar RTSP en App EZVIZ
```bash
# En app EZVIZ:
1. Seleccionar cámara
2. Settings > Advanced Settings
3. Network > RTSP
4. Enable RTSP: ON
5. RTSP Port: 554 (default)
6. RTSP Authentication: ON
```

### 2. Credenciales RTSP
```bash
Usuario: admin
Password: [Configurar password personalizado - mínimo 8 caracteres]
Recomendado: Abc123456
```

### 3. URLs RTSP
```bash
# Stream Principal (2K)
rtsp://admin:Abc123456@192.168.1.100:554/h264/ch1/main/av_stream

# Stream Secundario (720p - menor latencia)
rtsp://admin:Abc123456@192.168.1.100:554/h264/ch1/sub/av_stream

# Stream con audio
rtsp://admin:Abc123456@192.168.1.100:554/h264_ulaw/ch1/main/av_stream
```

## 🧪 Pruebas de Funcionamiento

### 1. Prueba con VLC Media Player
```bash
# Windows
vlc.exe rtsp://admin:Abc123456@192.168.1.100:554/h264/ch1/main/av_stream

# Linux
vlc rtsp://admin:Abc123456@192.168.1.100:554/h264/ch1/main/av_stream
```

### 2. Prueba con FFmpeg
```bash
# Verificar stream
ffprobe -v quiet -print_format json -show_streams rtsp://admin:Abc123456@192.168.1.100:554/h264/ch1/main/av_stream

# Capturar frame
ffmpeg -i rtsp://admin:Abc123456@192.168.1.100:554/h264/ch1/main/av_stream -vframes 1 test_frame.jpg
```

### 3. Prueba con OpenCV (Python)
```python
import cv2
import numpy as np
from datetime import datetime

def test_rtsp_connection():
    """Probar conexión RTSP con OpenCV"""
    rtsp_url = "rtsp://admin:Abc123456@192.168.1.100:554/h264/ch1/main/av_stream"
    
    print(f"🔗 Conectando a: {rtsp_url}")
    cap = cv2.VideoCapture(rtsp_url)
    
    # Configurar propiedades
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reducir latencia
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    if not cap.isOpened():
        print("❌ Error: No se pudo conectar al stream RTSP")
        return False
    
    # Propiedades del stream
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"✅ Conexión exitosa")
    print(f"📐 Resolución: {width}x{height}")
    print(f"🎬 FPS: {fps}")
    
    # Leer frames por 30 segundos
    start_time = datetime.now()
    frame_count = 0
    
    while (datetime.now() - start_time).seconds < 30:
        ret, frame = cap.read()
        
        if not ret:
            print("⚠️ Warning: No se pudo leer frame")
            continue
            
        frame_count += 1
        
        # Mostrar frame cada 30 frames (1 segundo)
        if frame_count % 30 == 0:
            elapsed = (datetime.now() - start_time).seconds
            print(f"⏱️ {elapsed}s - Frame {frame_count} recibido")
            
            # Guardar frame de prueba
            cv2.imwrite(f"test_frame_{elapsed}s.jpg", frame)
    
    cap.release()
    
    actual_fps = frame_count / 30
    print(f"📊 FPS Real: {actual_fps:.2f}")
    print(f"✅ Test completado - {frame_count} frames recibidos")
    
    return actual_fps >= 25  # Al menos 25 FPS para considerar exitoso

if __name__ == "__main__":
    test_rtsp_connection()
```

## 🌙 Configuración Visión Nocturna

### 1. En App EZVIZ
```bash
# Settings > Image > Night Vision
Mode: Auto
IR LED: On
Sensitivity: Medium
Switch Time: 18:00-06:00
```

### 2. Validación Automática
```python
import cv2
import numpy as np

def test_night_vision():
    """Detectar si visión nocturna está activa"""
    rtsp_url = "rtsp://admin:Abc123456@192.168.1.100:554/h264/ch1/main/av_stream"
    cap = cv2.VideoCapture(rtsp_url)
    
    ret, frame = cap.read()
    if not ret:
        return False
    
    # Convertir a escala de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Calcular brillo promedio
    brightness = np.mean(gray)
    
    # Detectar si imagen es en IR (tonos grises uniformes)
    is_ir_active = brightness < 100 and np.std(gray) > 20
    
    print(f"🌙 Brillo promedio: {brightness:.2f}")
    print(f"🔍 Visión nocturna activa: {'Sí' if is_ir_active else 'No'}")
    
    cap.release()
    return is_ir_active
```

## 🎛️ Control PTZ con ONVIF

### 1. Instalación de Dependencias
```bash
pip install onvif-zeep
```

### 2. Configuración ONVIF
```python
from onvif import ONVIFCamera

def setup_onvif_camera():
    """Configurar control PTZ via ONVIF"""
    try:
        # Crear conexión ONVIF
        camera = ONVIFCamera(
            host='192.168.1.100',
            port=80,  # Puerto HTTP para ONVIF
            user='admin',
            passwd='Abc123456'
        )
        
        # Obtener servicios
        media_service = camera.create_media_service()
        ptz_service = camera.create_ptz_service()
        
        # Obtener perfil de media
        profiles = media_service.GetProfiles()
        profile = profiles[0]
        
        print(f"✅ ONVIF conectado")
        print(f"📹 Perfil: {profile.Name}")
        
        return camera, ptz_service, profile.token
        
    except Exception as e:
        print(f"❌ Error ONVIF: {e}")
        return None, None, None

def test_ptz_movement():
    """Probar movimiento PTZ"""
    camera, ptz_service, profile_token = setup_onvif_camera()
    
    if not ptz_service:
        return False
    
    try:
        # Mover cámara (Pan: -1 a 1, Tilt: -1 a 1, Zoom: -1 a 1)
        request = ptz_service.create_type('ContinuousMove')
        request.ProfileToken = profile_token
        request.Velocity = {
            'PanTilt': {'x': 0.5, 'y': 0},  # Pan derecha
            'Zoom': {'x': 0}
        }
        
        print("🔄 Moviendo cámara a la derecha...")
        ptz_service.ContinuousMove(request)
        
        import time
        time.sleep(2)  # Mover por 2 segundos
        
        # Detener movimiento
        stop_request = ptz_service.create_type('Stop')
        stop_request.ProfileToken = profile_token
        ptz_service.Stop(stop_request)
        
        print("✅ Movimiento PTZ exitoso")
        return True
        
    except Exception as e:
        print(f"❌ Error PTZ: {e}")
        return False
```

## 🏃‍♂️ Detección de Movimiento

### 1. Configuración en App
```bash
# Settings > Smart Detection > Motion Detection
Enable: ON
Sensitivity: Medium (50%)
Detection Area: Full frame
Notification: ON
Recording: ON (5 min clips)
```

### 2. Validación con OpenCV
```python
import cv2
import numpy as np

def test_motion_detection():
    """Detectar movimiento en stream"""
    rtsp_url = "rtsp://admin:Abc123456@192.168.1.100:554/h264/ch1/main/av_stream"
    cap = cv2.VideoCapture(rtsp_url)
    
    # Leer primer frame como referencia
    ret, frame1 = cap.read()
    if not ret:
        return False
    
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
    
    motion_detected = False
    frame_count = 0
    
    print("🔍 Detectando movimiento (mover algo frente a la cámara)...")
    
    while frame_count < 300:  # 10 segundos a 30fps
        ret, frame2 = cap.read()
        if not ret:
            continue
            
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)
        
        # Diferencia entre frames
        diff = cv2.absdiff(gray1, gray2)
        thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
        
        # Contar píxeles que cambiaron
        motion_pixels = cv2.countNonZero(thresh)
        motion_percentage = (motion_pixels / (thresh.shape[0] * thresh.shape[1])) * 100
        
        if motion_percentage > 0.5:  # 0.5% de la imagen cambió
            if not motion_detected:
                print(f"🚨 Movimiento detectado! ({motion_percentage:.2f}% de cambio)")
                motion_detected = True
        
        gray1 = gray2.copy()
        frame_count += 1
    
    cap.release()
    return motion_detected
```

## 📊 Verificación Final

### Script de Validación Completa
```python
#!/usr/bin/env python3
"""
Script de validación completa para EZVIZ H6C Pro 2K
"""

import cv2
import numpy as np
import time
from datetime import datetime
import sys

def validate_ezviz_camera():
    """Validación completa de la cámara EZVIZ"""
    print("🚀 Iniciando validación EZVIZ H6C Pro 2K...")
    
    results = {
        'rtsp_connection': False,
        'resolution_2k': False,
        'fps_30': False,
        'night_vision': False,
        'motion_detection': False,
        'ptz_control': False
    }
    
    # 1. Conexión RTSP
    print("\n1️⃣ Probando conexión RTSP...")
    results['rtsp_connection'] = test_rtsp_connection()
    
    # 2. Resolución 2K
    print("\n2️⃣ Verificando resolución 2K...")
    results['resolution_2k'] = test_resolution()
    
    # 3. FPS 30
    print("\n3️⃣ Validando 30 FPS...")
    results['fps_30'] = test_fps()
    
    # 4. Visión Nocturna
    print("\n4️⃣ Probando visión nocturna...")
    results['night_vision'] = test_night_vision()
    
    # 5. Detección de Movimiento
    print("\n5️⃣ Validando detección de movimiento...")
    results['motion_detection'] = test_motion_detection()
    
    # 6. Control PTZ
    print("\n6️⃣ Probando control PTZ...")
    results['ptz_control'] = test_ptz_movement()
    
    # Resumen
    print("\n📋 RESUMEN DE VALIDACIÓN")
    print("=" * 50)
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test.replace('_', ' ').title()}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\n🎯 Éxito: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("✅ EZVIZ H6C Pro 2K configurada correctamente")
        return True
    else:
        print("❌ Configuración incompleta - revisar fallos")
        return False

if __name__ == "__main__":
    validate_ezviz_camera()
```

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. No se puede conectar al stream RTSP
```bash
Causa: RTSP no habilitado o credenciales incorrectas
Solución:
1. Verificar RTSP habilitado en app EZVIZ
2. Confirmar usuario: admin, password: Abc123456
3. Probar IP estática: ping 192.168.1.100
```

#### 2. Latencia alta o frames perdidos
```bash
Causa: Buffer de OpenCV muy grande
Solución:
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reducir buffer
cap.set(cv2.CAP_PROP_FPS, 30)        # Forzar 30 FPS
```

#### 3. Visión nocturna no funciona
```bash
Causa: Configuración automática deshabilitada
Solución:
1. App EZVIZ > Image > Night Vision > Auto
2. Verificar horario: 18:00-06:00
3. Probar manualmente: Force IR On
```

#### 4. PTZ no responde
```bash
Causa: ONVIF deshabilitado o puerto incorrecto
Solución:
1. Habilitar ONVIF en configuración avanzada
2. Usar puerto 80 para HTTP/ONVIF
3. Verificar credenciales admin/Abc123456
```

### Comandos de Diagnóstico
```bash
# Ping a cámara
ping 192.168.1.100

# Probar puertos
nmap -p 554,80,8000 192.168.1.100

# Verificar stream con curl
curl -v rtsp://admin:Abc123456@192.168.1.100:554/h264/ch1/main/av_stream

# Test de ancho de banda
iperf3 -c 192.168.1.100 -p 5201
```

## 📝 Checklist de Configuración

- [ ] Cámara conectada a Wi-Fi (LED azul fijo)
- [ ] IP estática asignada: 192.168.1.100
- [ ] RTSP habilitado con credenciales admin/Abc123456
- [ ] Stream 2K @ 30fps funcionando
- [ ] Visión nocturna automática configurada
- [ ] Detección de movimiento activa
- [ ] Control PTZ via ONVIF operativo
- [ ] Validación completa exitosa (>80% tests)

## 🚀 Siguiente Paso
Una vez completada esta configuración, la cámara estará lista para integración con el **inference-service** FastAPI para procesamiento de video en tiempo real.