# Modelo de Datos - Sistema de Detección de Infracciones de Tránsito

## 1. Visión General de la Arquitectura de Datos

### 1.1 Bases de Datos

| Base de Datos | Propósito | Tecnología | Ubicación |
|---------------|-----------|------------|-----------|
| **Primary DB** | Datos transaccionales | PostgreSQL 16 + PostGIS + TimescaleDB | RDS/Cloud SQL |
| **Cache** | Sesiones, consultas SUNARP | Redis 7 | ElastiCache/Cloud Memorystore |
| **Object Storage** | Videos, imágenes, modelos ML | MinIO/S3 | S3/GCS/Azure Blob |
| **Message Queue** | Eventos asíncronos | RabbitMQ 3.12 | Self-hosted/CloudAMQP |
| **Analytics** | Métricas de rendimiento | TimescaleDB (hypertables) | Integrado en Primary DB |

### 1.2 Principios de Diseño

1. **Normalización**: Tablas normalizadas hasta 3FN para evitar redundancia
2. **Denormalización Estratégica**: Campos calculados en `infractions` para optimizar queries frecuentes
3. **Auditoría**: Campos `created_at`, `updated_at` en todas las tablas
4. **Soft Deletes**: No se eliminan registros, se marca con `is_active=false` o `deleted_at`
5. **Particionamiento**: Tablas de series temporales particionadas por mes (TimescaleDB)
6. **Índices**: Índices compuestos para queries comunes, índices GIN para JSONB, GIST para geografía

---

## 2. Esquema de Base de Datos Completo

### 2.1 Módulo de Autenticación y Usuarios

#### Tabla: `users`
```sql
CREATE TABLE users (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Información personal
    full_name VARCHAR(255),
    phone VARCHAR(20),
    avatar_url TEXT,
    
    -- Rol y permisos
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'supervisor', 'operator', 'auditor')),
    permissions JSONB DEFAULT '[]',  -- Permisos adicionales granulares
    
    -- Estado y control
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    
    -- Auditoría
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Metadata
    metadata JSONB  -- Configuraciones personales, preferencias de UI
);

-- Índices
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role) WHERE is_active = TRUE;
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- Trigger para updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Función genérica para updated_at (reutilizable)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**Ejemplo de Datos**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "operator01",
  "email": "operator@municipalidad.pe",
  "full_name": "Juan Carlos Pérez",
  "role": "operator",
  "permissions": ["validate_infractions", "generate_reports"],
  "is_active": true,
  "metadata": {
    "language": "es",
    "timezone": "America/Lima",
    "dashboard_layout": "compact"
  }
}
```

---

