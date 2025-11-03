# Inference Service - Servicio de Inferencia en Tiempo Real

## 📋 Índice
- [Visión General](#visión-general)
- [Arquitectura](#arquitectura)
- [Funcionalidades](#funcionalidades)
- [Pipeline de Procesamiento](#pipeline-de-procesamiento)
- [APIs](#apis)
- [Modelos ML Utilizados](#modelos-ml-utilizados)
- [Integración con Otros Componentes](#integración-con-otros-componentes)
- [Configuración](#configuración)

---

## 🎯 Visión General

El **Inference Service** es un microservicio desarrollado en **FastAPI** responsable del procesamiento en tiempo real de streams de video provenientes de las cámaras de tráfico. Es el componente que realiza la **detección inicial** de vehículos y placas.

**Responsabilidades principales:**
- ✅ Conexión a streams RTSP de cámaras
- ✅ Detección de vehículos con YOLOv8
- ✅ Reconocimiento de placas con OCR
- ✅ Tracking de vehículos con DeepSORT
- ✅ Cálculo básico de velocidad
- ✅ Captura de evidencia (snapshots)
- ✅ Publicación de eventos a RabbitMQ
- ✅ Almacenamiento en MinIO

**Tecnologías:**
- FastAPI 0.110
- Python 3.11+
- Ultralytics YOLOv8
- EasyOCR
- OpenCV
- NumPy

**Puerto:** 8001  
**URL Base:** `http://localhost:8001`

---

## 🏗️ Arquitectura

### Estructura del Proyecto

```
inference-service/
├── app/
│   ├── main.py                  # Entry point FastAPI
│   ├── __init__.py
│   │
│   ├── core/                    # Configuración core
│   │   ├── __init__.py
│   │   ├── config.py           # Settings
│   │   └── logging.py          # Logger
│   │
│   ├── api/                     # Endpoints REST
│   │   ├── __init__.py
│   │   ├── routes.py           # Rutas principales
│   │   ├── health.py           # Health check
│   │   └── stream.py           # Stream management
│   │
│   ├── services/                # Servicios
│   │   ├── __init__.py
│   │   ├── model_service.py    # Gestión de modelos ML
│   │   ├── stream.py           # Stream processor
│   │   └── django_api.py       # Cliente API Django
│   │
│   ├── models/                  # Schemas Pydantic
│   │   ├── __init__.py
│   │   ├── detection.py        # Detection models
│   │   └── infraction.py       # Infraction models
│   │
│   └── utils/                   # Utilidades
│       ├── __init__.py
│       ├── video.py            # Video utilities
│       └── storage.py          # MinIO client
│
├── models/                      # Modelos ML
│   └── yolov8n.pt              # YOLOv8 nano
│
├── calibration/                 # Calibraciones de cámara
│   └── camera_calibrations.json
│
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## ⚙️ Funcionalidades

### 1. **Gestión de Streams de Video**

#### Conexión RTSP
- Conexión a cámaras EZVIZ vía protocolo RTSP
- Reconexión automática en caso de fallo
- Gestión de múltiples streams simultáneos
- Decodificación con OpenCV/FFmpeg

**Formato RTSP:**
```
rtsp://username:password@192.168.1.100:554/h264_stream
```

#### Control de Streams
- `POST /streams/start/{device_id}` - Iniciar procesamiento
- `POST /streams/stop/{device_id}` - Detener procesamiento
- `GET /streams/status/{device_id}` - Estado actual

---

### 2. **Detección de Vehículos (YOLOv8)**

**Modelo:** YOLOv8n (nano) - Optimizado para velocidad

**Clases detectadas:**
- `car` (automóvil)
- `truck` (camión)
- `bus` (autobús)
- `motorcycle` (motocicleta)
- `bicycle` (bicicleta)

**Proceso:**
1. Captura frame del stream
2. Preprocesamiento (resize, normalización)
3. Inferencia con YOLOv8
4. Post-procesamiento (NMS - Non-Maximum Suppression)
5. Filtrado por confianza (threshold: 0.5)

**Output:**
```python
Detection:
  - bbox: [x1, y1, x2, y2]
  - confidence: 0.92
  - class_id: 2 (car)
  - class_name: "car"
```

---

### 3. **Tracking de Vehículos (DeepSORT)**

**Propósito:** Mantener identidad de vehículos a través de frames

**Algoritmo:** DeepSORT (Deep Simple Online Realtime Tracking)

**Características:**
- Asigna ID único a cada vehículo
- Mantiene tracking incluso con oclusiones temporales
- Calcula trayectoria del vehículo
- Permite cálculo de velocidad

**Output:**
```python
TrackedVehicle:
  - track_id: 42
  - bbox: [x1, y1, x2, y2]
  - confidence: 0.89
  - class_name: "car"
  - trajectory: [[x1,y1], [x2,y2], ...]
  - frames_tracked: 45
```

---

### 4. **Reconocimiento de Placas (OCR)**

**Tecnología:** EasyOCR (alternativa: PaddleOCR)

**Pipeline:**
1. **Detección de región de placa** en el vehículo (YOLOv8 o modelo específico)
2. **Extracción del ROI** (Region of Interest)
3. **Preprocesamiento:**
   - Conversión a escala de grises
   - Ajuste de contraste
   - Binarización
   - Reducción de ruido
4. **OCR con EasyOCR**
5. **Validación de formato** (placas peruanas)
6. **Post-procesamiento** (corrección de caracteres comunes)

**Formatos válidos:**
- `ABC-123` (3 letras, 3 números)
- `AB-1234` (2 letras, 4 números)
- `A12-345` (1 letra, 2 números, 3 números)

**Output:**
```python
PlateRecognition:
  - plate_text: "ABC-123"
  - confidence: 0.87
  - bbox: [x1, y1, x2, y2]
  - format_valid: True
```

**Correcciones automáticas:**
- `0` ↔ `O`
- `1` ↔ `I`
- `5` ↔ `S`
- `8` ↔ `B`

---

### 5. **Cálculo de Velocidad**

**Método:** Estimación basada en calibración de cámara

**Requisitos:**
- Calibración previa de la cámara
- Líneas de referencia en la zona
- Tracking de vehículo en múltiples frames

**Fórmula simplificada:**
```python
velocidad_kmh = (distancia_metros / tiempo_segundos) * 3.6
```

**Proceso:**
1. Detectar vehículo cruzando línea de inicio
2. Trackear hasta línea de fin
3. Calcular tiempo transcurrido
4. Aplicar calibración de cámara para distancia real
5. Calcular velocidad

**Precisión:**
- Diurna: ±5 km/h
- Nocturna: ±8 km/h

---

### 6. **Captura de Evidencia**

#### Snapshots (Imágenes)
- Captura frame completo
- Captura crop del vehículo
- Captura crop de la placa
- Anotaciones visuales (bboxes, IDs, velocidad)

**Formato:** JPEG (calidad 85%)  
**Resolución:** Original del stream

#### Videos
- Grabación de 10 segundos (5s antes, 5s después del evento)
- Codec: H.264
- Compresión adaptativa

**Almacenamiento:** MinIO (S3-compatible)

**Buckets:**
- `traffic-snapshots` - Imágenes
- `traffic-videos` - Videos
- `evidence` - Evidencia de infracciones

---

### 7. **Publicación de Eventos**

**Message Broker:** RabbitMQ

**Colas:**

#### `infractions.detected`
Publicado cuando se detecta una posible infracción

```json
{
  "event_type": "infraction_detected",
  "timestamp": "2025-11-02T10:30:45.123Z",
  "device_id": "CAM001",
  "zone_id": "ZN001",
  "infraction_type": "speed",
  "vehicle": {
    "track_id": 42,
    "class": "car",
    "license_plate": "ABC-123",
    "plate_confidence": 0.87
  },
  "speed": {
    "detected": 95.5,
    "limit": 60,
    "over_limit": 35.5
  },
  "evidence": {
    "snapshot_url": "minio://traffic-snapshots/2025-11-02/cam001_1234567890.jpg",
    "video_url": "minio://traffic-videos/2025-11-02/cam001_1234567890.mp4"
  },
  "metadata": {
    "detection_confidence": 0.92,
    "tracking_quality": 0.88
  }
}
```

#### `vehicles.tracked`
Publicado periódicamente con información de vehículos trackeados

```json
{
  "event_type": "vehicle_tracked",
  "timestamp": "2025-11-02T10:30:45.123Z",
  "device_id": "CAM001",
  "vehicles": [
    {
      "track_id": 42,
      "class": "car",
      "position": [320, 240],
      "velocity": 65.3,
      "trajectory_points": 45
    }
  ]
}
```

#### `plates.recognized`
Publicado cuando se reconoce una placa con éxito

```json
{
  "event_type": "plate_recognized",
  "timestamp": "2025-11-02T10:30:45.123Z",
  "device_id": "CAM001",
  "track_id": 42,
  "license_plate": "ABC-123",
  "confidence": 0.87,
  "snapshot_url": "minio://traffic-snapshots/plates/ABC-123_1234567890.jpg"
}
```

---

## 🔄 Pipeline de Procesamiento

### Flujo Completo

```
1. STREAM INPUT
   │
   │ RTSP connection
   ▼
2. FRAME CAPTURE (OpenCV)
   │
   │ Frame @ 30 FPS
   ▼
3. VEHICLE DETECTION (YOLOv8)
   │
   │ Detected vehicles: [{bbox, confidence, class}, ...]
   ▼
4. VEHICLE TRACKING (DeepSORT)
   │
   │ Tracked vehicles: [{track_id, trajectory, ...}, ...]
   ▼
5. PLATE DETECTION (YOLOv8/Specific model)
   │
   │ Plate ROI: {bbox, vehicle_id}
   ▼
6. OCR RECOGNITION (EasyOCR)
   │
   │ Plate text: "ABC-123", confidence: 0.87
   ▼
7. VALIDATION & POST-PROCESSING
   │
   │ Format validation, corrections
   ▼
8. SPEED CALCULATION (if calibrated)
   │
   │ Speed: 95.5 km/h
   ▼
9. INFRACTION DETECTION (Basic rules)
   │
   │ Is speed > limit? → Infraction
   ▼
10. EVIDENCE CAPTURE
    │
    │ Snapshot + Video segment
    ▼
11. STORAGE (MinIO)
    │
    │ Upload to S3-compatible storage
    ▼
12. EVENT PUBLISHING (RabbitMQ)
    │
    │ Publish to: infractions.detected
    ▼
13. BACKEND PROCESSING
    │
    └─► Django Backend receives event and creates record
```

### Latencia por Etapa

| Etapa | Tiempo Promedio |
|-------|----------------|
| Frame capture | 1-2 ms |
| Vehicle detection (YOLOv8) | 30-50 ms (CPU), 5-10 ms (GPU) |
| Tracking (DeepSORT) | 5-10 ms |
| Plate detection | 20-30 ms |
| OCR (EasyOCR) | 100-200 ms |
| Speed calculation | 1-2 ms |
| Evidence capture | 5-10 ms |
| Storage upload | 50-100 ms |
| Event publishing | 5-10 ms |
| **TOTAL** | **~200-400 ms** (CPU) |

---

## 🌐 APIs

### Base URL
```
http://localhost:8001
```

### Endpoints

#### 1. Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models": {
    "yolo": "loaded",
    "ocr": "loaded"
  },
  "active_streams": 3,
  "uptime": 3600
}
```

---

#### 2. Model Info
```
GET /api/v1/models/info
```

**Response:**
```json
{
  "yolo": {
    "model": "yolov8n",
    "version": "8.0.0",
    "device": "cuda:0",
    "classes": ["car", "truck", "bus", "motorcycle", "bicycle"]
  },
  "ocr": {
    "engine": "easyocr",
    "languages": ["en"],
    "gpu": true
  }
}
```

---

#### 3. Start Stream Processing
```
POST /api/v1/streams/start
```

**Request:**
```json
{
  "device_id": "CAM001",
  "rtsp_url": "rtsp://user:pass@192.168.1.100:554/h264_stream",
  "zone_id": "ZN001",
  "speed_limit": 60,
  "enable_ocr": true,
  "enable_speed": true
}
```

**Response:**
```json
{
  "status": "started",
  "device_id": "CAM001",
  "stream_id": "stream_123",
  "message": "Stream processing started successfully"
}
```

---

#### 4. Stop Stream Processing
```
POST /api/v1/streams/stop/{device_id}
```

**Response:**
```json
{
  "status": "stopped",
  "device_id": "CAM001",
  "frames_processed": 12543,
  "vehicles_detected": 342,
  "infractions_detected": 5
}
```

---

#### 5. Stream Status
```
GET /api/v1/streams/status/{device_id}
```

**Response:**
```json
{
  "device_id": "CAM001",
  "status": "active",
  "fps": 28.5,
  "frames_processed": 12543,
  "vehicles_detected": 342,
  "plates_recognized": 287,
  "infractions_detected": 5,
  "uptime": 3600,
  "last_frame_time": "2025-11-02T10:30:45.123Z"
}
```

---

#### 6. Process Single Image
```
POST /api/v1/detect/image
```

**Request:** Multipart form-data
- `image`: File (JPEG/PNG)
- `enable_ocr`: Boolean
- `speed_limit`: Integer (opcional)

**Response:**
```json
{
  "vehicles": [
    {
      "bbox": [100, 150, 300, 400],
      "confidence": 0.92,
      "class": "car",
      "license_plate": "ABC-123",
      "plate_confidence": 0.87
    }
  ],
  "processing_time_ms": 245
}
```

---

## 🤖 Modelos ML Utilizados

### 1. YOLOv8 Nano
**Archivo:** `models/yolov8n.pt`  
**Propósito:** Detección de vehículos  
**Tamaño:** ~6 MB  
**Velocidad:** ~30-50 ms/frame (CPU), ~5-10 ms/frame (GPU)  
**Precisión:** mAP@0.5 ~37%

**Clases COCO relevantes:**
- ID 2: car
- ID 5: bus
- ID 7: truck
- ID 3: motorcycle
- ID 1: bicycle

---

### 2. EasyOCR
**Lenguajes:** Español/Inglés  
**Propósito:** Reconocimiento de placas  
**Velocidad:** ~100-200 ms/placa  
**Precisión:** ~85-90% en condiciones óptimas

**Configuración:**
```python
reader = easyocr.Reader(
    lang_list=['en'],
    gpu=True,
    model_storage_directory='models/ocr',
    download_enabled=True,
    detector=True,
    recognizer=True
)
```

---

## 🔗 Integración con Otros Componentes

### 1. Inference Service → Backend Django
**Protocolo:** HTTP REST API

**Llamadas:**
- `GET /api/devices/{id}/` - Obtener info de dispositivo
- `POST /api/infractions/` - Crear infracción

---

### 2. Inference Service → RabbitMQ
**Protocolo:** AMQP

**Colas producidas:**
- `infractions.detected`
- `vehicles.tracked`
- `plates.recognized`

---

### 3. Inference Service → MinIO
**Protocolo:** S3 API (HTTP)

**Operaciones:**
- `PUT` - Subir snapshots y videos
- `GET` - Recuperar evidencia

---

### 4. Cámaras EZVIZ → Inference Service
**Protocolo:** RTSP

**Conexión:**
```python
cap = cv2.VideoCapture(
    "rtsp://admin:password@192.168.1.100:554/h264_stream"
)
```

---

## 🔧 Configuración

### Variables de Entorno

```bash
# Service
APP_NAME=Traffic Inference Service
VERSION=1.0.0
HOST=0.0.0.0
PORT=8001
DEBUG=True
LOG_LEVEL=INFO
WORKERS=4

# ML Models
YOLO_MODEL_PATH=models/yolov8n.pt
OCR_LANGUAGES=en
OCR_GPU=True
INFERENCE_DEVICE=cpu  # cpu or cuda

# Database
DATABASE_URL=postgresql://postgres:postgres123!@postgres:5432/traffic_system

# Redis
REDIS_URL=redis://redis:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://admin:SecurePassword123!@rabbitmq:5672/

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=SecurePassword123!
MINIO_USE_SSL=False

# Processing
MAX_CONCURRENT_STREAMS=10
FRAME_SKIP=0  # Process every N frames (0 = process all)
DETECTION_CONFIDENCE=0.5
OCR_CONFIDENCE=0.6
```

---

## 📊 Responsabilidades

### ✅ Sí gestiona:
- Conexión a streams RTSP
- Detección de vehículos (YOLOv8)
- Tracking de vehículos (DeepSORT)
- OCR de placas (EasyOCR)
- Cálculo básico de velocidad
- Captura de evidencia
- Almacenamiento en MinIO
- Publicación de eventos

### ❌ No gestiona:
- Validación avanzada de infracciones (→ ML Service)
- Clasificación de severidad (→ ML Service)
- Persistencia en base de datos (→ Backend Django)
- Interfaz de usuario (→ Frontend Dashboard)
- Gestión de usuarios (→ Backend Django)

### 🎯 Rol en Detección de Infracciones

El Inference Service realiza la **detección inicial y básica** de infracciones:
- Detecta cuando un vehículo excede el límite de velocidad
- Identifica vehículos sin placa visible
- Captura evidencia del momento

**Sin embargo**, la **validación y clasificación avanzada** la realiza el **ML Service** (ViolationDetector).

---

**Ver también:**
- [ARQUITECTURA.md](./ARQUITECTURA.md) - Visión general
- [ML-SERVICE.md](./ML-SERVICE.md) - Detección avanzada
- [BACKEND-DJANGO.md](./BACKEND-DJANGO.md) - Sistema administrativo
- [FLUJOS-DETECCION.md](./FLUJOS-DETECCION.md) - Flujos completos

---

**Última actualización:** Noviembre 2025
