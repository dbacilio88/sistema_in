# ML Service - Servicio de Machine Learning y Análisis Avanzado

## 📋 Índice
- [Visión General](#visión-general)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Módulos Principales](#módulos-principales)
- [ViolationDetector - Detector de Infracciones](#violationdetector---detector-de-infracciones)
- [Otros Módulos](#otros-módulos)
- [Relaciones con Otros Componentes](#relaciones-con-otros-componentes)
- [Configuración](#configuración)

---

## 🎯 Visión General

El **ML Service** es el componente **responsable principal de la detección y validación de infracciones de tránsito**. Contiene módulos especializados de machine learning y análisis que procesan los datos capturados por el Inference Service y los convierten en infracciones validadas.

**🏆 COMPONENTE CLAVE:** Este es el **responsable de detectar infracciones** de manera avanzada.

**Responsabilidades:**
- ✅ **Detección integral de infracciones** (velocidad, carril, luz roja, etc.)
- ✅ **Clasificación de severidad** (menor, moderada, severa, crítica)
- ✅ **Validación y filtrado de falsos positivos**
- ✅ **Análisis de velocidad con calibración**
- ✅ **Detección de invasión de carril**
- ✅ **OCR avanzado de placas**
- ✅ **Tracking persistente de vehículos**
- ✅ **Sistema de notificaciones**

**Tecnologías:**
- Python 3.11+
- NumPy, OpenCV
- Scikit-learn
- YOLOv8 (para detección)
- Deep learning models personalizados

---

## 📁 Estructura del Proyecto

```
ml-service/
├── src/
│   ├── __init__.py
│   ├── config.py                    # Configuración general
│   │
│   ├── violations/                  # 🎯 MÓDULO PRINCIPAL
│   │   ├── __init__.py
│   │   ├── violation_detector.py   # ⭐ Detector de infracciones
│   │   ├── violation_manager.py    # Gestor de violaciones
│   │   ├── lane_detector.py        # Detección de carril
│   │   ├── notification_system.py  # Sistema de notificaciones
│   │   └── README.md
│   │
│   ├── speed/                       # Análisis de velocidad
│   │   ├── __init__.py
│   │   ├── speed_analyzer.py       # Análisis de velocidad
│   │   ├── camera_calibrator.py    # Calibración de cámara
│   │   └── speed_validator.py      # Validación de velocidad
│   │
│   ├── recognition/                 # Reconocimiento de placas
│   │   ├── __init__.py
│   │   ├── plate_detector.py       # Detección de placa
│   │   ├── plate_reader.py         # OCR de placa
│   │   └── plate_validator.py      # Validación de formato
│   │
│   ├── tracking/                    # Tracking de vehículos
│   │   ├── __init__.py
│   │   ├── vehicle_tracker.py      # Tracker DeepSORT
│   │   └── trajectory_analyzer.py  # Análisis de trayectoria
│   │
│   ├── detection/                   # Detección de objetos
│   │   ├── __init__.py
│   │   ├── vehicle_detector.py     # Detector YOLOv8
│   │   └── object_classifier.py    # Clasificador
│   │
│   ├── storage/                     # Almacenamiento
│   │   ├── __init__.py
│   │   └── minio_client.py         # Cliente MinIO
│   │
│   ├── reporting/                   # Reportes y analytics
│   │   ├── __init__.py
│   │   ├── report_generator.py     # Generador de reportes
│   │   └── analytics.py            # Análisis estadístico
│   │
│   └── realtime/                    # Procesamiento en tiempo real
│       ├── __init__.py
│       └── stream_service.py       # Servicio de streams
│
├── tests/                           # Tests unitarios
├── benchmarks/                      # Benchmarks de rendimiento
├── scripts/                         # Scripts de inicialización
├── requirements.txt
└── README.md
```

---

## 🎯 Módulos Principales

### 1. **violations/ - Detección de Infracciones** 🏆

#### **violation_detector.py** ⭐ COMPONENTE PRINCIPAL

Este es el **módulo más importante** del sistema. Es el **responsable directo de detectar infracciones**.

**Clase principal:** `ViolationDetector`

**Tipos de infracciones detectadas:**

```python
class ViolationType(Enum):
    SPEED_VIOLATION = "speed_violation"           # Exceso de velocidad
    LANE_VIOLATION = "lane_violation"             # Invasión de carril
    WRONG_WAY = "wrong_way"                       # Sentido contrario
    RED_LIGHT = "red_light"                       # Paso con luz roja
    STOP_SIGN = "stop_sign"                       # No detención en STOP
    ILLEGAL_TURN = "illegal_turn"                 # Giro ilegal
    PARKING_VIOLATION = "parking_violation"       # Estacionamiento ilegal
    FOLLOWING_DISTANCE = "following_distance"     # Distancia insuficiente
```

**Niveles de severidad:**

```python
class ViolationSeverity(Enum):
    MINOR = "minor"          # Leve
    MODERATE = "moderate"    # Moderada
    SEVERE = "severe"        # Grave
    CRITICAL = "critical"    # Crítica
```

---

### 📊 Estructura de una Infracción

```python
@dataclass
class TrafficViolation:
    """Registro completo de infracción de tránsito"""
    
    # Identificación
    violation_id: str                    # UUID único
    timestamp: float                     # Momento de detección
    violation_type: ViolationType        # Tipo de infracción
    severity: ViolationSeverity          # Severidad
    
    # Vehículo
    vehicle_id: int                      # Track ID del vehículo
    license_plate: Optional[str]         # Placa detectada
    plate_confidence: Optional[float]    # Confianza del OCR
    
    # Descripción
    description: str                     # Descripción legible
    confidence: float                    # Confianza global
    
    # Ubicación
    location: ViolationLocation          # Zona, coordenadas
    
    # Datos específicos (según tipo)
    speed_limit: Optional[float]         # Límite de velocidad
    measured_speed: Optional[float]      # Velocidad medida
    
    # Evidencia
    evidence_frame: Optional[np.ndarray] # Frame completo
    vehicle_crop: Optional[np.ndarray]   # Crop del vehículo
    
    # Metadatos técnicos
    detection_confidence: float          # Confianza de detección
    tracking_quality: float              # Calidad de tracking
    weather_conditions: Optional[str]    # Clima
    lighting_conditions: Optional[str]   # Iluminación
    
    # Revisión
    camera_id: Optional[str]
    processed_by: str                    # Sistema/operador
    reviewed: bool                       # ¿Revisada?
    false_positive: bool                 # ¿Falso positivo?
```

---

## 🔍 ViolationDetector - Detector de Infracciones

### Métodos Principales

#### 1. `detect_violations()`
**Propósito:** Método principal de detección

```python
def detect_violations(
    self,
    tracked_vehicles: List[TrackedVehicle],
    frame: np.ndarray,
    speed_violations: List[SpeedViolation] = None,
    lane_info: Dict[str, Any] = None,
    traffic_lights: List[Dict] = None
) -> List[TrafficViolation]:
    """
    Detecta todas las infracciones en el frame actual.
    
    Args:
        tracked_vehicles: Vehículos trackeados
        frame: Frame actual del video
        speed_violations: Violaciones de velocidad (opcional)
        lane_info: Información de carriles (opcional)
        traffic_lights: Estado de semáforos (opcional)
    
    Returns:
        Lista de infracciones detectadas
    """
```

**Proceso:**
1. Recibe vehículos trackeados del Inference Service
2. Analiza cada vehículo:
   - ¿Excede velocidad? → `SPEED_VIOLATION`
   - ¿Invade carril? → `LANE_VIOLATION`
   - ¿Va en sentido contrario? → `WRONG_WAY`
   - ¿Pasa con luz roja? → `RED_LIGHT`
3. Clasifica severidad
4. Valida y filtra falsos positivos
5. Captura evidencia
6. Retorna lista de infracciones

---

#### 2. `detect_speed_violations()`
**Propósito:** Procesar violaciones de velocidad

```python
def detect_speed_violations(
    self,
    speed_violations: List[SpeedViolation],
    vehicles: List[TrackedVehicle],
    frame: np.ndarray
) -> List[TrafficViolation]:
    """
    Procesa violaciones de velocidad del SpeedAnalyzer.
    
    Args:
        speed_violations: Violaciones detectadas por SpeedAnalyzer
        vehicles: Vehículos trackeados actualmente
        frame: Frame actual
    
    Returns:
        Lista de infracciones de velocidad validadas
    """
```

**Proceso:**
1. Recibe violaciones de velocidad del `SpeedAnalyzer`
2. Verifica cooldown (evita múltiples detecciones del mismo vehículo)
3. Encuentra vehículo correspondiente en tracking
4. Calcula severidad según exceso:
   - Minor: +10 km/h
   - Moderate: +20 km/h
   - Severe: +40 km/h
   - Critical: +60 km/h
5. Captura evidencia (crop del vehículo)
6. Intenta reconocer placa
7. Crea registro de `TrafficViolation`

---

#### 3. `detect_lane_violations()`
**Propósito:** Detectar invasión de carril

```python
def detect_lane_violations(
    self,
    vehicles: List[TrackedVehicle],
    lane_info: Dict[str, Any],
    frame: np.ndarray
) -> List[TrafficViolation]:
    """
    Detecta vehículos que invaden carriles prohibidos.
    
    Args:
        vehicles: Vehículos trackeados
        lane_info: Información de carriles y líneas
        frame: Frame actual
    
    Returns:
        Lista de infracciones de carril
    """
```

**Proceso:**
1. Obtiene definición de carriles (líneas)
2. Para cada vehículo:
   - Calcula posición relativa a las líneas
   - Determina si está en carril correcto
   - Calcula porcentaje de invasión
3. Si invasión > threshold → Infracción
4. Clasifica severidad por grado de invasión

---

#### 4. `detect_wrong_way()`
**Propósito:** Detectar vehículos en sentido contrario

```python
def detect_wrong_way(
    self,
    vehicles: List[TrackedVehicle],
    allowed_direction: Tuple[float, float],
    frame: np.ndarray
) -> List[TrafficViolation]:
    """
    Detecta vehículos circulando en sentido contrario.
    
    Args:
        vehicles: Vehículos trackeados
        allowed_direction: Vector de dirección permitida (dx, dy)
        frame: Frame actual
    
    Returns:
        Lista de infracciones de sentido contrario
    """
```

**Proceso:**
1. Define dirección permitida (vector)
2. Para cada vehículo:
   - Calcula dirección de movimiento (basado en trayectoria)
   - Calcula ángulo con dirección permitida
   - Si ángulo > 135° → Sentido contrario
3. Verifica persistencia (no fue giro temporal)
4. Crea infracción con severidad CRITICAL

---

#### 5. `_calculate_speed_severity()`
**Propósito:** Determinar severidad de exceso de velocidad

```python
def _calculate_speed_severity(self, over_limit: float) -> ViolationSeverity:
    """
    Calcula severidad basada en exceso de velocidad.
    
    Args:
        over_limit: Km/h sobre el límite
    
    Returns:
        Nivel de severidad
    """
    if over_limit >= 60.0:
        return ViolationSeverity.CRITICAL
    elif over_limit >= 40.0:
        return ViolationSeverity.SEVERE
    elif over_limit >= 20.0:
        return ViolationSeverity.MODERATE
    else:
        return ViolationSeverity.MINOR
```

---

#### 6. `_is_in_cooldown()`
**Propósito:** Evitar detecciones duplicadas

```python
def _is_in_cooldown(
    self,
    cooldown_key: Tuple[int, ViolationType]
) -> bool:
    """
    Verifica si una infracción está en período de cooldown.
    
    Args:
        cooldown_key: (vehicle_id, violation_type)
    
    Returns:
        True si aún está en cooldown
    """
```

**Cooldown periods:**
- `SPEED_VIOLATION`: 30 segundos
- `LANE_VIOLATION`: 15 segundos
- `WRONG_WAY`: 60 segundos
- `RED_LIGHT`: 120 segundos
- `STOP_SIGN`: 60 segundos
- `ILLEGAL_TURN`: 45 segundos
- `PARKING_VIOLATION`: 300 segundos
- `FOLLOWING_DISTANCE`: 20 segundos

---

### 📊 Estadísticas del Detector

```python
self.stats = {
    "total_violations": 0,
    "violations_by_type": {
        ViolationType.SPEED_VIOLATION: 0,
        ViolationType.LANE_VIOLATION: 0,
        # ...
    },
    "violations_by_severity": {
        ViolationSeverity.MINOR: 0,
        ViolationSeverity.MODERATE: 0,
        ViolationSeverity.SEVERE: 0,
        ViolationSeverity.CRITICAL: 0
    },
    "false_positives": 0,
    "processing_times": []
}
```

---

## 🔧 Otros Módulos

### 2. **speed/ - Análisis de Velocidad**

#### **speed_analyzer.py**
**Clase:** `SpeedAnalyzer`

**Funcionalidad:**
- Mide velocidad de vehículos usando calibración de cámara
- Define zonas de medición
- Detecta violaciones de velocidad
- Calcula precisión de medición

**Métodos principales:**
```python
def analyze_speed(vehicle: TrackedVehicle) -> Optional[SpeedViolation]
def calibrate_zone(reference_points: List[Point]) -> CalibrationMatrix
def validate_speed_reading(speed: float) -> bool
```

---

#### **camera_calibrator.py**
**Clase:** `CameraCalibrator`

**Funcionalidad:**
- Calibración de cámara para medición de distancias reales
- Corrección de distorsión de lente
- Mapeo pixel → metros

**Proceso de calibración:**
1. Define puntos de referencia con distancia conocida
2. Calcula matriz de transformación
3. Permite conversión pixel → metros

---

### 3. **recognition/ - Reconocimiento de Placas**

#### **plate_detector.py**
**Clase:** `PlateDetector`

**Funcionalidad:**
- Detecta región de placa en vehículo
- Extrae ROI (Region of Interest)
- Preprocesa imagen para OCR

---

#### **plate_reader.py**
**Clase:** `PlateReader`

**Funcionalidad:**
- OCR con EasyOCR/PaddleOCR
- Post-procesamiento de texto
- Corrección de caracteres comunes

**Correcciones:**
- `0` ↔ `O`
- `1` ↔ `I`
- `5` ↔ `S`
- `8` ↔ `B`

---

#### **plate_validator.py**
**Clase:** `PlateValidator`

**Funcionalidad:**
- Valida formato de placas peruanas
- Verifica checksum (si aplica)
- Consulta base de datos de placas

**Formatos válidos:**
- `ABC-123` (3 letras, 3 números)
- `AB-1234` (2 letras, 4 números)
- `A12-345` (1 letra, 2 números, 3 números)

---

### 4. **tracking/ - Tracking de Vehículos**

#### **vehicle_tracker.py**
**Clase:** `VehicleTracker`

**Funcionalidad:**
- Tracking con algoritmo DeepSORT
- Asignación de IDs persistentes
- Manejo de oclusiones
- Análisis de trayectoria

**Características:**
```python
@dataclass
class TrackedVehicle:
    track_id: int
    bbox: Tuple[int, int, int, int]
    confidence: float
    class_name: str
    center_x: float
    center_y: float
    trajectory: List[Tuple[float, float]]
    velocity: Optional[Tuple[float, float]]
    frames_tracked: int
    last_seen: int
```

---

### 5. **detection/ - Detección de Objetos**

#### **vehicle_detector.py**
**Clase:** `VehicleDetector`

**Funcionalidad:**
- Detección con YOLOv8
- Filtrado por clase y confianza
- NMS (Non-Maximum Suppression)

---

### 6. **notifications/ - Sistema de Notificaciones**

#### **notification_system.py**
**Clase:** `NotificationSystem`

**Funcionalidad:**
- Envío de notificaciones en tiempo real
- Integración con RabbitMQ
- Alertas por tipo de infracción
- Notificaciones a operadores

**Tipos de notificación:**
- Nueva infracción crítica
- Dispositivo offline
- Error en procesamiento
- Métricas anormales

---

## 🔄 Flujo de Detección Completo

```
1. INFERENCE SERVICE
   │ Detecta vehículo con YOLOv8
   │ Trackea con DeepSORT
   │ Reconoce placa con OCR
   ▼
2. Envía a RabbitMQ
   │ Queue: vehicles.tracked
   ▼
3. ML SERVICE - ViolationDetector
   │
   ├─► SpeedAnalyzer.analyze_speed()
   │   └─► ¿Excede límite? → SPEED_VIOLATION
   │
   ├─► LaneDetector.detect_lane_violations()
   │   └─► ¿Invade carril? → LANE_VIOLATION
   │
   ├─► ViolationDetector.detect_wrong_way()
   │   └─► ¿Sentido contrario? → WRONG_WAY
   │
   ├─► ViolationDetector._calculate_severity()
   │   └─► Determina: MINOR | MODERATE | SEVERE | CRITICAL
   │
   ├─► ViolationDetector._validate_violation()
   │   └─► Filtra falsos positivos
   │
   └─► ViolationDetector._capture_evidence()
       └─► Guarda snapshot + video en MinIO
   ▼
4. Publica a RabbitMQ
   │ Queue: infractions.detected
   ▼
5. BACKEND DJANGO
   │ Consume evento
   │ Crea registro en PostgreSQL
   │ Enriquece con SUNARP
   │ Envía notificación
   ▼
6. FRONTEND DASHBOARD
   └─► Muestra alerta en tiempo real
```

---

## 🔗 Relaciones con Otros Componentes

### ML Service ← Inference Service
**Comunicación:** RabbitMQ + módulos Python compartidos

**Inference llama a:**
- `ViolationDetector.detect_violations()`
- `PlateReader.read_plate()`
- `VehicleTracker.update()`

---

### ML Service → Backend Django
**Comunicación:** HTTP REST API (para consultas), RabbitMQ (para eventos)

**ML publica eventos:**
- `infractions.detected`
- `high_severity_alert`

---

### ML Service → MinIO
**Comunicación:** S3 API

**Operaciones:**
- Upload evidencia (snapshots, videos)
- Descarga de modelos ML

---

## 🔧 Configuración

### Variables de Entorno

```bash
# ML Service Configuration
ML_SERVICE_NAME=Traffic ML Service
ML_SERVICE_VERSION=1.0.0

# Violation Detection
ENABLE_SPEED_DETECTION=True
ENABLE_LANE_DETECTION=True
ENABLE_WRONG_WAY_DETECTION=True
ENABLE_RED_LIGHT_DETECTION=False  # Requiere detector de semáforos

# Thresholds
SPEED_VIOLATION_THRESHOLD=10  # km/h sobre límite
LANE_VIOLATION_THRESHOLD=0.3  # 30% invasión
CONFIDENCE_THRESHOLD=0.7

# Cooldown Periods (segundos)
SPEED_COOLDOWN=30
LANE_COOLDOWN=15
WRONG_WAY_COOLDOWN=60
RED_LIGHT_COOLDOWN=120

# Processing
MAX_TRACKING_AGE=30  # frames
MIN_TRACKING_QUALITY=0.6
ENABLE_FALSE_POSITIVE_FILTER=True

# Storage
EVIDENCE_STORAGE=minio
EVIDENCE_RETENTION_DAYS=90

# Notifications
ENABLE_REALTIME_NOTIFICATIONS=True
CRITICAL_VIOLATION_ALERT=True
```

---

## 📊 Responsabilidades

### ✅ Sí gestiona:
- ⭐ **Detección de infracciones** (RESPONSABLE PRINCIPAL)
- ⭐ **Clasificación de severidad**
- ⭐ **Validación de infracciones**
- Análisis de velocidad con calibración
- Detección de invasión de carril
- Detección de sentido contrario
- OCR avanzado de placas
- Tracking persistente de vehículos
- Captura y almacenamiento de evidencia
- Filtrado de falsos positivos
- Sistema de notificaciones

### ❌ No gestiona:
- Conexión a cámaras (→ Inference Service)
- Interfaz de usuario (→ Frontend Dashboard)
- Persistencia en base de datos (→ Backend Django)
- Gestión de usuarios (→ Backend Django)

---

## 🎯 Resumen

### **ViolationDetector es el RESPONSABLE PRINCIPAL de:**

1. ✅ Detectar infracciones de tránsito
2. ✅ Clasificar tipo y severidad
3. ✅ Validar y filtrar falsos positivos
4. ✅ Recopilar evidencia
5. ✅ Generar registros completos de infracciones

### **Flujo simplificado:**

```
Cámara → Inference (detección básica) → ML Service (validación) → Django (persistencia) → Frontend (visualización)
```

**El ML Service con su módulo ViolationDetector es el cerebro que decide qué es una infracción y qué no.**

---

**Ver también:**
- [ARQUITECTURA.md](./ARQUITECTURA.md) - Visión general
- [INFERENCE-SERVICE.md](./INFERENCE-SERVICE.md) - Captura de video
- [BACKEND-DJANGO.md](./BACKEND-DJANGO.md) - Persistencia
- [FLUJOS-DETECCION.md](./FLUJOS-DETECCION.md) - Flujos detallados

---

**Última actualización:** Noviembre 2025