#### Tabla: `user_sessions`
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,  -- Hash del JWT refresh token
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at) WHERE revoked = FALSE;
```

---

### 2.2 Módulo de Geografía y Zonas

#### Tabla: `zones`
```sql
CREATE TABLE zones (
    -- Identificación
    id VARCHAR(50) PRIMARY KEY,  -- Ejemplo: ZN001, ZN-JPRADO-01
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Configuración de tráfico
    speed_limit INTEGER NOT NULL CHECK (speed_limit > 0 AND speed_limit <= 200),  -- km/h
    lane_count INTEGER DEFAULT 2,
    has_traffic_light BOOLEAN DEFAULT FALSE,
    
    -- Geografía
    geometry GEOGRAPHY(POLYGON, 4326),  -- PostGIS, sistema WGS84
    center_point GEOGRAPHY(POINT, 4326),  -- Centro de la zona
    
    -- Configuración de carriles (para detección de invasión)
    lane_config JSONB,  -- Definición geométrica de carriles
    /*
    Ejemplo de lane_config:
    {
      "lanes": [
        {
          "id": 1,
          "type": "normal",
          "points": [[x1, y1], [x2, y2], ...],  // Polilínea en coordenadas de imagen
          "direction": "north"
        },
        {
          "id": 2,
          "type": "exclusive_bus",
          "points": [[x1, y1], [x2, y2], ...],
          "direction": "north"
        }
      ],
      "stop_line": [[x1, y1], [x2, y2]]  // Línea de alto para semáforos
    }
    */
    
    -- Estado y metadata
    is_active BOOLEAN DEFAULT TRUE,
    municipality VARCHAR(100),  -- San Isidro, Miraflores, etc.
    district VARCHAR(100),
    
    -- Auditoría
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Índices espaciales
CREATE INDEX idx_zones_geometry ON zones USING GIST(geometry);
CREATE INDEX idx_zones_center ON zones USING GIST(center_point);
CREATE INDEX idx_zones_active ON zones(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_zones_municipality ON zones(municipality);

-- Constraint: geometría válida
ALTER TABLE zones ADD CONSTRAINT zones_geometry_valid 
    CHECK (ST_IsValid(geometry::geometry));
```

**Ejemplo de Datos**:
```sql
INSERT INTO zones (id, name, speed_limit, geometry, center_point, municipality) VALUES
('ZN001', 
 'Av. Javier Prado Este - San Isidro', 
 60,
 ST_GeogFromText('POLYGON((-77.0320 -12.0868, -77.0315 -12.0868, -77.0315 -12.0872, -77.0320 -12.0872, -77.0320 -12.0868))'),
 ST_GeogFromText('POINT(-77.03175 -12.0870)'),
 'San Isidro'
);
```

---

### 2.3 Módulo de Dispositivos IoT

#### Tabla: `devices`
```sql
CREATE TABLE devices (
    -- Identificación
    id VARCHAR(50) PRIMARY KEY,  -- Ejemplo: CAM001, CAM-JP-001
    zone_id VARCHAR(50) REFERENCES zones(id) ON DELETE SET NULL,
    
    -- Información del dispositivo
    name VARCHAR(255) NOT NULL,
    model VARCHAR(100) DEFAULT 'EZVIZ H6C Pro 2K',
    serial_number VARCHAR(100) UNIQUE,
    firmware_version VARCHAR(50),
    
    -- Conectividad
    rtsp_url TEXT NOT NULL,  -- rtsp://user:pass@ip:port/path
    rtsp_substream_url TEXT,  -- Stream de baja resolución
    onvif_url TEXT,  -- http://ip:port/onvif/device_service
    ip_address INET,
    mac_address MACADDR,
    
    -- Ubicación y orientación
    location GEOGRAPHY(POINT, 4326),  -- Coordenadas GPS de la cámara
    altitude FLOAT,  -- Metros sobre nivel del mar
    orientation FLOAT,  -- Ángulo de orientación 0-360° (norte = 0°)
    tilt FLOAT,  -- Ángulo de inclinación -90° a 90°
    field_of_view FLOAT,  -- Campo de visión en grados
    
    -- Calibración
    calibration_matrix JSONB,  -- Matriz de homografía 3x3
    /*
    Ejemplo:
    {
      "H": [
        [1.2, 0.1, -50],
        [0.05, 1.5, -100],
        [0.0001, 0.0002, 1]
      ],
      "reference_points": [
        {"image": [120, 680], "world": [0, 0]},
        {"image": [450, 650], "world": [10, 0]}
      ],
      "calibration_date": "2025-11-01T10:30:00Z",
      "calibrated_by": "550e8400-e29b-41d4-a716-446655440000",
      "error_meters": 0.35
    }
    */
    
    -- Configuración de detección
    detection_config JSONB DEFAULT '{}',
    /*
    {
      "fps": 30,
      "resolution": "2K",
      "detection_threshold": 0.5,
      "enable_night_mode": true,
      "roi": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]  // Región de interés
    }
    */
    
    -- Estado operativo
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance', 'error', 'offline')),
    last_heartbeat TIMESTAMP,
    uptime_seconds INTEGER DEFAULT 0,
    
    -- Métricas de rendimiento
    current_fps FLOAT,
    avg_latency_ms FLOAT,
    total_detections BIGINT DEFAULT 0,
    total_infractions BIGINT DEFAULT 0,
    
    -- Mantenimiento
    last_maintenance DATE,
    next_maintenance DATE,
    maintenance_notes TEXT,
    
    -- Auditoría
    installed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Metadata adicional
    metadata JSONB
);

-- Índices
CREATE INDEX idx_devices_zone ON devices(zone_id);
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_devices_location ON devices USING GIST(location);
CREATE INDEX idx_devices_last_heartbeat ON devices(last_heartbeat DESC);
CREATE INDEX idx_devices_ip ON devices(ip_address);

-- Constraint: URL RTSP válida
ALTER TABLE devices ADD CONSTRAINT devices_rtsp_url_format 
    CHECK (rtsp_url LIKE 'rtsp://%');
```

**Ejemplo de Datos**:
```sql
INSERT INTO devices (id, zone_id, name, rtsp_url, location, orientation, calibration_matrix) VALUES
('CAM001',
 'ZN001',
 'Cámara Javier Prado Este - Entrada',
 'rtsp://admin:Abc123456@192.168.1.100:554/h264/ch1/main/av_stream',
 ST_GeogFromText('POINT(-77.03175 -12.0870)'),
 45.0,
 '{"H": [[1.2, 0.1, -50], [0.05, 1.5, -100], [0.0001, 0.0002, 1]], "error_meters": 0.35}'::jsonb
);
```

---

#### Tabla: `device_health_logs`
```sql
CREATE TABLE device_health_logs (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Métricas de salud
    status VARCHAR(50) NOT NULL,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    temperature FLOAT,  -- °C
    
    -- Conectividad
    network_latency_ms FLOAT,
    packet_loss FLOAT,
    bandwidth_mbps FLOAT,
    
    -- Stream
    fps FLOAT,
    bitrate_kbps FLOAT,
    dropped_frames INTEGER,
    
    -- Errores
    error_count INTEGER DEFAULT 0,
    error_messages TEXT[],
    
    -- Metadata
    metadata JSONB
);

-- TimescaleDB hypertable
SELECT create_hypertable('device_health_logs', 'timestamp');

-- Política de retención: 90 días
SELECT add_retention_policy('device_health_logs', INTERVAL '90 days');

-- Índices
CREATE INDEX idx_device_health_device_time ON device_health_logs(device_id, timestamp DESC);
CREATE INDEX idx_device_health_status ON device_health_logs(status, timestamp DESC);
```

---

### 2.4 Módulo de Vehículos y Conductores

#### Tabla: `vehicles`
```sql
CREATE TABLE vehicles (
    -- Identificación
    plate VARCHAR(20) PRIMARY KEY,  -- ABC-1234, ABC-123
    
    -- Información del vehículo
    brand VARCHAR(100),
    model VARCHAR(100),
    year INTEGER CHECK (year > 1900 AND year <= EXTRACT(YEAR FROM CURRENT_DATE) + 1),
    color VARCHAR(50),
    vehicle_type VARCHAR(50),  -- sedan, suv, truck, bus, motorcycle, etc.
    
    -- Propietario
    owner_name VARCHAR(255),
    owner_dni VARCHAR(20),
    owner_address TEXT,
    owner_phone VARCHAR(20),
    
    -- Registro
    registration_date DATE,
    registration_status VARCHAR(50),  -- active, suspended, cancelled
    
    -- Datos SUNARP
    sunarp_last_check TIMESTAMP,
    sunarp_data JSONB,
    /*
    Ejemplo:
    {
      "placa": "ABC-1234",
      "marca": "Toyota",
      "modelo": "Corolla",
      "anio": 2020,
      "color": "Gris",
      "propietario": {
        "nombre": "JUAN CARLOS PEREZ LOPEZ",
        "dni": "12345678",
        "direccion": "Av. Los Alamos 123, San Isidro"
      },
      "estado": "VIGENTE",
      "fecha_inscripcion": "2020-03-15",
      "sede": "LIMA",
      "ultimo_check": "2025-11-01T15:30:00Z"
    }
    */
    sunarp_cache_expires TIMESTAMP,
    
    -- Estadísticas
    total_infractions INTEGER DEFAULT 0,
    last_infraction_date TIMESTAMP,
    
    -- Auditoría
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadata
    metadata JSONB
);

-- Índices
CREATE INDEX idx_vehicles_owner_dni ON vehicles(owner_dni);
CREATE INDEX idx_vehicles_brand_model ON vehicles(brand, model);
CREATE INDEX idx_vehicles_type ON vehicles(vehicle_type);
CREATE INDEX idx_vehicles_total_infractions ON vehicles(total_infractions DESC);
CREATE INDEX idx_vehicles_sunarp_cache ON vehicles(sunarp_cache_expires) 
    WHERE sunarp_cache_expires > CURRENT_TIMESTAMP;

-- Índice GIN para búsqueda en JSONB
CREATE INDEX idx_vehicles_sunarp_data ON vehicles USING GIN(sunarp_data);
```

---

#### Tabla: `drivers`
```sql
CREATE TABLE drivers (
    -- Identificación
    dni VARCHAR(20) PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    
    -- Licencia de conducir
    license_number VARCHAR(50),
    license_category VARCHAR(20),  -- A-I, A-IIa, A-IIb, A-IIIa, etc.
    license_expiry DATE,
    license_issued_date DATE,
    license_issuing_authority VARCHAR(100),
    
    -- Información personal
    birth_date DATE,
    age INTEGER GENERATED ALWAYS AS (EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM birth_date)) STORED,
    gender VARCHAR(20),
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    
    -- Historial de conducción
    driving_experience_years INTEGER,  -- Años desde primera licencia
    total_infractions INTEGER DEFAULT 0,
    serious_infractions INTEGER DEFAULT 0,  -- Infracciones graves
    last_infraction_date TIMESTAMP,
    
    -- Score de riesgo (calculado por ML)
    risk_score FLOAT DEFAULT 0.0 CHECK (risk_score >= 0 AND risk_score <= 1),
    risk_category VARCHAR(20) DEFAULT 'low' CHECK (risk_category IN ('low', 'medium', 'high', 'critical')),
    risk_updated_at TIMESTAMP,
    
    -- Estado
    is_active BOOLEAN DEFAULT TRUE,
    is_blacklisted BOOLEAN DEFAULT FALSE,
    blacklist_reason TEXT,
    
    -- Auditoría
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadata
    metadata JSONB
);

-- Índices
CREATE INDEX idx_drivers_full_name ON drivers(full_name);
CREATE INDEX idx_drivers_license ON drivers(license_number);
CREATE INDEX idx_drivers_risk_score ON drivers(risk_score DESC);
CREATE INDEX idx_drivers_risk_category ON drivers(risk_category);
CREATE INDEX idx_drivers_total_infractions ON drivers(total_infractions DESC);
CREATE INDEX idx_drivers_age ON drivers(age);

-- Constraint: edad mínima para conducir
ALTER TABLE drivers ADD CONSTRAINT drivers_min_age 
    CHECK (age >= 18);
```

---

### 2.5 Módulo de Infracciones (Core)

#### Tabla: `infractions`
```sql
CREATE TABLE infractions (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    infraction_code VARCHAR(50) UNIQUE NOT NULL,  -- INF-20251101-001
    
    -- Tipo de infracción
    type VARCHAR(50) NOT NULL CHECK (type IN ('SPEED_VIOLATION', 'LANE_INVASION', 'RED_LIGHT', 'NO_SEATBELT', 'PHONE_USAGE', 'OTHER')),
    
    -- Referencias
    device_id VARCHAR(50) REFERENCES devices(id) ON DELETE SET NULL,
    zone_id VARCHAR(50) REFERENCES zones(id) ON DELETE SET NULL,
    plate VARCHAR(20) REFERENCES vehicles(plate) ON DELETE SET NULL,
    driver_dni VARCHAR(20) REFERENCES drivers(dni) ON DELETE SET NULL,
    
    -- Detalles de la infracción (específicos por tipo)
    detected_speed FLOAT,  -- km/h (para SPEED_VIOLATION)
    speed_limit FLOAT,  -- km/h
    speed_excess FLOAT GENERATED ALWAYS AS (detected_speed - speed_limit) STORED,
    
    violation_details JSONB,
    /*
    Para SPEED_VIOLATION:
    {
      "trajectory": [...],  // Últimos N puntos de la trayectoria
      "acceleration": 2.5,  // m/s²
      "distance_traveled": 45.3  // metros
    }
    
    Para LANE_INVASION:
    {
      "invaded_lane_id": 2,
      "invasion_duration_seconds": 3.5,
      "invasion_points": [[x1, y1], [x2, y2], ...]
    }
    
    Para RED_LIGHT:
    {
      "traffic_light_state": "red",
      "time_after_red_seconds": 1.2,
      "stop_line_crossed": true
    }
    */
    
    -- Evidencia multimedia
    video_url TEXT NOT NULL,  -- s3://bucket/2025/11/01/CAM001_143522.mp4
    video_duration_seconds INTEGER DEFAULT 15,
    snapshot_url TEXT NOT NULL,  -- s3://bucket/2025/11/01/CAM001_143522.jpg
    plate_crop_url TEXT,  -- Crop de la placa
    additional_images TEXT[],  -- Array de URLs de imágenes adicionales
    
    -- Metadatos de detección
    confidence_score FLOAT NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    ocr_confidence FLOAT CHECK (ocr_confidence >= 0 AND ocr_confidence <= 1),
    track_id INTEGER,  -- ID del tracking en el momento de detección
    
    -- Contexto temporal y ambiental
    detected_at TIMESTAMP NOT NULL,
    hour_of_day INTEGER GENERATED ALWAYS AS (EXTRACT(HOUR FROM detected_at)) STORED,
    day_of_week INTEGER GENERATED ALWAYS AS (EXTRACT(DOW FROM detected_at)) STORED,
    is_weekend BOOLEAN GENERATED ALWAYS AS (EXTRACT(DOW FROM detected_at) IN (0, 6)) STORED,
    
    weather_conditions VARCHAR(50),  -- clear, cloudy, rain, fog
    visibility VARCHAR(50),  -- excellent, good, moderate, poor
    lighting_conditions VARCHAR(50),  -- daylight, dawn, dusk, night
    
    -- Estado y flujo de trabajo
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'validated', 'rejected', 'appealed', 'paid', 'cancelled')),
    validated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    validated_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- Multa
    fine_amount DECIMAL(10, 2),
    fine_code VARCHAR(50),
    fine_issued BOOLEAN DEFAULT FALSE,
    fine_paid BOOLEAN DEFAULT FALSE,
    fine_paid_at TIMESTAMP,
    
    -- Predicciones ML
    recidivism_risk FLOAT CHECK (recidivism_risk >= 0 AND recidivism_risk <= 1),
    accident_risk FLOAT CHECK (accident_risk >= 0 AND accident_risk <= 1),
    risk_factors JSONB,
    /*
    {
      "infraction_count": {"value": 5, "importance": 0.35},
      "recency": {"value": 7, "importance": 0.28},
      "severity": {"value": "high", "importance": 0.22}
    }
    */
    
    -- Auditoría
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadata adicional
    metadata JSONB
);

