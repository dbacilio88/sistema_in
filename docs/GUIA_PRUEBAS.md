# Guía de Pruebas - Detección con Bounding Boxes

## Pre-requisitos

### 1. Servicios Necesarios

```bash
# Verificar que los servicios estén corriendo
docker-compose ps

# Deberías ver:
# - postgres       (puerto 5432)
# - redis          (puerto 6379)
# - rabbitmq       (puerto 5672)
```

### 2. Modelos de ML

```bash
# Verificar que los modelos YOLOv8 estén descargados
ls -la inference-service/models/

# Deberías ver:
# yolov8n.pt   (Nano - rápido)
# yolov8s.pt   (Small - balance)
# yolov8m.pt   (Medium - preciso)
```

### 3. Cámaras Configuradas

```bash
# Verificar que haya cámaras con RTSP URL configurado
cd backend-django
python manage.py shell

>>> from devices.models import Device
>>> cameras = Device.objects.filter(device_type='camera')
>>> for cam in cameras:
...     print(f"{cam.name}: {cam.rtsp_url}")
```

## Iniciar los Servicios

### Paso 1: Base de Datos y Servicios Backend

```bash
# Terminal 1: Iniciar Docker
docker-compose up -d postgres redis rabbitmq

# Esperar a que estén listos (30 segundos)
docker-compose logs -f postgres
# Cuando veas: "database system is ready to accept connections"
# Presiona Ctrl+C
```

### Paso 2: Backend Django

```bash
# Terminal 2: Django
cd backend-django

# Activar entorno virtual (si usas uno)
source venv/bin/activate  # Linux/Mac
# o
.\venv\Scripts\activate   # Windows

# Instalar dependencias (primera vez)
pip install -r requirements.txt

# Migraciones (primera vez)
python manage.py migrate

# Crear superusuario (primera vez)
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver 0.0.0.0:8000
```

### Paso 3: Inference Service

```bash
# Terminal 3: Inference Service
cd inference-service

# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Instalar dependencias (primera vez)
pip install -r requirements.txt

# Descargar modelo YOLOv8 (primera vez)
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Iniciar servicio
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Paso 4: Frontend

```bash
# Terminal 4: Frontend
cd frontend-dashboard

# Instalar dependencias (primera vez)
npm install

# Iniciar en desarrollo
npm run dev
```

## Verificar que Todo Funciona

### 1. Health Checks

```bash
# Django API
curl http://localhost:8000/api/health/
# Esperado: {"status": "healthy"}

# Inference Service
curl http://localhost:8001/health
# Esperado: {"status": "healthy", "models_loaded": true}

# Frontend
curl http://localhost:3000
# Esperado: HTML de la página
```

### 2. Verificar Logs

```bash
# Terminal Django: Deberías ver
# ✓ Sistema de autenticación cargado
# ✓ Modelos sincronizados
# ✓ Servidor corriendo en http://0.0.0.0:8000/

# Terminal Inference: Deberías ver
# ✓ YOLOv8 model loaded
# ✓ OCR model initialized
# ✓ Application startup complete
# ✓ Uvicorn running on http://0.0.0.0:8001

# Terminal Frontend: Deberías ver
# ✓ ready - started server on 0.0.0.0:3000
# ✓ Local: http://localhost:3000
```

## Prueba del Sistema

### Opción 1: Prueba con Cámara Real

#### 1.1 Configurar Cámara en Django Admin

```bash
# Abrir navegador
http://localhost:8000/admin/

# Login con el superusuario creado
# Ir a: Devices → Devices → Add Device

# Completar:
Name: Cámara Principal
Code: CAM-001
Device Type: camera
Status: active
RTSP URL: rtsp://usuario:password@192.168.1.100:554/stream1
Resolution: 1920x1080
FPS: 30
Zone: [Seleccionar una zona]

