# Backend Django - Sistema de Administración

## 📋 Índice
- [Visión General](#visión-general)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Modelos de Datos](#modelos-de-datos)
- [APIs REST](#apis-rest)
- [Funcionalidades](#funcionalidades)
- [Relaciones con Otros Componentes](#relaciones-con-otros-componentes)
- [Configuración](#configuración)

---

## 🎯 Visión General

El **Backend Django** es el sistema de administración principal del proyecto. Proporciona:
- Panel administrativo para operadores
- API REST para el frontend
- Gestión de usuarios y autenticación
- CRUD de todas las entidades del sistema
- Generación de reportes
- Sistema de notificaciones

**Tecnologías:**
- Django 5.0
- Django REST Framework 3.14
- PostgreSQL 16
- Redis 7
- JWT para autenticación

**Puerto:** 8000  
**URL Base:** `http://localhost:8000`

---

## 📁 Estructura del Proyecto

```
backend-django/
├── config/                      # Configuración principal
│   ├── settings.py             # Settings de Django
│   ├── urls.py                 # URLs principales
│   ├── wsgi.py                 # WSGI application
│   ├── asgi.py                 # ASGI application
│   └── celery.py               # Configuración Celery
│
├── authentication/              # App de autenticación
│   ├── models.py               # Modelo User personalizado
│   ├── serializers.py          # Serializers JWT
│   ├── views.py                # Login, Register, Logout
│   └── permissions.py          # Permisos personalizados
│
├── devices/                     # App de dispositivos
│   ├── models.py               # Zone, Device
│   ├── serializers.py          # Serializers de dispositivos
│   ├── views.py                # CRUD ViewSets
│   └── admin.py                # Admin de dispositivos
│
├── vehicles/                    # App de vehículos
│   ├── models.py               # Vehicle, Driver
│   ├── serializers.py          # Serializers de vehículos
│   ├── views.py                # CRUD + consulta SUNARP
│   └── admin.py                # Admin de vehículos
│
├── infractions/                 # App de infracciones
│   ├── models.py               # Infraction
│   ├── serializers.py          # Serializers de infracciones
│   ├── views.py                # CRUD + validación
│   └── admin.py                # Admin de infracciones
│
├── notifications/               # App de notificaciones
│   ├── models.py               # Notification
│   ├── serializers.py          # Serializers de notificaciones
│   ├── views.py                # ViewSets de notificaciones
│   └── consumers.py            # WebSocket consumers
│
├── manage.py                    # Django CLI
├── requirements.txt             # Dependencias Python
└── Dockerfile                   # Imagen Docker
```

---

## 🗄️ Modelos de Datos

### 1. **Authentication App**

#### User (Personalizado)
```python
User
├── id (UUID)
├── username (str, unique)
├── email (str, unique)
├── first_name (str)
├── last_name (str)
├── role (str: admin, operator, viewer)
├── is_active (bool)
├── is_staff (bool)
├── is_superuser (bool)
├── date_joined (datetime)
└── last_login (datetime)
```

**Roles disponibles:**
- `admin` - Acceso completo
- `operator` - Validación de infracciones
- `viewer` - Solo lectura

---

### 2. **Devices App**

#### Zone (Zona de tráfico)
```python
Zone
├── id (UUID)
├── code (str, unique) - Ej: "ZN001"
├── name (str) - Ej: "Av. Arequipa - Cruce Javier Prado"
├── description (text)
├── boundary (JSON) - GeoJSON del polígono
├── center_point_lat (decimal)
├── center_point_lon (decimal)
├── speed_limit (int) - Límite de velocidad en km/h
├── is_active (bool)
├── created_at (datetime)
└── updated_at (datetime)
```

**Relaciones:**
- `devices` - Dispositivos en esta zona (ForeignKey inversa)
- `infractions` - Infracciones en esta zona (ForeignKey inversa)

#### Device (Cámara/Dispositivo)
```python
Device
├── id (UUID)
├── code (str, unique) - Ej: "CAM001"
├── name (str) - Ej: "Cámara Norte"
├── device_type (str: camera, sensor, radar)
├── zone (FK → Zone)
├── location_lat (decimal)
├── location_lon (decimal)
├── address (str)
├── ip_address (IP)
├── rtsp_url (URL) - Stream RTSP
├── rtsp_username (str)
├── rtsp_password (str)
├── model (str) - Ej: "EZVIZ H6C Pro"
├── manufacturer (str)
├── firmware_version (str)
├── resolution (str) - Ej: "1920x1080"
├── fps (int)
├── calibration_matrix (JSON)
├── status (str: active, inactive, maintenance, error)
├── last_seen (datetime)
├── is_active (bool)
├── created_at (datetime)
└── updated_at (datetime)
```

**Relaciones:**
- `zone` - Zona donde está ubicado (ForeignKey)
- `infractions` - Infracciones detectadas por este dispositivo (ForeignKey inversa)

---

### 3. **Vehicles App**

#### Vehicle (Vehículo)
```python
Vehicle
├── id (UUID)
├── license_plate (str, unique) - Ej: "ABC-123"
├── make (str) - Marca
├── model (str) - Modelo
├── year (int)
├── color (str)
├── vehicle_type (str: car, truck, bus, motorcycle, bicycle, other)
├── owner_name (str) - Datos de SUNARP
├── owner_dni (str)
├── owner_address (text)
├── registration_date (date)
├── is_stolen (bool)
├── is_wanted (bool)
├── notes (text)
├── sunarp_last_updated (datetime)
├── created_at (datetime)
└── updated_at (datetime)
```

**Validación de placa:**
- Formato peruano: `ABC-123`, `AB-1234`, `A12-345`
- Regex: `^[A-Z]{3}-\d{3,4}$|^[A-Z]{2}-\d{4}$|^[A-Z]\d{2}-\d{3}$`

**Relaciones:**
- `infractions` - Infracciones del vehículo (ForeignKey inversa)
- `drivers` - Conductores asociados (ManyToMany)

#### Driver (Conductor)
```python
Driver
├── id (UUID)
├── document_type (str: dni, passport, foreign_card)
├── document_number (str, unique)
├── first_name (str)
├── last_name (str)
├── birth_date (date)
├── phone (str)
├── email (str)
├── address (text)
├── license_number (str)
├── license_class (str)
├── license_expiry (date)
├── has_infractions (bool)
├── risk_score (int) - 0-100
├── created_at (datetime)
└── updated_at (datetime)
```

**Relaciones:**
- `infractions` - Infracciones del conductor (ForeignKey inversa)
- `vehicles` - Vehículos asociados (ManyToMany)

---

### 4. **Infractions App**

#### Infraction (Infracción)
```python
Infraction
├── id (UUID)
├── infraction_code (str, unique) - Ej: "INF-2025-001234"
├── infraction_type (str: speed, red_light, wrong_lane, no_helmet, 
│                          parking, phone_use, seatbelt, other)
├── severity (str: low, medium, high, critical)
├── device (FK → Device)
├── zone (FK → Zone)
├── location_lat (decimal)
├── location_lon (decimal)
├── vehicle (FK → Vehicle, nullable)
├── driver (FK → Driver, nullable)
├── license_plate_detected (str)
├── license_plate_confidence (float) - 0.0 a 1.0
├── detected_speed (float) - km/h
├── speed_limit (int) - km/h
├── snapshot_url (URL) - URL en MinIO
├── video_url (URL) - URL en MinIO
├── evidence_metadata (JSON)
├── status (str: pending, validated, rejected, appealed, paid, dismissed)
├── reviewed_by (FK → User, nullable)
├── reviewed_at (datetime)
├── review_notes (text)
├── fine_amount (decimal)
├── fine_due_date (date)
├── payment_date (datetime)
├── detected_at (datetime) - Momento de detección
├── created_at (datetime)
└── updated_at (datetime)
```

**Estados:**
- `pending` - Pendiente de revisión
- `validated` - Validada por operador
- `rejected` - Rechazada (falso positivo)
- `appealed` - En proceso de apelación
- `paid` - Multa pagada
- `dismissed` - Desestimada

**Relaciones:**
- `device` - Dispositivo que detectó (ForeignKey)
- `zone` - Zona donde ocurrió (ForeignKey)
- `vehicle` - Vehículo infractor (ForeignKey, nullable)
- `driver` - Conductor infractor (ForeignKey, nullable)
- `reviewed_by` - Usuario que revisó (ForeignKey, nullable)

---

### 5. **Notifications App**

#### Notification (Notificación)
```python
Notification
├── id (UUID)
├── user (FK → User)
├── title (str)
├── message (text)
├── notification_type (str: info, warning, error, success, 
│                           infraction, device, system)
├── link (str) - URL opcional
├── is_read (bool)
├── created_at (datetime)
└── read_at (datetime)
```

**Relaciones:**
- `user` - Usuario destinatario (ForeignKey)

---

## 🌐 APIs REST

### Base URL
```
http://localhost:8000/api/
```

### Endpoints Principales

#### 1. Authentication
```
POST   /api/auth/login/          - Login (retorna JWT)
POST   /api/auth/register/       - Registro de usuario
POST   /api/auth/logout/         - Logout
POST   /api/auth/refresh/        - Refresh token
GET    /api/auth/me/             - Usuario actual
```

**Ejemplo Login:**
```json
POST /api/auth/login/
{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

---

#### 2. Devices
```
GET    /api/devices/              - Listar dispositivos
POST   /api/devices/              - Crear dispositivo
GET    /api/devices/{id}/         - Detalle dispositivo
PUT    /api/devices/{id}/         - Actualizar dispositivo
DELETE /api/devices/{id}/         - Eliminar dispositivo
GET    /api/devices/{id}/status/  - Estado del dispositivo
POST   /api/devices/{id}/start/   - Iniciar stream
POST   /api/devices/{id}/stop/    - Detener stream
```

#### 3. Zones
```
GET    /api/zones/                - Listar zonas
POST   /api/zones/                - Crear zona
GET    /api/zones/{id}/           - Detalle zona
PUT    /api/zones/{id}/           - Actualizar zona
DELETE /api/zones/{id}/           - Eliminar zona
GET    /api/zones/{id}/devices/   - Dispositivos en zona
GET    /api/zones/{id}/infractions/ - Infracciones en zona
```

---

#### 4. Infractions
```
GET    /api/infractions/          - Listar infracciones
POST   /api/infractions/          - Crear infracción (desde Inference)
GET    /api/infractions/{id}/     - Detalle infracción
PUT    /api/infractions/{id}/     - Actualizar infracción
DELETE /api/infractions/{id}/     - Eliminar infracción
POST   /api/infractions/{id}/validate/   - Validar infracción
POST   /api/infractions/{id}/reject/     - Rechazar infracción
GET    /api/infractions/stats/    - Estadísticas
GET    /api/infractions/pending/  - Pendientes de revisión
```

**Filtros disponibles:**
- `?status=pending` - Por estado
- `?infraction_type=speed` - Por tipo
- `?device=uuid` - Por dispositivo
- `?zone=uuid` - Por zona
- `?date_from=2025-11-01` - Desde fecha
- `?date_to=2025-11-30` - Hasta fecha

**Ejemplo:**
```json
GET /api/infractions/?status=pending&infraction_type=speed

Response:
{
  "count": 42,
  "next": "http://localhost:8000/api/infractions/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "infraction_code": "INF-2025-001234",
      "infraction_type": "speed",
      "severity": "high",
      "detected_speed": 95.5,
      "speed_limit": 60,
      "license_plate_detected": "ABC-123",
      "status": "pending",
      "detected_at": "2025-11-02T10:30:00Z",
      "device": {...},
      "zone": {...}
    }
  ]
}
```

---

#### 5. Vehicles
```
GET    /api/vehicles/             - Listar vehículos
POST   /api/vehicles/             - Crear vehículo
GET    /api/vehicles/{id}/        - Detalle vehículo
PUT    /api/vehicles/{id}/        - Actualizar vehículo
DELETE /api/vehicles/{id}/        - Eliminar vehículo
POST   /api/vehicles/enrich/      - Consultar SUNARP
GET    /api/vehicles/{id}/infractions/ - Infracciones del vehículo
```

#### 6. Drivers
```
GET    /api/drivers/              - Listar conductores
POST   /api/drivers/              - Crear conductor
GET    /api/drivers/{id}/         - Detalle conductor
PUT    /api/drivers/{id}/         - Actualizar conductor
DELETE /api/drivers/{id}/         - Eliminar conductor
GET    /api/drivers/{id}/infractions/ - Infracciones del conductor
```

---

#### 7. Notifications
```
GET    /api/notifications/        - Listar notificaciones
GET    /api/notifications/{id}/   - Detalle notificación
POST   /api/notifications/{id}/mark-read/ - Marcar como leída
POST   /api/notifications/mark-all-read/  - Marcar todas como leídas
DELETE /api/notifications/{id}/   - Eliminar notificación
```

---

#### 8. Reports
```
GET    /api/reports/daily/        - Reporte diario
GET    /api/reports/weekly/       - Reporte semanal
GET    /api/reports/monthly/      - Reporte mensual
GET    /api/reports/by-zone/      - Por zona
GET    /api/reports/by-device/    - Por dispositivo
GET    /api/reports/export/       - Exportar (PDF/Excel)
```

---

## ⚙️ Funcionalidades

### 1. Autenticación y Autorización
- **JWT (JSON Web Tokens)** para autenticación stateless
- **Refresh tokens** para renovación automática
- **Permisos por rol** (admin, operator, viewer)
- **Token blacklist** para logout seguro

### 2. Gestión de Infracciones
- CRUD completo de infracciones
- **Validación manual** por operadores
- **Rechazo de falsos positivos**
- **Workflow de estados** (pending → validated → paid)
- **Filtros avanzados** (fecha, tipo, zona, estado)
- **Búsqueda por placa**

### 3. Integración SUNARP
- Consulta automática de datos de vehículos
- **Cache de resultados** en Redis (24 horas)
- Enriquecimiento de datos de propietario
- Validación de placas peruanas

### 4. Sistema de Notificaciones
- Notificaciones en tiempo real vía **WebSocket**
- Notificaciones por tipo (info, warning, error, infracción, dispositivo)
- **Push notifications** para nuevas infracciones
- Historial de notificaciones

### 5. Reportes y Analytics
- Reportes diarios, semanales, mensuales
- Estadísticas por zona
- Estadísticas por dispositivo
- Estadísticas por tipo de infracción
- **Exportación a PDF y Excel**

### 6. Panel Administrativo Django
- Interfaz web para administradores
- CRUD visual de todas las entidades
- Búsqueda y filtros avanzados
- Acciones en lote
- **URL:** `http://localhost:8000/admin/`

---

## 🔗 Relaciones con Otros Componentes

### 1. Backend Django ↔️ Inference Service
**Comunicación:** HTTP REST API + RabbitMQ

**Django → Inference:**
- `POST /start-stream/{device_id}` - Iniciar procesamiento
- `POST /stop-stream/{device_id}` - Detener procesamiento
- `GET /stream-status/{device_id}` - Consultar estado

**Inference → Django:**
- Publica eventos en RabbitMQ:
  - `infraction.detected`
  - `vehicle.tracked`
  - `plate.recognized`
- Django consume estos eventos y crea registros en la BD

---

### 2. Backend Django ↔️ Frontend Dashboard
**Comunicación:** HTTP REST API + WebSocket

**Frontend → Django:**
- Consume todos los endpoints REST
- Autenticación con JWT

**Django → Frontend:**
- **WebSocket** en `ws://localhost:8000/ws/notifications/`
- Envia notificaciones en tiempo real
- Actualiza dashboard automáticamente

---

### 3. Backend Django ↔️ PostgreSQL
**Comunicación:** TCP/IP (puerto 5432)

- ORM de Django para todas las operaciones
- Migraciones automáticas
- Índices optimizados

---

### 4. Backend Django ↔️ Redis
**Comunicación:** Redis Protocol (puerto 6379)

**Usos:**
- Cache de sesiones de usuario
- Cache de respuestas API
- Cache de consultas SUNARP
- Storage para WebSocket (Django Channels)

---

### 5. Backend Django ↔️ RabbitMQ
**Comunicación:** AMQP (puerto 5672)

**Colas consumidas:**
- `infractions.detected` - Nuevas infracciones
- `devices.status` - Estado de dispositivos

**Colas producidas:**
- `notifications.send` - Envío de notificaciones

---

## 🔧 Configuración

### Variables de Entorno (.env)

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DATABASE_URL=postgresql://postgres:postgres123!@postgres:5432/traffic_system
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123!
POSTGRES_DB=traffic_system

# Redis
REDIS_URL=redis://redis:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://admin:SecurePassword123!@rabbitmq:5672/
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=SecurePassword123!

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=SecurePassword123!
MINIO_USE_SSL=False

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60  # minutos
JWT_REFRESH_TOKEN_LIFETIME=1440  # minutos (24 horas)

# SUNARP
SUNARP_API_KEY=your-sunarp-api-key
SUNARP_API_URL=https://api.sunarp.gob.pe/v1/
```

### Comandos Útiles

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Cargar datos de prueba
python manage.py loaddata seed_data.json

# Ejecutar servidor de desarrollo
python manage.py runserver 0.0.0.0:8000

# Crear datos de ejemplo
python seed_data.py

# Shell interactivo
python manage.py shell
```

---

## 📊 Responsabilidades

✅ **Sí gestiona:**
- Usuarios y autenticación
- CRUD de todas las entidades
- Persistencia en base de datos
- Notificaciones
- Reportes
- Panel administrativo

❌ **No gestiona:**
- Procesamiento de video
- Detección de vehículos
- Reconocimiento de placas
- Inferencia con ML

---

## 📝 Notas Importantes

1. **Django NO detecta infracciones directamente**, solo las gestiona después de ser detectadas por Inference/ML Service

2. **Todas las infracciones** pasan por validación manual antes de emitir multa

3. **SUNARP** es consultado automáticamente, pero puede fallar (servicio externo)

4. **WebSocket** requiere Redis como backend de channels

5. **Django Admin** está disponible en `/admin/` para gestión rápida

---

**Ver también:**
- [ARQUITECTURA.md](./ARQUITECTURA.md) - Visión general del sistema
- [INFERENCE-SERVICE.md](./INFERENCE-SERVICE.md) - Servicio de inferencia
- [ML-SERVICE.md](./ML-SERVICE.md) - Módulos de ML
- [FLUJOS-DETECCION.md](./FLUJOS-DETECCION.md) - Flujos de detección

---

**Última actualización:** Noviembre 2025