-- Índices principales
CREATE INDEX idx_infractions_type ON infractions(type);
CREATE INDEX idx_infractions_status ON infractions(status);
CREATE INDEX idx_infractions_device ON infractions(device_id, detected_at DESC);
CREATE INDEX idx_infractions_zone ON infractions(zone_id, detected_at DESC);
CREATE INDEX idx_infractions_plate ON infractions(plate);
CREATE INDEX idx_infractions_driver ON infractions(driver_dni);
CREATE INDEX idx_infractions_detected_at ON infractions(detected_at DESC);

-- Índices compuestos para queries comunes
CREATE INDEX idx_infractions_pending ON infractions(status, detected_at DESC) 
    WHERE status = 'pending';
CREATE INDEX idx_infractions_zone_date ON infractions(zone_id, detected_at) 
    WHERE status != 'cancelled';
CREATE INDEX idx_infractions_type_date ON infractions(type, detected_at DESC);

-- Índice para búsqueda de texto completo
CREATE INDEX idx_infractions_code ON infractions(infraction_code);

-- Índice GIN para JSONB
CREATE INDEX idx_infractions_details ON infractions USING GIN(violation_details);
CREATE INDEX idx_infractions_risk_factors ON infractions USING GIN(risk_factors);

-- Trigger para generar infraction_code
CREATE OR REPLACE FUNCTION generate_infraction_code()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.infraction_code IS NULL THEN
        NEW.infraction_code := 'INF-' || TO_CHAR(NEW.detected_at, 'YYYYMMDD') || '-' || 
                              LPAD(nextval('infraction_code_seq')::TEXT, 5, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE SEQUENCE infraction_code_seq START 1;

CREATE TRIGGER set_infraction_code
    BEFORE INSERT ON infractions
    FOR EACH ROW
    EXECUTE FUNCTION generate_infraction_code();

-- Trigger para actualizar estadísticas de vehículos
CREATE OR REPLACE FUNCTION update_vehicle_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.plate IS NOT NULL AND NEW.status = 'validated' THEN
        UPDATE vehicles 
        SET total_infractions = total_infractions + 1,
            last_infraction_date = NEW.detected_at
        WHERE plate = NEW.plate;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_vehicle_infraction_count
    AFTER INSERT OR UPDATE OF status ON infractions
    FOR EACH ROW
    WHEN (NEW.status = 'validated')
    EXECUTE FUNCTION update_vehicle_stats();
```

**Ejemplo de Datos**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "infraction_code": "INF-20251101-001",
  "type": "SPEED_VIOLATION",
  "device_id": "CAM001",
  "zone_id": "ZN001",
  "plate": "ABC-1234",
  "detected_speed": 78.5,
  "speed_limit": 60.0,
  "speed_excess": 18.5,
  "violation_details": {
    "trajectory": [...],
    "acceleration": 2.3
  },
  "video_url": "s3://traffic-videos/2025/11/01/CAM001_143522.mp4",
  "snapshot_url": "s3://traffic-snapshots/2025/11/01/CAM001_143522.jpg",
  "confidence_score": 0.92,
  "ocr_confidence": 0.89,
  "detected_at": "2025-11-01T14:35:22Z",
  "weather_conditions": "clear",
  "lighting_conditions": "daylight",
  "status": "pending",
  "recidivism_risk": 0.68,
  "fine_amount": 396.00
}
```

---

### 2.6 Módulo de Machine Learning

#### Tabla: `ml_models`
```sql
CREATE TABLE ml_models (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(100) NOT NULL,  -- recidivism_xgboost, accident_lstm
    version VARCHAR(50) NOT NULL,  -- v1.2.3, 2025-11-01
    model_type VARCHAR(50) NOT NULL CHECK (model_type IN ('classification', 'regression', 'clustering', 'detection')),
    
    -- Framework
    framework VARCHAR(50) NOT NULL,  -- xgboost, tensorflow, pytorch, sklearn
    framework_version VARCHAR(50),
    
    -- Artefactos
    model_path TEXT NOT NULL,  -- s3://models/recidivism_v1.2.3.pkl
    model_size_mb FLOAT,
    
    -- MLflow integration
    mlflow_run_id VARCHAR(100),
    mlflow_experiment_id VARCHAR(100),
    mlflow_model_uri TEXT,
    
    -- Métricas de rendimiento
    metrics JSONB NOT NULL,
    /*
    {
      "accuracy": 0.92,
      "precision": 0.89,
      "recall": 0.87,
      "f1_score": 0.88,
      "auc_roc": 0.94,
      "confusion_matrix": [[45, 5], [3, 47]]
    }
    */
    
    -- Hiperparámetros
    hyperparameters JSONB,
    /*
    {
      "max_depth": 6,
      "learning_rate": 0.1,
      "n_estimators": 200,
      "subsample": 0.8
    }
    */
    
    -- Dataset
    training_dataset_path TEXT,
    training_dataset_size INTEGER,
    validation_dataset_path TEXT,
    test_dataset_path TEXT,
    
    -- Features
    feature_names TEXT[],
    feature_importance JSONB,
    
    -- Deployment
    is_active BOOLEAN DEFAULT FALSE,
    deployed_at TIMESTAMP,
    deployed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    deployment_environment VARCHAR(50),  -- staging, production
    
    -- Monitoring
    prediction_count BIGINT DEFAULT 0,
    avg_prediction_time_ms FLOAT,
    last_prediction_at TIMESTAMP,
    
    -- Drift detection
    data_drift_detected BOOLEAN DEFAULT FALSE,
    concept_drift_detected BOOLEAN DEFAULT FALSE,
    drift_check_at TIMESTAMP,
    
    -- Auditoría
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trained_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Notas y documentación
    description TEXT,
    training_notes TEXT,
    
    -- Metadata
    metadata JSONB,
    
    UNIQUE(model_name, version)
);

-- Índices
CREATE INDEX idx_ml_models_name ON ml_models(model_name);
CREATE INDEX idx_ml_models_active ON ml_models(model_name, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_ml_models_created ON ml_models(created_at DESC);
CREATE INDEX idx_ml_models_framework ON ml_models(framework);

-- Constraint: solo un modelo activo por nombre
CREATE UNIQUE INDEX idx_ml_models_one_active 
    ON ml_models(model_name) 
    WHERE is_active = TRUE;
```

---

#### Tabla: `ml_predictions`
```sql
CREATE TABLE ml_predictions (
    id BIGSERIAL PRIMARY KEY,
    model_id UUID NOT NULL REFERENCES ml_models(id) ON DELETE CASCADE,
    infraction_id UUID REFERENCES infractions(id) ON DELETE CASCADE,
    driver_dni VARCHAR(20) REFERENCES drivers(dni) ON DELETE SET NULL,
    
    -- Predicción
    prediction_type VARCHAR(50) NOT NULL,  -- recidivism, accident_risk
    prediction_value FLOAT NOT NULL,
    prediction_class VARCHAR(50),  -- low, medium, high para clasificación
    prediction_confidence FLOAT,
    
    -- Features utilizados
    features JSONB NOT NULL,
    
    -- Resultado real (para evaluación posterior)
    actual_value FLOAT,
    actual_class VARCHAR(50),
    
    -- Timing
    prediction_time_ms FLOAT,
    predicted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadata
    metadata JSONB
);

-- TimescaleDB hypertable
SELECT create_hypertable('ml_predictions', 'predicted_at');

-- Índices
CREATE INDEX idx_ml_predictions_model ON ml_predictions(model_id, predicted_at DESC);
CREATE INDEX idx_ml_predictions_infraction ON ml_predictions(infraction_id);
CREATE INDEX idx_ml_predictions_driver ON ml_predictions(driver_dni, predicted_at DESC);
CREATE INDEX idx_ml_predictions_type ON ml_predictions(prediction_type);
```

---

### 2.7 Módulo de Eventos y Logs (Time-Series)

#### Tabla: `events`
```sql
CREATE TABLE events (
    id BIGSERIAL,
    
    -- Tipo de evento
    event_type VARCHAR(50) NOT NULL,  -- detection, tracking, ocr, infraction, system, error
    event_category VARCHAR(50),  -- vehicle_detected, plate_recognized, inference_complete
    
    -- Referencias
    device_id VARCHAR(50) REFERENCES devices(id) ON DELETE CASCADE,
    infraction_id UUID REFERENCES infractions(id) ON DELETE CASCADE,
    
    -- Timing
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Datos del evento
    data JSONB NOT NULL,
    /*
    Ejemplo para detection:
    {
      "frame_id": 12345,
      "detections": [
        {"class": "car", "bbox": [120, 340, 450, 680], "confidence": 0.92}
      ]
    }
    
    Ejemplo para ocr:
    {
      "plate_text": "ABC-1234",
      "confidence": 0.89,
      "bbox": [200, 400, 300, 450]
    }
    */
    
    -- Severidad (para errores)
    severity VARCHAR(20) CHECK (severity IN ('debug', 'info', 'warning', 'error', 'critical')),
    
    PRIMARY KEY (id, timestamp)
);

-- TimescaleDB hypertable
SELECT create_hypertable('events', 'timestamp');

-- Política de retención: 90 días
SELECT add_retention_policy('events', INTERVAL '90 days');

-- Continuous aggregates para métricas
CREATE MATERIALIZED VIEW events_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', timestamp) AS hour,
    device_id,
    event_type,
    COUNT(*) as event_count,
    AVG((data->>'confidence')::FLOAT) as avg_confidence
FROM events
WHERE event_type = 'detection'
GROUP BY hour, device_id, event_type;

-- Política de refresco: cada 10 minutos
SELECT add_continuous_aggregate_policy('events_hourly',
    start_offset => INTERVAL '2 hours',
    end_offset => INTERVAL '10 minutes',
    schedule_interval => INTERVAL '10 minutes');

-- Índices
CREATE INDEX idx_events_device_time ON events(device_id, timestamp DESC);
CREATE INDEX idx_events_type ON events(event_type, timestamp DESC);
CREATE INDEX idx_events_severity ON events(severity) WHERE severity IN ('error', 'critical');
CREATE INDEX idx_events_data ON events USING GIN(data);
```

---

#### Tabla: `inference_metrics`
```sql
CREATE TABLE inference_metrics (
    id BIGSERIAL,
    device_id VARCHAR(50) NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Métricas de rendimiento
    fps FLOAT NOT NULL,
    latency_ms FLOAT NOT NULL,
    throughput_frames_per_sec FLOAT,
    
    -- Recursos
    gpu_id INTEGER DEFAULT 0,
    gpu_utilization FLOAT,  -- Porcentaje 0-100
    gpu_memory_used_mb FLOAT,
    gpu_memory_total_mb FLOAT,
    gpu_temperature FLOAT,
    cpu_utilization FLOAT,
    memory_mb FLOAT,
    
    -- Detecciones
    detections_count INTEGER DEFAULT 0,
    tracked_objects_count INTEGER DEFAULT 0,
    infractions_count INTEGER DEFAULT 0,
    
    -- Latencias por stage
    decode_latency_ms FLOAT,
    detection_latency_ms FLOAT,
    tracking_latency_ms FLOAT,
    ocr_latency_ms FLOAT,
    
    -- Calidad
    avg_detection_confidence FLOAT,
    avg_ocr_confidence FLOAT,
    
    PRIMARY KEY (id, timestamp)
);

-- TimescaleDB hypertable
SELECT create_hypertable('inference_metrics', 'timestamp');

-- Retención: 30 días para métricas brutas
SELECT add_retention_policy('inference_metrics', INTERVAL '30 days');

-- Continuous aggregate: métricas por 5 minutos
CREATE MATERIALIZED VIEW inference_metrics_5min
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('5 minutes', timestamp) AS bucket,
    device_id,
    AVG(fps) as avg_fps,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_latency,
    AVG(gpu_utilization) as avg_gpu_util,
    SUM(detections_count) as total_detections,
    SUM(infractions_count) as total_infractions
FROM inference_metrics
GROUP BY bucket, device_id;

-- Índices
CREATE INDEX idx_inference_metrics_device ON inference_metrics(device_id, timestamp DESC);
CREATE INDEX idx_inference_metrics_gpu ON inference_metrics(gpu_id, timestamp DESC);
```

---

### 2.8 Módulo de Notificaciones y Auditoría

#### Tabla: `notifications`
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Destinatario
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Contenido
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,  -- infraction, system, alert, report_ready
    
    -- Referencias
    infraction_id UUID REFERENCES infractions(id) ON DELETE CASCADE,
    device_id VARCHAR(50) REFERENCES devices(id) ON DELETE SET NULL,
    
    -- Estado
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    
    -- Prioridad
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    
    -- Canales
    channel VARCHAR(50) DEFAULT 'in_app',  -- in_app, email, sms, push
    email_sent BOOLEAN DEFAULT FALSE,
    email_sent_at TIMESTAMP,
    
    -- Timing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- Metadata
    metadata JSONB
);