# Guardar
```

#### 1.2 Abrir Dashboard de Monitoreo

```bash
# Abrir navegador
http://localhost:3000/realtime
```

#### 1.3 Iniciar Transmisión

1. En la página, verás la lista de cámaras
2. Busca "Cámara Principal" (CAM-001)
3. Click en la cámara para seleccionarla
4. Click en el botón "Play" (▶) o "Iniciar Transmisión"

#### 1.4 Verificar Detecciones

Deberías ver:
- ✅ Video en tiempo real de la cámara
- ✅ Recuadros verdes alrededor de vehículos detectados
- ✅ Etiquetas con: tipo de vehículo, confianza, placa (si es legible)
- ✅ Stats overlay mostrando FPS y número de detecciones
- ✅ Indicador verde de "Conectado"

### Opción 2: Prueba con Video de Ejemplo

Si no tienes una cámara RTSP disponible:

#### 2.1 Descargar Video de Prueba

```bash
# Desde el directorio raíz
mkdir -p test-data

# Descargar video de ejemplo (traffic)
# Opción 1: YouTube-DL
youtube-dl "https://www.youtube.com/watch?v=MNn9qKG2UFI" -o test-data/traffic.mp4

# Opción 2: Usar archivo MP4 existente
# Copiar cualquier video de tráfico a test-data/traffic.mp4
```

#### 2.2 Crear Servidor RTSP Local

```bash
# Opción 1: MediaMTX (recomendado)
# Descargar desde: https://github.com/bluenviron/mediamtx/releases

# Windows
mediamtx.exe

# Linux/Mac
./mediamtx

# Configurar para servir el video en loop
# Editar mediamtx.yml:
paths:
  test:
    source: record
    sourceOnDemand: yes
    sourceOnDemandStartTimeout: 10s
    sourceOnDemandCloseAfter: 10s
```

#### 2.3 Transmitir Video a RTSP

```bash
# Usando FFmpeg
ffmpeg -re -stream_loop -1 \
  -i test-data/traffic.mp4 \
  -c:v copy \
  -f rtsp rtsp://localhost:8554/test
```

#### 2.4 Configurar Cámara con RTSP Local

```bash
# En Django Admin
RTSP URL: rtsp://localhost:8554/test
```

### Opción 3: Prueba con WebSocket Directo

Para pruebas técnicas sin UI:

#### 3.1 Crear Script de Prueba

```python
# test_websocket.py
import asyncio
import websockets
import json
import base64
import cv2

async def test_stream():
    # Conectar al WebSocket
    uri = "ws://localhost:8001/stream/ws/camera/test-device?camera_url=rtsp://localhost:8554/test"
    
    async with websockets.connect(uri) as websocket:
        print("✓ Conectado al WebSocket")
        
        # Enviar configuración
        config = {
            "type": "config",
            "config": {
                "confidence_threshold": 0.7,
                "enable_ocr": True,
                "enable_speed": True,
                "infractions": ["speeding"],
                "speed_limit": 60
            }
        }
        await websocket.send(json.dumps(config))
        print("✓ Configuración enviada")
        
        # Recibir frames
        frame_count = 0
        while frame_count < 30:  # Primeros 30 frames
            message = await websocket.recv()
            data = json.loads(message)
            
            if data.get("type") == "frame":
                frame_count += 1
                detections = data.get("detections", [])
                
                print(f"\nFrame {frame_count}:")
                print(f"  Detecciones: {len(detections)}")
                
                for det in detections:
                    print(f"    - {det['vehicle_type']}: {det['confidence']:.2f}")
                    if 'license_plate' in det:
                        print(f"      Placa: {det['license_plate']}")
                    if 'speed' in det:
                        print(f"      Velocidad: {det['speed']:.1f} km/h")

asyncio.run(test_stream())
```

#### 3.2 Ejecutar Prueba

```bash
python test_websocket.py
```

Deberías ver:
```
✓ Conectado al WebSocket
✓ Configuración enviada

Frame 1:
  Detecciones: 2
    - car: 0.95
      Placa: ABC123
      Velocidad: 45.2 km/h
    - truck: 0.88

Frame 2:
  Detecciones: 3
    - car: 0.92
...
```

## Verificación de Funcionalidades

### ✅ Checklist de Pruebas

- [ ] **Conexión WebSocket exitosa**
  - Indicador verde en UI
  - No errores en console

- [ ] **Video streaming**
  - Frames se actualizan continuamente
  - FPS > 20

- [ ] **Detección de vehículos**
  - Recuadros verdes aparecen
  - Etiquetas con tipo de vehículo

- [ ] **OCR de placas**
  - Placas legibles se muestran
  - Confianza > 0.7

- [ ] **Estimación de velocidad**
  - Velocidad se calcula después de ~10 frames
  - Valor razonable (0-120 km/h)

- [ ] **Registro de infracciones**
  - Cuando velocidad > límite, se registra
  - Aparece en Django Admin → Infractions

- [ ] **Performance**
  - CPU < 80%
  - Memoria < 2GB
  - Sin lag en UI

## Solución de Problemas

### Problema: WebSocket no conecta

```bash
# Verificar que Inference Service está corriendo
curl http://localhost:8001/health

