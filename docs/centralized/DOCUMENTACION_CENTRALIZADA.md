# 📚 Documentación Centralizada - Sistema de Detección de Infracciones de Tráfico

---

## 📋 Índice General

1. [**Introducción y Visión General**](#introducción-y-visión-general)
2. [**Arquitectura del Sistema**](#arquitectura-del-sistema)
3. [**APIs y Servicios**](#apis-y-servicios)
4. [**Configuración e Instalación**](#configuración-e-instalación)
5. [**Machine Learning e IA**](#machine-learning-e-ia)
6. [**Base de Datos**](#base-de-datos)
7. [**Monitoreo en Tiempo Real**](#monitoreo-en-tiempo-real)
8. [**Operaciones y Administración**](#operaciones-y-administración)
9. [**Troubleshooting y Resolución de Problemas**](#troubleshooting-y-resolución-de-problemas)
10. [**Mejores Prácticas y Entrenamiento**](#mejores-prácticas-y-entrenamiento)
11. [**Manual de Usuario**](#manual-de-usuario)
12. [**Guías de Testing y Verificación**](#guías-de-testing-y-verificación)

---

# Introducción y Visión General

## Sistema de Detección de Infracciones de Tráfico

El Sistema de Detección de Infracciones de Tráfico está diseñado como una arquitectura de microservicios distribuida que permite escalabilidad, mantenibilidad y alta disponibilidad. El sistema combina tecnologías modernas de machine learning, procesamiento en tiempo real y interfaces de usuario intuitivas.

### Índice de Documentación del Proyecto

#### 📋 Documentación del Proyecto
- [**README Principal**](../README.md) - Introducción y guía rápida
- [**Arquitectura del Sistema**](architecture/README.md) - Diseño y componentes
- [**Plan de Desarrollo**](../specs/plan.md) - Roadmap y sprints

#### 🛠️ Documentación Técnica

##### API y Servicios
- [**API REST Backend**](api/backend-api.md) - Documentación completa de endpoints
- [**API ML Service**](api/ml-service-api.md) - Servicios de machine learning
- [**API Config Service**](api/config-service-api.md) - Gestión de configuración
- [**WebSocket APIs**](api/websocket-api.md) - Comunicación en tiempo real

##### Arquitectura y Diseño
- [**Arquitectura General**](architecture/overview.md) - Visión general del sistema
- [**Arquitectura de Microservicios**](architecture/microservices.md) - Diseño de servicios
- [**Base de Datos**](architecture/database.md) - Esquema y relaciones
- [**Seguridad**](architecture/security.md) - Implementación de seguridad

##### Desarrollo
- [**Guía de Configuración**](development/setup.md) - Configuración del entorno
- [**Estándares de Código**](development/coding-standards.md) - Convenciones y mejores prácticas
- [**Testing**](development/testing.md) - Estrategias y frameworks de pruebas
- [**Debugging**](development/debugging.md) - Herramientas y técnicas

#### 🚀 Despliegue y Operaciones

##### Despliegue
- [**Guía de Despliegue**](../deployment/README.md) - Instrucciones completas
- [**Docker y Containers**](deployment/docker.md) - Containerización
- [**Kubernetes**](deployment/kubernetes.md) - Orquestación y manifests
- [**CI/CD**](deployment/cicd.md) - Pipelines de integración continua

##### Infraestructura
- [**Terraform**](deployment/terraform.md) - Infrastructure as Code
- [**Cloud Providers**](deployment/cloud-providers.md) - AWS, Azure, GCP
- [**Monitoring**](deployment/monitoring.md) - Prometheus, Grafana, logs
- [**Backup y Recovery**](deployment/backup.md) - Estrategias de respaldo

#### 👥 Operaciones y Mantenimiento

##### Administración
- [**Guía de Administración**](operations/admin-guide.md) - Tareas administrativas
- [**Runbooks Operacionales**](operations/runbooks.md) - Procedimientos operativos
- [**Troubleshooting**](operations/troubleshooting.md) - Resolución de problemas
- [**Performance Tuning**](operations/performance.md) - Optimización

---

# Arquitectura del Sistema

## Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                          │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Web Dashboard │   Mobile App    │   Config Management UI      │
│   (React)       │   (React Native)│   (React)                   │
└─────────────────┴─────────────────┴─────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │    Load Balancer    │
                    │     (NGINX)         │
                    └──────────┬──────────┘
                               │
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                          │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Backend API   │   ML Service    │   Config Service           │
│   (Django)      │   (FastAPI)     │   (FastAPI)                │
│   Port: 8000    │   Port: 8001    │   Port: 8002               │
└─────────────────┴─────────────────┴─────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                               │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│ PostgreSQL  │   Redis     │   MinIO     │    RabbitMQ        │
│ (Primary DB)│  (Cache)    │ (Storage)   │  (Message Queue)   │
└─────────────┴─────────────┴─────────────┴─────────────────────┘
```

## Principios de Diseño

### 1. Microservicios
- **Separación de responsabilidades**: Cada servicio tiene una función específica
- **Independencia de despliegue**: Servicios pueden actualizarse independientemente
- **Escalabilidad horizontal**: Servicios se escalan según demanda
- **Tecnología heterogénea**: Cada servicio usa la tecnología más apropiada

### 2. Event-Driven Architecture
- **Comunicación asíncrona**: Eventos para operaciones no críticas
- **Desacoplamiento**: Servicios no dependen directamente unos de otros
- **Resiliencia**: Sistema continúa funcionando si un servicio falla
- **Auditabilidad**: Todos los eventos son trazables

### 3. API-First Design
- **Contratos claros**: APIs bien definidas entre servicios
- **Documentación automática**: OpenAPI/Swagger para todas las APIs
- **Versionado**: Control de versiones para evolución de APIs
- **Consistencia**: Patrones uniformes en todas las APIs

### 4. Cloud Native
- **Containerización**: Todos los servicios en Docker
- **Orquestación**: Kubernetes para gestión de contenedores
- **Observabilidad**: Métricas, logs y trazas distribuidas
- **Configuración externa**: Configuración fuera del código

## Componentes Principales

### Frontend Layer

#### 1. Web Dashboard (React)
- **Propósito**: Interfaz principal para operadores y administradores
- **Tecnologías**: React 18, TypeScript, Material-UI, React Query
- **Características**:
  - Dashboard en tiempo real con métricas
  - Gestión de infracciones y vehículos
  - Configuración del sistema
  - Reportes y análisis

#### 2. Mobile App (React Native)
- **Propósito**: Aplicación móvil para oficiales de campo
- **Tecnologías**: React Native, TypeScript, Native Base
- **Características**:
  - Captura de evidencia fotográfica
  - Consulta de vehículos e infracciones
  - Sincronización offline
  - Notificaciones push

#### 3. Config Management UI (React)
- **Propósito**: Interfaz especializada para configuración
- **Tecnologías**: React, WebSocket para tiempo real
- **Características**:
  - Configuración centralizada
  - Vista en tiempo real de cambios
  - Validación de configuraciones
  - Historial de cambios

### Application Layer

#### 1. Backend API (Django)
- **Propósito**: API principal del sistema y lógica de negocio
- **Tecnologías**: Django 4.2, Django REST Framework, Celery
- **Responsabilidades**:
  - Gestión de usuarios y autenticación
  - CRUD de infracciones, vehículos y dispositivos
  - Business logic y validaciones
  - Integración con servicios externos

---

# APIs y Servicios

## API REST Backend - Documentación Completa

### Información General

#### Base URL
- **Desarrollo**: `http://localhost:8000/api/v1`
- **Staging**: `https://staging-api.trafficsystem.com/api/v1`
- **Producción**: `https://api.trafficsystem.com/api/v1`

#### Autenticación
El sistema utiliza autenticación basada en JWT (JSON Web Tokens).

```http
Authorization: Bearer <jwt_token>
```

#### Formato de Respuesta
Todas las respuestas siguen el formato estándar:

```json
{
  "success": true|false,
  "data": <response_data>,
  "message": "Mensaje descriptivo",
  "errors": <array_of_errors>,
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

### Autenticación

#### POST /auth/login
Autenticar usuario y obtener token JWT.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "permissions": ["read", "write", "admin"]
    }
  }
}
```

## API ML Service - Documentación Técnica

### Información General

#### Base URL
- **Desarrollo**: `http://localhost:8001`
- **Staging**: `https://staging-ml.trafficsystem.com`
- **Producción**: `https://ml.trafficsystem.com`

#### Framework
FastAPI con Pydantic para validación y documentación automática.

#### Documentación Interactiva
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI Schema**: `/openapi.json`

### Endpoints de Salud

#### GET /health
Verificar estado del servicio ML.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models": {
    "license_plate_detection": {
      "status": "loaded",
      "version": "v2.1",
      "accuracy": 0.98
    },
    "vehicle_classification": {
      "status": "loaded", 
      "version": "v1.5",
      "accuracy": 0.95
    },
    "infraction_detection": {
      "status": "loaded",
      "version": "v3.0", 
      "accuracy": 0.92
    }
  },
  "gpu_available": true,
  "memory_usage": "2.1GB/8GB",
  "timestamp": "2024-01-15T14:30:00Z"
}
```

### Detección de Placas

#### POST /detect/license-plates
Detectar placas en imágenes o videos.

**Request (multipart/form-data):**
```
file: <image_or_video_file>
confidence_threshold: float (default: 0.8)
max_detections: int (default: 10)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "detections": [
      {
        "license_plate": "ABC123",
        "confidence": 0.95,
        "bbox": {
          "x": 100,
          "y": 50,
          "width": 120,
          "height": 40
        },
        "region": "Lima",
        "country": "Peru"
      }
    ],
    "processing_time_ms": 150,
    "image_dimensions": {
      "width": 1920,
      "height": 1080
    }
  }
}
```

---

# Configuración e Instalación

## 📹 EZVIZ H6C Pro 2K - Guía de Configuración

### 🎯 Objetivo
Configurar cámara EZVIZ H6C Pro 2K para obtener stream RTSP estable con resolución 2K @ 30fps, visión nocturna automática y control PTZ.

### 📋 Especificaciones Técnicas
- **Modelo**: EZVIZ H6C Pro 2K (CS-H6C-3M2WFR)
- **Resolución**: 2560x1440 (2K)
- **Frame Rate**: 30 fps
- **Conectividad**: Wi-Fi 2.4GHz/5GHz, Ethernet
- **Visión Nocturna**: IR automática hasta 30m
- **PTZ**: Pan 340°, Tilt 80°, Zoom 4x digital
- **Protocolos**: ONVIF, RTSP, HTTP

### 🔧 Configuración Inicial

#### 1. Instalación App EZVIZ
```bash
# Android/iOS
Descargar: EZVIZ app desde App Store/Google Play
Crear cuenta: usuario@email.com
```

#### 2. Emparejamiento de Cámara
```bash
# Pasos en la app
1. Conectar cámara a corriente (LED azul parpadeando)
2. Escanear QR code en base de cámara
3. Configurar Wi-Fi: SSID y password
4. Esperar LED azul fijo (conexión exitosa)
```

#### 3. Configuración de Red

##### IP Estática en Router
```bash
# Acceder a router (ejemplo: 192.168.1.1)
# Configurar DHCP Reservation:
MAC Address: [Obtener de app EZVIZ]
IP Address: 192.168.1.100
Gateway: 192.168.1.1
DNS: 8.8.8.8, 8.8.4.4
```

##### Configuración Wi-Fi
```bash
Network: [Tu SSID]
Security: WPA2-PSK
Password: [Tu password WiFi]
Channel: Auto (recomendado canal 1, 6, o 11 para 2.4GHz)
```

---

# Machine Learning e IA

## Integración ML - YOLOv8 y OCR

### Descripción

Se ha integrado exitosamente YOLOv8 para detección de vehículos en tiempo real, EasyOCR para lectura de placas vehiculares, y registro automático de infracciones en la base de datos de Django.

### Componentes Implementados

#### 1. Model Service (`inference-service/app/services/model_service.py`)

Servicio que gestiona los modelos de Machine Learning:

##### YOLOv8 - Detección de Vehículos
- **Modelo**: YOLOv8n (nano) para balance entre velocidad y precisión
- **Clases detectadas**: car, motorcycle, bus, truck
- **Configuración**:
  - Confidence threshold: 0.5 (configurable)
  - IOU threshold: 0.45
  - Ubicación modelo: `/app/models/yolov8n.pt`

##### EasyOCR - Detección de Placas
- **Idiomas**: Inglés (alphanumeric)
- **Formatos soportados** (Perú):
  - AAA-123 o AAA-1234 (3 letras + 3-4 números)
  - AB-1234 (2 letras + 4 números)
  - A12-345 (1 letra + 2 números + 3 números)
- **GPU**: Deshabilitado por defecto (configurable vía `OCR_GPU`)

##### Estimación de Velocidad
- Método: Tracking simple basado en desplazamiento de píxeles
- Requiere: Historial de detecciones (mínimo 10 frames)
- Calibración: 1 pixel ≈ 0.05 metros (ajustable con calibración de cámara)
- **Nota**: Para producción, implementar Optical Flow + Kalman Filter

#### 2. Django API Service (`inference-service/app/services/django_api.py`)

Servicio para comunicación con el backend Django:

**Funcionalidades**:
- `create_infraction()`: Crea infracciones en la base de datos
- `get_or_create_vehicle()`: Obtiene o crea vehículos
- `get_device()`: Obtiene información del dispositivo
- `get_zone()`: Obtiene información de la zona
- `upload_evidence_to_minio()`: Sube evidencia a MinIO (placeholder)

#### 3. WebSocket con Detección Real (`inference-service/app/api/websocket.py`)

Endpoint WebSocket actualizado con:

##### VehicleTracker
- Mantiene historial de detecciones por vehículo
- Máximo 30 frames de historia
- Limpieza automática de tracks antiguos

##### RealtimeDetector
**Flujo de procesamiento**:
1. Decodifica frame base64
2. Detecta vehículos con YOLOv8
3. Para cada vehículo:
   - Detecta placa con OCR (si habilitado)
   - Actualiza tracking
   - Estima velocidad (si hay suficiente historial)
   - Detecta infracciones
   - Registra en base de datos si aplica

**Tipos de infracciones detectadas**:
- ✅ **Exceso de velocidad**: Basado en estimación vs límite configurado
- 🚧 **Luz roja**: Placeholder (requiere detección de semáforos)
- 🚧 **Invasión de carril**: Placeholder (requiere detección de carriles)

### Configuración

#### Variables de Entorno (inference-service)

```env
# ML Models
YOLO_MODEL_PATH=/app/models/yolov8n.pt
YOLO_CONFIDENCE_THRESHOLD=0.5
YOLO_IOU_THRESHOLD=0.45
OCR_LANGUAGES=["en"]
OCR_GPU=false

# Django Backend API
DJANGO_API_URL=http://django:8000
DJANGO_API_TIMEOUT=30
```

### Estado Actual - Solución Temporal YOLOv8

#### 🔴 Problema con EasyOCR

EasyOCR está fallando debido a:
1. Problema con doble slash en la ruta (`/home/app/.EasyOCR//model/`)
2. Corrupción de archivos durante descarga (MD5 hash mismatch)
3. Errores de permisos en archivos temporales

#### ✅ Solución Temporal Aplicada

**Modificado**: `inference-service/app/services/model_service.py`

##### Cambios:

1. **OCR ahora es opcional** - No falla todo el servicio si OCR no funciona
2. **YOLOv8 sigue funcionando** - La detección de vehículos funciona normalmente
3. **Mensajes claros** - Se informa cuando OCR no está disponible

```python
# OCR ahora tiene try/catch separado
try:
    self.ocr_reader = await asyncio.get_event_loop().run_in_executor(
        self.executor,
        self._load_ocr_reader
    )
    logger.info("OCR reader loaded successfully")
except Exception as ocr_error:
    logger.warning(f"Failed to load OCR reader: {str(ocr_error)}")
    logger.warning("Continuing without OCR support")
    self.ocr_reader = None  # ← Permite continuar sin OCR
```

#### 🚀 Estado Actual

El servicio ya fue reconstruido y debería estar funcionando con:
- ✅ **YOLOv8** - Detección de vehículos (car, truck, bus, motorcycle)
- ⚠️ **EasyOCR** - Deshabilitado temporalmente (no detectará placas)

### Resumen de Cambios - Integración YOLOv8 y OCR

**Fecha**: 2 de Noviembre, 2025  
**Objetivo**: Reemplazar detección simulada con YOLOv8 real, integrar OCR para placas, y registrar infracciones en la base de datos.

#### ✅ Cambios Completados

##### 1. Servicio de Inferencia - Nuevas Dependencias

**Archivo**: `inference-service/requirements.txt`

**Paquetes añadidos**:
```txt
ultralytics==8.0.230    # YOLOv8 para detección de vehículos
easyocr==1.7.1          # OCR para lectura de placas
```

##### 2. Configuración ML

**Archivo**: `inference-service/app/core/config.py`

**Nuevas variables**:
```python
# ML Model Configuration
YOLO_MODEL_PATH: str = "/app/models/yolov8n.pt"
YOLO_CONFIDENCE_THRESHOLD: float = 0.5
YOLO_IOU_THRESHOLD: float = 0.45
OCR_LANGUAGES: list = ['en']
OCR_GPU: bool = False

# Django Backend API
DJANGO_API_URL: str = "http://django:8000"
DJANGO_API_TIMEOUT: int = 30
```

---

# Base de Datos

## Database Setup Guide

### PostgreSQL Configuration

#### Required Extensions

The system requires the following PostgreSQL extensions:

- **PostGIS**: Geographic data support for device locations and zones
- **TimescaleDB**: Time-series data for events and analytics  
- **uuid-ossp**: UUID generation for primary keys
- **pg_trgm**: Text search functionality
- **btree_gin**: JSONB indexing
- **pg_stat_statements**: Query monitoring
- **pgcrypto**: Additional cryptographic functions

#### Database Schema

The system creates the following schemas:

- `public`: Main application tables
- `timeseries`: TimescaleDB hypertables for time-series data
- `analytics`: Analytics and reporting tables

#### Main Tables

##### Authentication
- `authentication_customuser`: Custom user model with roles
- `authentication_loginhistory`: Login tracking for security

##### Devices & Zones
- `devices_zone`: Traffic zones with geographic boundaries
- `devices_device`: IoT cameras and sensors
- `devices_deviceevent`: Device status events (TimescaleDB)

##### Vehicles & Drivers
- `vehicles_vehicle`: Vehicle registration data
- `vehicles_driver`: Driver/person information
- `vehicles_vehicleownership`: Vehicle-driver relationships

##### Infractions
- `infractions_infraction`: Main infractions table
- `infractions_infractionevent`: Infraction lifecycle events (TimescaleDB)
- `infractions_appeal`: Appeal submissions

#### TimescaleDB Hypertables

The following tables are configured as TimescaleDB hypertables for optimal time-series performance:

- `devices_deviceevent`: Partitioned by `timestamp`
- `infractions_infractionevent`: Partitioned by `timestamp`

---

# Monitoreo en Tiempo Real

## Módulo de Monitoreo en Tiempo Real

### Descripción

Este módulo permite la detección en tiempo real de vehículos e infracciones de tránsito utilizando diferentes fuentes de video:
- Cámara web local
- Dispositivo móvil (cámara)
- Streams RTSP de cámaras IP

### Características

#### 🎥 Fuentes de Video
- **Cámara Web Local**: Acceso directo a la cámara web del computador
- **Dispositivo Móvil**: Acceso a la cámara del dispositivo móvil
- **RTSP Stream**: Conexión a cámaras IP mediante protocolo RTSP

#### 🚗 Detección de Vehículos
- Identificación de vehículos en tiempo real con recuadros verdes
- Confianza de detección mostrada en porcentaje
- Detección de placas vehiculares (OCR)

#### ⚠️ Detección de Infracciones
Los siguientes tipos de infracciones son detectados con recuadros de colores específicos:

- **Exceso de Velocidad** (Recuadro Naranja)
  - Detecta vehículos que superan el límite de velocidad configurado
  - Muestra velocidad detectada vs límite permitido
  
- **Pasarse la Luz Roja** (Recuadro Rojo)
  - Identifica vehículos que no respetan semáforos en rojo
  
- **Invasión de Carril** (Recuadro Amarillo)
  - Detecta vehículos que invaden carriles no permitidos

#### ⚙️ Configuración
- **Límite de Velocidad**: Configurable por el usuario (20-120 km/h)
- **Umbral de Confianza**: Ajustable para filtrar detecciones (50%-95%)
- **Detección de Placas (OCR)**: Activable/desactivable
- **Detección de Velocidad**: Activable/desactivable

#### 📊 Panel de Monitoreo
- Visualización del stream de video en tiempo real
- Overlay de detecciones con información detallada
- Lista de detecciones recientes con timestamps
- Métricas de rendimiento (FPS, número de detecciones)
- Estado de conexión en tiempo real

### Arquitectura Técnica

#### Frontend (`RealtimeMonitor.tsx`)
- **Framework**: React + Next.js 14 + TypeScript
- **Video API**: WebRTC (getUserMedia) para acceso a cámaras locales
- **WebSocket**: Comunicación bidireccional con el backend para inferencia
- **Canvas API**: Renderizado de detecciones sobre el video

#### Backend (Inference Service)
- **Framework**: FastAPI + WebSockets
- **Ubicación**: `inference-service/app/api/websocket.py`
- **Endpoint**: `ws://localhost:8001/api/v1/ws/inference`
- **Procesamiento**: OpenCV + NumPy para análisis de frames

#### Flujo de Datos

```
[Cámara] → [Frontend: Video Stream] → [Canvas Capture] → [Base64 Frame]
    ↓
[WebSocket Send] → [Backend: Inference Service] → [ML Models]
    ↓
[Detection Results] ← [WebSocket Receive] ← [Backend Response]
    ↓
[Canvas Overlay] → [Visual Feedback]
```

### Uso

#### 1. Acceder al Módulo
- Inicia sesión en el dashboard
- En el menú lateral, selecciona "Monitoreo en Tiempo Real"

#### 2. Seleccionar Fuente de Video
- Escoge entre: Cámara Web Local, Dispositivo Móvil o RTSP
- Para RTSP, ingresa la URL del stream (ej: `rtsp://192.168.1.10:554/stream`)

#### 3. Configurar Detección
- Ajusta el límite de velocidad según la zona
- Selecciona los tipos de infracciones a monitorear
- Configura el umbral de confianza
- Activa/desactiva OCR y detección de velocidad

#### 4. Iniciar Monitoreo
- Clic en "Iniciar Detección"
- El sistema solicitará permisos de acceso a la cámara (primera vez)
- El video comenzará a procesarse en tiempo real

#### 5. Interpretar Resultados
- **Recuadros Verdes**: Vehículos detectados sin infracciones
- **Recuadros Naranjas**: Exceso de velocidad
- **Recuadros Rojos**: Luz roja
- **Recuadros Amarillos**: Invasión de carril
- Cada detección muestra: tipo, confianza, placa (si se detecta), velocidad (si aplica)

---

# Operaciones y Administración

## Guía de Administración del Sistema

### Introducción

Esta guía proporciona las instrucciones necesarias para administrar el Sistema de Detección de Infracciones de Tráfico en un entorno de producción. Incluye tareas rutinarias, procedimientos de mantenimiento, y mejores prácticas operacionales.

### 1. Tareas de Administración Diarias

#### Verificación de Estado del Sistema

##### Script de Verificación Matutina
```bash
#!/bin/bash
# daily-check.sh - Verificación diaria del sistema

echo "=== Daily System Health Check - $(date) ==="

# 1. Verificar estado de pods
echo "1. Pod Status:"
kubectl get pods -n traffic-system --field-selector=status.phase!=Running

# 2. Verificar uso de recursos
echo "2. Resource Usage:"
kubectl top nodes
kubectl top pods -n traffic-system --sort-by=cpu

# 3. Verificar almacenamiento
echo "3. Storage Usage:"
kubectl get pvc -n traffic-system
df -h | grep -E "(disk|vol)"

# 4. Verificar servicios críticos
echo "4. Service Health:"
for service in backend ml-service config-service postgresql redis; do
  echo "Checking $service..."
  kubectl get pods -l app.kubernetes.io/component=$service -n traffic-system
done

# 5. Verificar métricas de negocio
echo "5. Business Metrics:"
curl -s http://prometheus:9090/api/v1/query?query=infractions_detected_total | jq '.data.result[0].value[1]'

# 6. Verificar alertas activas
echo "6. Active Alerts:"
curl -s http://alertmanager:9093/api/v1/alerts | jq '.data[] | select(.status.state=="firing") | .labels.alertname'

echo "=== Check Complete ==="
```

##### Dashboard de Monitoreo
Acceder diariamente a:
- **Grafana Dashboard**: `https://grafana.trafficsystem.com`
- **Prometheus Alerts**: `https://prometheus.trafficsystem.com/alerts`
- **Application Logs**: `https://kibana.trafficsystem.com`

#### Revisión de Logs

##### Logs Críticos a Revisar
```bash
# Errores en el backend
kubectl logs -l app.kubernetes.io/component=backend -n traffic-system --since=24h | grep -i error

# Errores en ML Service
kubectl logs -l app.kubernetes.io/component=ml-service -n traffic-system --since=24h | grep -i "error\|exception"

# Eventos de Kubernetes
kubectl get events -n traffic-system --sort-by='.lastTimestamp' | tail -50

# Logs de base de datos
kubectl logs traffic-system-postgresql-0 -n traffic-system --since=24h | grep -i "error\|fatal"
```

#### Limpieza de Archivos Temporales
```bash
# Limpiar archivos temporales del ML Service
kubectl exec -it deployment/traffic-system-ml-service -n traffic-system -- \
  find /tmp -name "*.jpg" -o -name "*.mp4" -mtime +1 -delete

# Limpiar logs antiguos
kubectl exec -it deployment/traffic-system-backend -n traffic-system -- \
  find /app/logs -name "*.log" -mtime +7 -delete

# Limpiar cache de Redis si es necesario
kubectl exec -it traffic-system-redis-master-0 -n traffic-system -- \
  redis-cli FLUSHDB
```

### Runbooks Operacionales

#### RB-001: Sistema Completamente Caído

##### Síntomas
- Interfaz web no responde
- APIs devuelven 503/504 errors
- Usuarios no pueden acceder al sistema

##### Tiempo Objetivo de Resolución
- **RTO**: 30 minutos
- **Escalamiento**: 15 minutos si no hay progreso

##### Procedimiento

**Paso 1: Verificación Inicial (2 minutos)**
```bash
# Verificar estado general del cluster
kubectl get nodes
kubectl get pods -A | grep -v Running

# Verificar ingress controller
kubectl get pods -n ingress-nginx
```

**Paso 2: Diagnóstico Rápido (5 minutos)**
```bash
# Verificar namespace principal
kubectl get pods -n traffic-system

# Verificar eventos recientes
kubectl get events -n traffic-system --sort-by='.lastTimestamp' | tail -20

# Verificar recursos
kubectl top nodes
kubectl get pvc -n traffic-system
```

**Paso 3: Acciones de Recuperación (10 minutos)**
```bash
# Si pods están CrashLoopBackOff
kubectl delete pod -l app.kubernetes.io/name=traffic-system -n traffic-system

# Si hay problemas de storage
kubectl get pvc -n traffic-system
kubectl describe pvc <problematic-pvc> -n traffic-system

# Si hay problemas de red
kubectl get svc -n traffic-system
kubectl describe ingress traffic-system -n traffic-system
```

**Paso 4: Escalamiento (si es necesario)**
```bash
# Activar modo de emergencia
kubectl scale deployment traffic-system-backend --replicas=10 -n traffic-system
kubectl scale deployment traffic-system-frontend --replicas=5 -n traffic-system

# Verificar auto-scaling
kubectl get hpa -n traffic-system
```

**Paso 5: Verificación de Recuperación (5 minutos)**
```bash
# Probar endpoints críticos
curl -f https://traffic-system.domain.com/health/
curl -f https://traffic-system.domain.com/api/v1/health/

# Verificar dashboard
# Acceder a Grafana y verificar métricas principales
```

**Comunicación:**
- Notificar a stakeholders inmediatamente
- Actualizar status page
- Documentar en incident ticket

---

# Troubleshooting y Resolución de Problemas

## Troubleshooting ML

### 🔴 Problemas Identificados

1. **No aparecen cuadros rojos/verdes**: Los modelos ML NO están cargados correctamente
2. **No se almacenan datos en MinIO**: El bucket `ml-models` no existe

### ✅ Soluciones Aplicadas

#### 1. Código Corregido

**Problema**: Había un error en `model_service.py` al cargar YOLO  
**Solución**: ✅ Código corregido y servicio reconstruido completamente

#### 2. Servicio Reconstruido

El servicio de inferencia ha sido reconstruido con `--no-cache` para asegurar que use el código corregido.

**Build completado**: ✅ 274 segundos (imagen: sistema_in-inference)

### 📋 Pasos para Activar la Detección

#### Paso 1: Iniciar el Servicio de Inferencia

Ejecutar en WSL/Terminal:

```bash
cd /home/bacsystem/github.com/sistema_in
docker compose up -d inference
```

**Esperado**: 
```
[+] Running 1/1
 ✔ Container traffic-inference  Started
```

#### Paso 2: Verificar que los Modelos se Carguen

Monitorear los logs en tiempo real:

```bash
docker compose logs -f inference
```

**Buscar estas líneas (debe tardar 10-30 segundos)**:

```
✅ CORRECTO:
{"event": "Initializing ML models...", "level": "info"}
{"event": "YOLO model not found, downloading...", "level": "info"}
Downloading yolov8n.pt: 100%|██████████| 6.23M/6.23M
{"event": "YOLO model loaded from /app/models/yolov8n.pt", "level": "info"}
{"event": "OCR reader loaded for languages: ['en']", "level": "info"}
{"event": "ML models initialized successfully", "level": "info"}
{"event": "Application startup complete", "level": "info"}
```

❌ **SI VES ERRORES** como `"Failed to load YOLO model"`:
- Detener: `docker compose stop inference`
- Eliminar: `docker compose rm -f inference`
- Volver a iniciar: `docker compose up -d inference`

#### Paso 3: Crear Bucket de MinIO para Modelos

```bash
# Opción 1: Usar MinIO Web UI
# 1. Abrir http://localhost:9001
# 2. Login: admin / SecurePassword123!
# 3. Click en "Buckets" → "Create Bucket"
# 4. Nombre: ml-models
# 5. Click "Create"

# Opción 2: Línea de comandos (desde WSL)
docker compose run --rm minio-init mc mb --ignore-existing myminio/ml-models
```

### Fix Completo - Permisos YOLOv8 y EasyOCR

#### 🔴 Errores Encontrados

##### Error 1: YOLOv8
```
Permission denied: '/app/models/yolov8n.pt'
```

##### Error 2: EasyOCR
```
No such file or directory: '/home/app/.EasyOCR//model/temp.zip'
```

#### ✅ Soluciones Aplicadas

**Archivo modificado**: `inference-service/Dockerfile`

##### Cambios:

```dockerfile
# ANTES:
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# DESPUÉS:
RUN useradd --create-home --shell /bin/bash app && \
    mkdir -p /app/models && \
    mkdir -p /home/app/.EasyOCR/model && \
    chown -R app:app /app && \
    chown -R app:app /home/app/.EasyOCR
USER app
```

**Explicación**:
1. `/app/models/` - Directorio para YOLOv8 (yolov8n.pt ~6MB)
2. `/home/app/.EasyOCR/model/` - Directorio para modelos OCR (~100MB)
3. Ambos directorios se crean ANTES de cambiar al usuario `app`
4. Permisos correctos asignados con `chown`

### Guía de Troubleshooting - Problemas de Conectividad

#### Frontend no puede conectar al Backend
**Síntomas:**
- Error 502 Bad Gateway
- Timeouts en requests
- "Network Error" en la interfaz

**Diagnóstico:**
```bash
# Verificar estado de servicios
kubectl get pods -n traffic-system
kubectl get svc -n traffic-system

# Verificar logs del ingress
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# Probar conectividad directa
kubectl port-forward svc/traffic-system-backend 8000:8000 -n traffic-system
curl http://localhost:8000/api/v1/health/
```

**Soluciones:**
1. **Verificar configuración de Ingress:**
   ```bash
   kubectl describe ingress traffic-system -n traffic-system
   ```

2. **Revisar DNS y configuración:**
   ```bash
   # Verificar resolución DNS
   nslookup traffic-system.yourdomain.com
   
   # Verificar certificados TLS
   kubectl get certificate -n traffic-system
   ```

3. **Reiniciar servicios:**
   ```bash
   kubectl rollout restart deployment/traffic-system-backend -n traffic-system
   ```

#### Base de Datos Inaccesible
**Síntomas:**
- Error "Unable to connect to database"
- Timeouts en queries
- 500 Internal Server Error

**Diagnóstico:**
```bash
# Verificar estado de PostgreSQL
kubectl get pods -l app.kubernetes.io/name=postgresql -n traffic-system
kubectl logs traffic-system-postgresql-0 -n traffic-system

# Probar conexión directa
kubectl exec -it traffic-system-postgresql-0 -n traffic-system -- psql -U trafficuser -d trafficdb
```

**Soluciones:**
1. **Verificar recursos:**
   ```bash
   kubectl describe pod traffic-system-postgresql-0 -n traffic-system
   kubectl top pod traffic-system-postgresql-0 -n traffic-system
   ```

2. **Revisar configuración de conexión:**
   ```bash
   kubectl get secret traffic-system-postgresql -n traffic-system -o yaml
   ```

3. **Restaurar desde backup:**
   ```bash
   # Ver procedimiento completo en backup.md
   kubectl exec -it traffic-system-postgresql-0 -n traffic-system -- \
     pg_restore -U trafficuser -d trafficdb /backup/latest.dump
   ```

#### Alto Tiempo de Respuesta en ML Service
**Síntomas:**
- Timeouts en detección de placas
- Cola de requests acumulándose
- CPU/GPU al 100%

**Diagnóstico:**
```bash
# Verificar recursos del ML Service
kubectl top pod -l app.kubernetes.io/component=ml-service -n traffic-system

# Verificar métricas de GPU
kubectl exec -it deployment/traffic-system-ml-service -n traffic-system -- nvidia-smi

# Revisar logs para errores
kubectl logs -f deployment/traffic-system-ml-service -n traffic-system
```

---

# Mejores Prácticas y Entrenamiento

## Guía de Mejores Prácticas

### Introducción

Esta guía compila las mejores prácticas para el desarrollo, operación y mantenimiento del Sistema de Detección de Infracciones de Tráfico. Las prácticas están organizadas por área funcional y nivel de experiencia.

### 🏗️ Desarrollo de Software

#### Estándares de Código

##### Python (Backend Django)

**Estructura de Archivos:**
```python
# ✅ Bueno: Importaciones organizadas
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

import requests
from django.db import models
from django.core.exceptions import ValidationError

from authentication.models import User
from vehicles.models import Vehicle

# ❌ Malo: Importaciones desordenadas
from datetime import datetime
from django.db import models
import requests
from authentication.models import User
from typing import List
```

**Documentación de Funciones:**
```python
# ✅ Bueno: Documentación completa
def detect_license_plate(image_path: str, confidence_threshold: float = 0.8) -> Dict[str, Any]:
    """
    Detecta placas vehiculares en una imagen usando ML.
    
    Args:
        image_path: Ruta absoluta a la imagen a procesar
        confidence_threshold: Umbral mínimo de confianza (0.0-1.0)
    
    Returns:
        Dict con 'plates' (lista de placas detectadas), 'confidence' y 'processing_time'
        
    Raises:
        FileNotFoundError: Si la imagen no existe
        ValidationError: Si confidence_threshold no está en rango válido
        
    Example:
        >>> result = detect_license_plate('/path/image.jpg', 0.9)
        >>> print(result['plates'])
        ['ABC123', 'XYZ789']
    """
    if not 0.0 <= confidence_threshold <= 1.0:
        raise ValidationError("Confidence threshold must be between 0.0 and 1.0")
    
    # Implementation here...
    return {
        'plates': detected_plates,
        'confidence': avg_confidence,
        'processing_time': elapsed_time
    }

# ❌ Malo: Sin documentación
def detect_license_plate(image_path, confidence_threshold=0.8):
    # Implementation without documentation
    pass
```

**Manejo de Errores:**
```python
# ✅ Bueno: Manejo específico de errores
from infractions.exceptions import ProcessingError, InsufficientConfidenceError

def process_infraction(image_data: bytes) -> Infraction:
    try:
        plates = detect_plates(image_data)
        if not plates:
            raise InsufficientConfidenceError("No plates detected with sufficient confidence")
            
        vehicle = Vehicle.objects.get(license_plate=plates[0])
        return create_infraction(vehicle, image_data)
        
    except Vehicle.DoesNotExist:
        logger.warning(f"Vehicle with plate {plates[0]} not found")
        raise ProcessingError(f"Vehicle {plates[0]} not registered")
    except Exception as e:
        logger.error(f"Unexpected error processing infraction: {e}")
        raise ProcessingError("Failed to process infraction")

# ❌ Malo: Manejo genérico
def process_infraction(image_data):
    try:
        # Complex logic here
        pass
    except Exception as e:
        print(f"Error: {e}")  # Nunca usar print en producción
```

---

# Manual de Usuario

## Manual de Usuario - Interfaz Web

### Introducción

El Sistema de Detección de Infracciones de Tráfico proporciona una interfaz web intuitiva para gestionar y monitorear infracciones de tráfico en tiempo real. Este manual te guiará a través de todas las funcionalidades disponibles.

### Acceso al Sistema

#### URL de Acceso
- **Producción**: `https://traffic-system.yourdomain.com`
- **Staging**: `https://staging.traffic-system.yourdomain.com`

#### Inicio de Sesión

1. **Acceder a la página de login**
   - Abrir navegador web
   - Navegar a la URL del sistema
   - Aparecerá la pantalla de inicio de sesión

2. **Credenciales de acceso**
   ```
   Campo: Usuario
   Descripción: Tu nombre de usuario asignado
   
   Campo: Contraseña
   Descripción: Tu contraseña personal
   ```

3. **Proceso de autenticación**
   - Introducir credenciales
   - Hacer clic en "Iniciar Sesión"
   - El sistema validará y redirigirá al dashboard principal

#### Recuperación de Contraseña

1. **Hacer clic en "¿Olvidaste tu contraseña?"**
2. **Introducir email registrado**
3. **Revisar email de recuperación**
4. **Seguir instrucciones del email**
5. **Establecer nueva contraseña**

### Dashboard Principal

#### Vista General

El dashboard principal muestra:

```
┌─────────────────────────────────────────────────────────┐
│  🚦 Sistema de Detección de Infracciones de Tráfico    │
├─────────────────────────────────────────────────────────┤
│  📊 Métricas del Día        │  🔔 Alertas Recientes     │
│  • Infracciones: 45         │  • Cámara Av. Principal   │
│  • Confirmadas: 38          │    offline hace 2 min     │
│  • Pendientes: 7            │  • High CPU en ML Service │
│  • Precisión: 94%           │    hace 5 min             │
├─────────────────────────────────────────────────────────┤
│  📈 Gráfico de Infracciones │  🗺️ Mapa de Detecciones  │
│  [Gráfico de barras]        │  [Mapa interactivo]       │
└─────────────────────────────────────────────────────────┘
```

#### Widgets Principales

##### 1. Métricas del Día
- **Infracciones Detectadas**: Total del día actual
- **Confirmadas**: Infracciones validadas
- **Pendientes**: Esperando revisión
- **Precisión**: % de detecciones correctas

##### 2. Alertas del Sistema
- **Estado de cámaras**: Online/Offline
- **Performance del sistema**: CPU, memoria, etc.
- **Errores críticos**: Fallos que requieren atención

##### 3. Gráfico de Tendencias
- **Vista temporal**: Últimas 24 horas, 7 días, 30 días
- **Tipos de infracción**: Desglose por categorías
- **Comparación**: Periodos anteriores

##### 4. Mapa de Detecciones
- **Ubicaciones en tiempo real**: Puntos de detección
- **Heat map**: Zonas con más infracciones
- **Estado de cámaras**: Visual en el mapa

### Gestión de Infracciones

#### Lista de Infracciones

##### Acceso
```
Menú Principal → Infracciones → Lista de Infracciones
```

##### Filtros Disponibles

1. **Por Estado**
   - Pendiente: Esperando validación
   - Confirmada: Validada como infracción real
   - Desestimada: No es una infracción válida

2. **Por Tipo de Infracción**
   - Exceso de velocidad
   - Luz roja
   - Invasión de carril
   - Estacionamiento indebido

3. **Por Fecha**
   - Rango de fechas personalizable
   - Filtros predefinidos (Hoy, Ayer, Última semana, Último mes)

4. **Por Ubicación**
   - Selección de zona o dispositivo específico
   - Filtro por dirección o coordenadas

---

# Guías de Testing y Verificación

## Guía de Verificación y Testing - Integración ML

### Estado Actual

✅ **Código completado**: Toda la integración de YOLOv8, EasyOCR y Django API está implementada  
🔄 **Build en progreso**: El servicio de inferencia se está reconstruyendo con las nuevas dependencias  
⚠️ **Error detectado y corregido**: Problema en la carga del modelo YOLO (línea de export removida)

### Pasos para Verificar

#### 1. Verificar que el servicio está corriendo

```bash
cd /home/bacsystem/github.com/sistema_in
docker compose ps inference
```

**Esperado**: El contenedor debe estar en estado "Up" o "Running"

#### 2. Verificar logs de inicialización

```bash
docker compose logs inference | grep -E "(Initializing|initialized|YOLO|OCR|ML models)"
```

**Esperado**:
```
INFO: Initializing ML models...
INFO: YOLO model loaded from /app/models/yolov8n.pt
INFO: OCR reader loaded for languages: ['en']
INFO: ML models initialized successfully
INFO: Application startup complete.
```

#### 3. Buscar errores

```bash
docker compose logs inference | grep -i error | tail -20
```

**Si hay errores**, revisar:
- Error de "Invalid export format": Ya fue corregido, rebuild necesario
- Error de memoria: Puede ocurrir si no hay suficiente RAM (YOLOv8n + EasyOCR ~ 2GB)
- Error de torch/CUDA: Normal si no hay GPU, debe funcionar en CPU

#### 4. Verificar que el modelo se descargó

```bash
docker exec -it traffic-inference ls -lh /app/models/
```

**Esperado**:
```
-rw-r--r-- 1 appuser appuser 6.2M Nov  2 07:29 yolov8n.pt
```

#### 5. Probar el endpoint WebSocket

Desde el navegador, abrir la consola de desarrollador (F12) y ejecutar:

```javascript
const ws = new WebSocket('ws://localhost:8001/api/ws/inference');

ws.onopen = () => {
    console.log('✅ WebSocket conectado');
    
    // Enviar configuración
    ws.send(JSON.stringify({
        type: 'config',
        data: {
            detection_types: ['speed'],
            confidence_threshold: 0.7,
            enable_ocr: true,
            enable_speed_detection: true,
            speed_limit: 60
        }
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('📩 Mensaje recibido:', data);
};

ws.onerror = (error) => {
    console.error('❌ Error:', error);
};

ws.onclose = () => {
    console.log('🔌 WebSocket cerrado');
};
```

#### 6. Probar desde el Frontend

1. **Abrir la aplicación**:
   - URL: http://localhost:3002
   - Navegar a: "Monitoreo en Tiempo Real"

2. **Configurar detección**:
   - Límite de velocidad: 60 km/h
   - Umbral de confianza: 0.7
   - Habilitar OCR: Sí (si EasyOCR funciona)
   - Habilitar detección de velocidad: Sí

3. **Iniciar detección**:
   - Seleccionar "Cámara Web Local"
   - Clic en "Iniciar Detección"
   - Permitir acceso a la cámara

4. **Verificar funcionamiento**:
   - ✅ Video se muestra en tiempo real
   - ✅ Se envían frames al WebSocket (cada ~200ms)
   - ✅ Se reciben respuestas del servicio ML
   - ✅ Se muestran detecciones si hay vehículos en el video

#### ⚠️ Troubleshooting Común

1. **Error: "Failed to load YOLO model"**
   ```bash
   docker compose restart inference
   docker compose logs -f inference
   ```

2. **Error: "OCR initialization failed"**
   - Normal si hay problemas con EasyOCR
   - YOLOv8 debe seguir funcionando sin OCR

3. **Error: "WebSocket connection failed"**
   ```bash
   docker compose ps inference
   curl http://localhost:8001/health
   ```

4. **Video no se muestra**:
   - Verificar permisos de cámara en el navegador
   - Probar en modo incógnito
   - Verificar que no hay otras apps usando la cámara

5. **No se detectan vehículos**:
   - Verificar que hay vehículos visibles en el video
   - Ajustar umbral de confianza (probar con 0.3-0.5)
   - Verificar logs del servicio ML

#### 📊 Métricas de Éxito

Una integración exitosa debe mostrar:

1. **Logs sin errores críticos**
2. **YOLOv8 model descargado** (~6.2MB)
3. **WebSocket conecta** sin errores
4. **Detección funciona** con cámara local
5. **FPS estable** (5-15 FPS típico)
6. **Detecciones precisas** en vehículos visibles

#### 🚀 Próximos Pasos

Una vez que la verificación sea exitosa:

1. **Calibrar cámara** para estimación de velocidad precisa
2. **Entrenar modelo personalizado** con placas peruanas
3. **Implementar tracking avanzado** (Kalman filter)
4. **Optimizar rendimiento** (batch processing, GPU)
5. **Agregar métricas de precisión** y dashboards

---

## Verificaciones Finales

### ✅ Checklist de Verificación Completa

- [ ] Todos los servicios están corriendo (docker compose ps)
- [ ] Logs de inicialización exitosos
- [ ] Modelos ML cargados correctamente
- [ ] WebSocket endpoint funcional
- [ ] Frontend conecta al backend
- [ ] Cámara local accesible
- [ ] Detecciones de vehículos funcionando
- [ ] Base de datos accesible
- [ ] MinIO bucket creado
- [ ] Sin errores críticos en logs

### 📋 Verificar Configuración Completa

```bash
# Verificar todos los servicios
docker compose ps

# Verificar conectividad completa
curl http://localhost:3002 # Frontend
curl http://localhost:8000/api/v1/health/ # Backend
curl http://localhost:8001/health # ML Service
curl http://localhost:9000/minio/health/live # MinIO

# Verificar base de datos
docker exec -it traffic-db psql -U trafficuser -d trafficdb -c "\dt"
```

Ejecute estos comandos para confirmar que todo el sistema está funcionando correctamente antes de proceder con el uso en producción.

---

## Conclusión

Esta documentación centralizada proporciona una vista completa de todos los aspectos del Sistema de Detección de Infracciones de Tráfico, desde la arquitectura hasta la operación diaria. Para información más detallada sobre cualquier tema específico, consulte los archivos originales en sus respectivas carpetas.

**Ubicación de archivos originales:**
- `docs/` - Documentación principal
- `docs/api/` - Documentación de APIs
- `docs/architecture/` - Arquitectura del sistema
- `docs/deployment/` - Guías de despliegue
- `docs/operations/` - Procedimientos operacionales
- `docs/training/` - Mejores prácticas y entrenamiento
- `docs/user/` - Manuales de usuario

**Última actualización:** 2 de Noviembre, 2025