-- Índices
CREATE INDEX idx_notifications_user ON notifications(user_id, created_at DESC);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;
CREATE INDEX idx_notifications_type ON notifications(notification_type);
CREATE INDEX idx_notifications_priority ON notifications(priority) WHERE priority IN ('high', 'urgent');
```

---

#### Tabla: `audit_logs`
```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    
    -- Actor
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    username VARCHAR(150),
    
    -- Acción
    action VARCHAR(100) NOT NULL,  -- create, update, delete, validate, login, export
    resource_type VARCHAR(50) NOT NULL,  -- infraction, device, user, vehicle
    resource_id VARCHAR(255),
    
    -- Cambios
    old_values JSONB,
    new_values JSONB,
    
    -- Contexto
    ip_address INET,
    user_agent TEXT,
    endpoint VARCHAR(255),
    http_method VARCHAR(10),
    
    -- Resultado
    success BOOLEAN NOT NULL,
    error_message TEXT,
    
    -- Timing
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadata
    metadata JSONB
);

-- TimescaleDB hypertable
SELECT create_hypertable('audit_logs', 'timestamp');

-- Retención: 2 años para auditoría
SELECT add_retention_policy('audit_logs', INTERVAL '2 years');

-- Índices
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, timestamp DESC);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id, timestamp DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action, timestamp DESC);
CREATE INDEX idx_audit_logs_failed ON audit_logs(success, timestamp DESC) WHERE success = FALSE;
```

---

## 3. Relaciones y Cardinalidad

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  zones   │ 1     N │ devices  │ 1     N │ events   │
│          ├─────────┤          ├─────────┤          │
└────┬─────┘         └────┬─────┘         └──────────┘
     │                    │
     │ 1                  │ 1
     │                    │
     │ N                  │ N
     │                    │
┌────┴──────────┐    ┌───┴──────────────────┐
│ infractions   │────┤ inference_metrics    │
└────┬──────────┘    └──────────────────────┘
     │
     ├─── N:1 ───► vehicles (plate)
     │
     ├─── N:1 ───► drivers (dni)
     │
     ├─── N:1 ───► users (validated_by)
     │
     └─── 1:N ───► ml_predictions
```