# Verificar logs
cd inference-service
tail -f logs/app.log

# Verificar firewall
sudo ufw allow 8001  # Linux
# o configurar Windows Firewall
```

### Problema: No detecta vehículos

```bash
# Verificar modelo YOLOv8
cd inference-service
python -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt'); print(model.names)"

# Debería imprimir:
# {0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', ...}

# Verificar que el video tiene vehículos
# Abrir el RTSP en VLC:
# Media → Open Network Stream → rtsp://localhost:8554/test
```

### Problema: Recuadros no se dibujan

```bash
# Verificar en Console del navegador (F12)
# Deberías ver mensajes:
# "WebSocket connected for device XXX"
# "Received frame with N detections"

# Si no aparecen, verificar:
# 1. URL del WebSocket en VideoPlayerWithDetection.tsx
# 2. CORS en Inference Service
# 3. Formato de mensajes JSON
```

### Problema: Baja performance

```bash
# Opción 1: Reducir process_interval
# En VideoPlayerWithDetection.tsx:
config.process_interval = 3  # Procesa cada 3 frames

# Opción 2: Usar modelo más ligero
# En inference-service/app/services/model_service.py:
self.model = YOLO('yolov8n.pt')  # Nano (más rápido)

# Opción 3: Reducir resolución de cámara
# En Django Admin → Device:
Resolution: 1280x720  # En lugar de 1920x1080
```

### Problema: OCR no lee placas

```bash
# Verificar instalación de EasyOCR
pip install easyocr

# Descargar modelos
python -c "import easyocr; reader = easyocr.Reader(['es', 'en'])"

# Ajustar confianza mínima
# En inference-service/app/services/model_service.py:
if license_confidence > 0.5:  # Reducir umbral
```

## Logs y Debugging

### Ver logs en tiempo real

```bash
# Terminal 1: Django
cd backend-django
python manage.py runserver  # Ver en consola

# Terminal 2: Inference Service
cd inference-service
tail -f logs/app.log

# Terminal 3: Frontend
cd frontend-dashboard
npm run dev  # Ver en consola

# Terminal 4: Browser Console
# F12 → Console
# Filtrar por "WebSocket" o "detection"
```

### Guardar logs para análisis

```bash
# Crear directorio de logs
mkdir -p logs/test-$(date +%Y%m%d-%H%M%S)

# Capturar logs
cd backend-django
python manage.py runserver > ../logs/test-*/django.log 2>&1 &

cd ../inference-service
python -m uvicorn app.main:app --reload > ../logs/test-*/inference.log 2>&1 &

cd ../frontend-dashboard
npm run dev > ../logs/test-*/frontend.log 2>&1 &
```

## Métricas de Éxito

Para considerar la prueba exitosa, verifica:

| Métrica | Valor Esperado | Cómo Verificar |
|---------|----------------|----------------|
| FPS | > 20 | Stats overlay en UI |
| Detecciones | > 0 (si hay vehículos) | Contador en UI |
| Confianza | > 0.7 | Etiquetas en bounding boxes |
| Latencia | < 200ms | Console logs |
| Memoria | < 2GB | `htop` o Task Manager |
| CPU | < 80% | `htop` o Task Manager |

## Siguientes Pasos

Una vez que las pruebas básicas funcionen:

1. **Calibrar velocidades** - Ajustar parámetros de estimación
2. **Entrenar modelo personalizado** - Usar imágenes de tus cámaras
3. **Optimizar performance** - Usar GPU si está disponible
4. **Configurar alertas** - Notificaciones en tiempo real
5. **Agregar más cámaras** - Escalar a múltiples streams

## Recursos Adicionales

- **Documentación YOLOv8**: https://docs.ultralytics.com/
- **FastAPI WebSocket**: https://fastapi.tiangolo.com/advanced/websockets/
- **Canvas API**: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API
- **Docker Compose**: https://docs.docker.com/compose/
