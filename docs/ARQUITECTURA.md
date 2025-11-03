# Arquitectura del Sistema de Detección de Infracciones de Tránsito

## 📋 Índice
- [Visión General](#visión-general)
- [Componentes Principales](#componentes-principales)
- [Flujo de Datos](#flujo-de-datos)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Relaciones entre Componentes](#relaciones-entre-componentes)

---

## 🎯 Visión General

El **Sistema Inteligente de Detección de Infracciones de Tránsito** es una plataforma distribuida basada en microservicios que combina tecnologías de:
- **Visión por Computadora (Computer Vision)** para detección de vehículos
- **Aprendizaje Automático (Machine Learning)** para reconocimiento de placas y clasificación
- **IoT** para integración con cámaras de tráfico
- **Backend administrativo** para gestión de datos y usuarios

### Arquitectura de Alto Nivel

```
┌──────────────────────────────────────────────────────────────────┐
│                       CAPA DE PRESENTACIÓN                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐     ┌──────────────────┐                   │
│  │ Frontend Dashboard│     │  Django Admin   │                   │
│  │  (Next.js/React) │     │     Panel       │                   │
│  │   Puerto: 3000   │     │   Puerto: 8000  │                   │
│  └─────────┬─────────┘     └────────┬─────────┘                   │
│            │                        │                             │
└────────────┼────────────────────────┼─────────────────────────────┘
             │                        │
             │    ┌──────────────────┐│
             │    │   API Gateway    ││
             └───►│  (Nginx/Traefik) ││◄───┐
                  └──────────┬────────┘    │
                             │             │
┌────────────────────────────┼─────────────┼────────────────────────┐
│                    CAPA DE SERVICIOS                              │
├────────────────────────────┼─────────────┼────────────────────────┤
│                            │             │                        │
│  ┌────────────────────────▼─┐     ┌─────▼──────────────────────┐ │
│  │   Django Backend         │     │  FastAPI Inference Service │ │
│  │   (Admin & REST API)     │     │    (Detección ML)          │ │
│  │   Puerto: 8000           │     │    Puerto: 8001            │ │
│  │                          │     │                            │ │
│  │ • Gestión de Usuarios    │     │ • Procesamiento Video RTSP │ │
│  │ • CRUD Infracciones      │     │ • Detección con YOLOv8     │ │
│  │ • CRUD Vehículos         │     │ • OCR de Placas (EasyOCR)  │ │
│  │ • CRUD Dispositivos      │     │ • Tracking de Vehículos    │ │
│  │ • Reportes               │     │ • Cálculo de Velocidad     │ │
│  │ • Notificaciones         │     │ • Publicación de Eventos   │ │
│  │ • Autenticación JWT      │     │ • Almacenamiento Evidencia │ │
│  └─────────┬────────────────┘     └──────────┬─────────────────┘ │
│            │                                  │                   │
└────────────┼──────────────────────────────────┼───────────────────┘
             │                                  │
             │        ┌────────────┐            │
             └───────►│ RabbitMQ   │◄───────────┘
                      │  Message   │
                      │   Broker   │
                      └─────┬──────┘
                            │
┌───────────────────────────┼────────────────────────────────────────┐
│              CAPA DE SERVICIOS ESPECIALIZADOS                      │
├───────────────────────────┼────────────────────────────────────────┤
│                           │                                        │
│  ┌────────────────────────▼─────────────────────────────┐         │
│  │           ML Service (Python)                        │         │
│  │     Análisis Avanzado de Violaciones                 │         │
│  │                                                       │         │
│  │  • ViolationDetector   (Detección de infracciones)  │         │
│  │  • SpeedAnalyzer       (Análisis de velocidad)      │         │
│  │  • LaneDetector        (Detección de carriles)      │         │
│  │  • PlateRecognizer     (OCR avanzado de placas)     │         │
│  │  • VehicleTracker      (Seguimiento de vehículos)   │         │
│  │  • NotificationSystem  (Sistema de notificaciones)  │         │
│  └──────────────────────────────────────────────────────┘         │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
             │                      │                      │
             ▼                      ▼                      ▼
┌────────────────────────────────────────────────────────────────────┐
│                      CAPA DE PERSISTENCIA                          │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐│
│  │ PostgreSQL   │  │    Redis     │  │       MinIO/S3           ││
│  │   (v16)      │  │   (Cache)    │  │  (Object Storage)        ││
│  │              │  │              │  │                          ││
│  │ • Usuarios   │  │ • Sesiones   │  │ • Videos (Evidencia)     ││
│  │ • Vehículos  │  │ • Cache API  │  │ • Snapshots (Imágenes)   ││
│  │ • Infracc.   │  │ • WebSocket  │  │ • Modelos ML             ││
│  │ • Devices    │  │ • Temp Data  │  │ • Calibraciones Cámara   ││
│  │ • Zonas      │  │              │  │                          ││
│  └──────────────┘  └──────────────┘  └──────────────────────────┘│
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────────┐
│                      CAPA DE HARDWARE / IoT                        │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │        EZVIZ H6C Pro 2K - Cámaras de Tráfico                 │ │
│  │        (Múltiples cámaras distribuidas)                      │ │
│  │                                                               │ │
│  │  • Protocolo: RTSP (Real-Time Streaming Protocol)           │ │
│  │  • Resolución: 2K (2560×1440)                               │ │
│  │  • FPS: 25-30 frames por segundo                            │ │
│  │  • Visión Nocturna: Sí (IR)                                 │ │
│  │  • PTZ: Pan, Tilt, Zoom                                     │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Componentes Principales

### 1. **Backend Django** 🐍
**Responsabilidad:** Sistema de administración y API REST principal

**Funcionalidades:**
- Gestión de usuarios y autenticación (JWT)
- CRUD de entidades: dispositivos, zonas, vehículos, conductores, infracciones
- Generación de reportes
- Notificaciones en tiempo real
- Integración con SUNARP (consulta de datos vehiculares)
- Panel administrativo Django Admin

**Puerto:** 8000  
**Base de Datos:** PostgreSQL  
**Documentación:** [BACKEND-DJANGO.md](./BACKEND-DJANGO.md)

---

### 2. **Inference Service (FastAPI)** 🚀
**Responsabilidad:** Procesamiento en tiempo real de video e inferencia ML

**Funcionalidades:**
- Conexión a streams RTSP de cámaras
- Detección de vehículos con YOLOv8
- Reconocimiento de placas con OCR (EasyOCR)
- Tracking de vehículos (DeepSORT)
- Cálculo de velocidad
- Detección de infracciones básicas
- Publicación de eventos a RabbitMQ
- Almacenamiento de evidencia en MinIO

**Puerto:** 8001  
**Modelos ML:** YOLOv8n, EasyOCR  
**Documentación:** [INFERENCE-SERVICE.md](./INFERENCE-SERVICE.md)

---

### 3. **ML Service** 🤖
**Responsabilidad:** Análisis avanzado de violaciones y machine learning

**Módulos:**
- **ViolationDetector:** Detección integral de infracciones (velocidad, carril, sentido contrario, etc.)
- **SpeedAnalyzer:** Análisis de velocidad con calibración de cámara
- **LaneDetector:** Detección de invasión de carril
- **PlateRecognizer:** OCR avanzado con validación de formato
- **VehicleTracker:** Tracking persistente con DeepSORT
- **NotificationSystem:** Sistema de notificaciones

**Documentación:** [ML-SERVICE.md](./ML-SERVICE.md)

---

### 4. **Frontend Dashboard** 💻
**Responsabilidad:** Interfaz web de usuario para operadores y supervisores

**Funcionalidades:**
- Dashboard con métricas en tiempo real
- Visualización de infracciones
- Mapa de tráfico
- Monitoreo de cámaras en vivo
- Gráficos y analíticas
- Gestión de dispositivos
- Configuración del sistema

**Puerto:** 3000  
**Tecnología:** Next.js 14, React, TypeScript, TailwindCSS  
**Documentación:** [FRONTEND-DASHBOARD.md](./FRONTEND-DASHBOARD.md)

---

### 5. **Infraestructura** 🏗️

#### PostgreSQL 16
- Base de datos relacional principal
- Almacena: usuarios, vehículos, infracciones, dispositivos, zonas, conductores
- Puerto: 5432

#### Redis 7
- Cache de sesiones
- Cache de respuestas API
- Datos temporales de WebSocket
- Puerto: 6379

#### RabbitMQ 3.12
- Message broker para comunicación asíncrona
- Colas: `infractions.detected`, `vehicles.tracked`, `plates.recognized`
- Puerto: 5672 (AMQP), 15672 (Management UI)

#### MinIO
- Object storage compatible con S3
- Buckets: `traffic-snapshots`, `traffic-videos`, `ml-models`
- Puerto: 9000 (API), 9001 (Console)

**Documentación:** [INFRASTRUCTURE.md](./INFRASTRUCTURE.md)

---

## 🔄 Flujo de Datos

### Flujo de Detección de Infracciones

```
1. CÁMARA IoT (EZVIZ)
   │
   │ Stream RTSP
   ▼
2. INFERENCE SERVICE (FastAPI)
   │
   ├─► Decodifica frames
   ├─► Detección YOLOv8 (vehículos)
   ├─► Tracking DeepSORT
   ├─► OCR EasyOCR (placas)
   └─► Cálculo de velocidad
   │
   │ Eventos detectados
   ▼
3. RABBITMQ
   │
   │ Mensaje: infraction.detected
   ▼
4. ML SERVICE
   │
   ├─► ViolationDetector (validación)
   ├─► Clasificación de severidad
   └─► Almacena evidencia en MinIO
   │
   │ API Call
   ▼
5. BACKEND DJANGO
   │
   ├─► Guarda infracción en PostgreSQL
   ├─► Enriquece con datos SUNARP
   └─► Crea notificación
   │
   │ WebSocket / API
   ▼
6. FRONTEND DASHBOARD
   │
   └─► Muestra alerta en tiempo real
```

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 5.0** - Framework web Python
- **Django REST Framework 3.14** - API REST
- **FastAPI 0.110** - Framework asíncrono para inferencia
- **Python 3.11+**

### Machine Learning
- **YOLOv8** (Ultralytics) - Detección de objetos
- **EasyOCR / PaddleOCR** - Reconocimiento de texto
- **OpenCV** - Procesamiento de video
- **NumPy** - Cálculos numéricos

### Frontend
- **Next.js 14** - Framework React
- **TypeScript** - Tipado estático
- **TailwindCSS** - Estilos
- **Recharts** - Gráficos

### Bases de Datos
- **PostgreSQL 16** - Base de datos relacional
- **Redis 7** - Cache en memoria

### Infraestructura
- **Docker** - Contenedores
- **Docker Compose** - Orquestación
- **RabbitMQ 3.12** - Message broker
- **MinIO** - Object storage

---

## 🔗 Relaciones entre Componentes

### 1. Backend Django ↔️ Inference Service
- **Comunicación:** HTTP REST API + RabbitMQ
- **Dirección:** Bidireccional
- **Propósito:** 
  - Django solicita inicio/parada de streams
  - Inference publica eventos de detección
  - Django consulta estado de dispositivos

### 2. Inference Service ↔️ ML Service
- **Comunicación:** RabbitMQ (eventos), módulos Python compartidos
- **Dirección:** Inference → ML (principalmente)
- **Propósito:**
  - Inference usa módulos de ML Service (ViolationDetector, PlateRecognizer)
  - ML valida y enriquece detecciones

### 3. Backend Django ↔️ Frontend Dashboard
- **Comunicación:** HTTP REST API + WebSocket
- **Dirección:** Bidireccional
- **Propósito:**
  - Frontend consume API REST
  - WebSocket para actualizaciones en tiempo real
  - CRUD de todas las entidades

### 4. Todos los servicios ↔️ PostgreSQL
- **Comunicación:** TCP/IP (puerto 5432)
- **Propósito:** Persistencia de datos

### 5. Todos los servicios ↔️ Redis
- **Comunicación:** Redis Protocol
- **Propósito:** Cache, sesiones, datos temporales

### 6. Inference Service / ML Service ↔️ MinIO
- **Comunicación:** S3 API (HTTP)
- **Propósito:** Almacenamiento de videos, imágenes, modelos ML

---

## 📊 Responsabilidades por Componente

| Componente | Responsabilidad Principal | Detecta Infracciones |
|------------|--------------------------|----------------------|
| **Backend Django** | Administración, persistencia, reportes | ❌ No |
| **Inference Service** | Procesamiento en tiempo real, detección básica | ✅ Sí (Básico) |
| **ML Service** | Análisis avanzado, validación, clasificación | ✅ Sí (Avanzado) |
| **Frontend Dashboard** | Visualización, interfaz de usuario | ❌ No |

### 🎯 **RESPONSABLE PRINCIPAL DE DETECCIÓN DE INFRACCIONES**

El **componente encargado de la detección de infracciones** es:

#### **ML Service - Módulo ViolationDetector** 🏆

**Ubicación:** `ml-service/src/violations/violation_detector.py`

**Razones:**
1. ✅ Contiene la lógica completa de detección de violaciones
2. ✅ Implementa reglas de negocio (límites de velocidad, carriles, etc.)
3. ✅ Clasifica tipos de infracción (velocidad, carril, luz roja, etc.)
4. ✅ Determina severidad (menor, moderada, severa, crítica)
5. ✅ Valida y filtra falsos positivos
6. ✅ Recopila evidencia y metadatos

**Tipos de Infracciones Detectadas:**
- 🏎️ `SPEED_VIOLATION` - Exceso de velocidad
- 🛣️ `LANE_VIOLATION` - Invasión de carril
- ⬅️ `WRONG_WAY` - Sentido contrario
- 🚦 `RED_LIGHT` - Paso con luz roja
- 🛑 `STOP_SIGN` - No detención en STOP
- ↪️ `ILLEGAL_TURN` - Giro ilegal
- 🅿️ `PARKING_VIOLATION` - Estacionamiento ilegal
- 📏 `FOLLOWING_DISTANCE` - Distancia de seguimiento insuficiente

**Flujo de Detección:**
```python
Inference Service (captura video)
    ↓
ML Service - ViolationDetector.detect_violations()
    ↓
ML Service - ViolationDetector.classify_severity()
    ↓
Backend Django (guarda en DB)
    ↓
Frontend Dashboard (muestra alerta)
```

---

## 📝 Documentos Adicionales

- [Backend Django](./BACKEND-DJANGO.md) - Detalle del sistema administrativo
- [Inference Service](./INFERENCE-SERVICE.md) - Servicio de procesamiento en tiempo real
- [ML Service](./ML-SERVICE.md) - Módulos de machine learning
- [Frontend Dashboard](./FRONTEND-DASHBOARD.md) - Interfaz de usuario
- [Infrastructure](./INFRASTRUCTURE.md) - Bases de datos y servicios
- [Flujos de Detección](./FLUJOS-DETECCION.md) - Diagramas de secuencia

---

**Última actualización:** Noviembre 2025  
**Versión del sistema:** 1.0.0