---

## 4. Queries Comunes y Optimizadas

### 4.1 Infracciones Pendientes de Validación
```sql
SELECT 
    i.infraction_code,
    i.type,
    i.detected_at,
    i.plate,
    v.brand,
    v.model,
    i.detected_speed,
    i.speed_limit,
    i.confidence_score,
    i.snapshot_url,
    d.name as camera_name,
    z.name as zone_name
FROM infractions i
LEFT JOIN vehicles v ON i.plate = v.plate
LEFT JOIN devices d ON i.device_id = d.id
LEFT JOIN zones z ON i.zone_id = z.id
WHERE i.status = 'pending'
    AND i.confidence_score >= 0.8
ORDER BY i.detected_at DESC
LIMIT 50;
```

### 4.2 Top Infractores del Mes
```sql
SELECT 
    v.plate,
    v.brand,
    v.model,
    v.owner_name,
    dr.full_name as driver_name,
    dr.risk_score,
    COUNT(*) as infraction_count,
    SUM(CASE WHEN i.type = 'SPEED_VIOLATION' THEN 1 ELSE 0 END) as speed_violations,
    SUM(CASE WHEN i.type = 'RED_LIGHT' THEN 1 ELSE 0 END) as red_light_violations,
    MAX(i.detected_speed - i.speed_limit) as max_speed_excess
FROM infractions i
JOIN vehicles v ON i.plate = v.plate
LEFT JOIN drivers dr ON i.driver_dni = dr.dni
WHERE i.detected_at >= DATE_TRUNC('month', CURRENT_DATE)
    AND i.status = 'validated'
GROUP BY v.plate, v.brand, v.model, v.owner_name, dr.full_name, dr.risk_score
ORDER BY infraction_count DESC
LIMIT 20;
```

### 4.3 Estadísticas por Zona y Horario
```sql
SELECT 
    z.name as zone,
    EXTRACT(HOUR FROM i.detected_at) as hour,
    COUNT(*) as total_infractions,
    COUNT(DISTINCT i.plate) as unique_vehicles,
    AVG(i.detected_speed) as avg_speed,
    MAX(i.detected_speed) as max_speed,
    AVG(i.confidence_score) as avg_confidence
FROM infractions i
JOIN zones z ON i.zone_id = z.id
WHERE i.detected_at >= CURRENT_DATE - INTERVAL '7 days'
    AND i.type = 'SPEED_VIOLATION'
    AND i.status = 'validated'
GROUP BY z.name, EXTRACT(HOUR FROM i.detected_at)
ORDER BY zone, hour;
```

### 4.4 Rendimiento de Cámaras
```sql
SELECT 
    d.id,
    d.name,
    d.status,
    d.last_heartbeat,
    d.current_fps,
    d.avg_latency_ms,
    d.total_detections,
    d.total_infractions,
    ROUND((d.total_infractions::NUMERIC / NULLIF(d.total_detections, 0)) * 100, 2) as infraction_rate,
    AVG(im.gpu_utilization) as avg_gpu_util,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY im.latency_ms) as p95_latency
FROM devices d
LEFT JOIN LATERAL (
    SELECT * FROM inference_metrics 
    WHERE device_id = d.id 
        AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
) im ON true
WHERE d.status = 'active'
GROUP BY d.id, d.name, d.status, d.last_heartbeat, d.current_fps, 
         d.avg_latency_ms, d.total_detections, d.total_infractions
ORDER BY d.name;
```

### 4.5 Análisis de Reincidencia
```sql
WITH driver_infractions AS (
    SELECT 
        driver_dni,
        COUNT(*) as total_infractions,
        COUNT(DISTINCT DATE(detected_at)) as days_with_infractions,
        MIN(detected_at) as first_infraction,
        MAX(detected_at) as last_infraction,
        AVG(recidivism_risk) as avg_predicted_risk
    FROM infractions
    WHERE driver_dni IS NOT NULL
        AND status = 'validated'
    GROUP BY driver_dni
)
SELECT 
    dr.full_name,
    dr.license_number,
    dr.risk_score,
    di.total_infractions,
    di.days_with_infractions,
    di.first_infraction,
    di.last_infraction,
    EXTRACT(DAY FROM di.last_infraction - di.first_infraction) as days_span,
    ROUND(di.total_infractions::NUMERIC / NULLIF(EXTRACT(DAY FROM di.last_infraction - di.first_infraction), 0), 2) as infractions_per_day,
    di.avg_predicted_risk
FROM driver_infractions di
JOIN drivers dr ON di.driver_dni = dr.dni
WHERE di.total_infractions >= 3
ORDER BY di.total_infractions DESC, dr.risk_score DESC
LIMIT 50;
```

---

## 5. Políticas de Retención y Archivado

### 5.1 Retención de Datos

| Tabla | Retención en DB Principal | Archivado |
|-------|---------------------------|-----------|
| `infractions` | 2 años | S3 Glacier después de 2 años |
| `events` | 90 días | Eliminar después de 90 días |
| `inference_metrics` | 30 días (raw), 1 año (agregado) | Eliminar después de 1 año |
| `audit_logs` | 2 años | S3 Glacier después de 2 años |
| `device_health_logs` | 90 días | Eliminar después de 90 días |
| `ml_predictions` | 1 año | S3 después de 1 año |
| Videos (MinIO/S3) | 30 días (hot), 2 años (cold) | Glacier después de 2 años |
| Snapshots (MinIO/S3) | 90 días (hot), 2 años (cold) | Glacier después de 2 años |

### 5.2 Scripts de Archivado

```sql
-- Función para archivar infracciones antiguas
CREATE OR REPLACE FUNCTION archive_old_infractions()
RETURNS void AS $$
BEGIN
    -- Exportar a CSV para archivado en S3
    COPY (
        SELECT * FROM infractions 
        WHERE detected_at < CURRENT_DATE - INTERVAL '2 years'
    ) TO '/tmp/infractions_archive_' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '.csv' 
    WITH CSV HEADER;
    
    -- Marcar como archivado (no eliminar directamente)
    UPDATE infractions 
    SET metadata = jsonb_set(COALESCE(metadata, '{}'::jsonb), '{archived}', 'true'::jsonb)
    WHERE detected_at < CURRENT_DATE - INTERVAL '2 years';
END;
$$ LANGUAGE plpgsql;

-- Job programado (pg_cron)
SELECT cron.schedule('archive-infractions', '0 2 * * 0', 'SELECT archive_old_infractions()');
```

---

## 6. Backup y Disaster Recovery

### 6.1 Estrategia de Backup

```bash
# Backup diario de PostgreSQL
#!/bin/bash
BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="traffic_system"

# Full backup
pg_dump -h localhost -U admin -F c -b -v -f \
    "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.backup" $DB_NAME

# Retener últimos 7 días localmente
find $BACKUP_DIR -name "*.backup" -mtime +7 -delete

# Subir a S3 para redundancia
aws s3 cp "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.backup" \
    s3://traffic-system-backups/postgres/

# Verificar integridad
pg_restore --list "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.backup" > /dev/null
if [ $? -eq 0 ]; then
    echo "Backup successful and verified"
else
    echo "Backup verification failed!" | mail -s "ALERT: Backup Failed" admin@example.com
fi
```

### 6.2 Plan de Recuperación

**RTO (Recovery Time Objective)**: 4 horas  
**RPO (Recovery Point Objective)**: 24 horas

**Procedimiento de Restauración**:
1. Provisionar nueva instancia de PostgreSQL
2. Restaurar último backup disponible:
   ```bash
   pg_restore -h new-host -U admin -d traffic_system \
       -v /backups/traffic_system_20251101_020000.backup
   ```
3. Verificar integridad de datos
4. Actualizar configuración de servicios (connection strings)
5. Reiniciar servicios Django y FastAPI
6. Validar funcionalidad con test suite

---

**Versión**: 1.0  
**Fecha**: 2025-11-01  
**Mantenido por**: Equipo de Datos  
**Próxima Revisión**: Mensual
