# Infrastructure - Infraestructura y Servicios

## 📋 Índice
- [Visión General](#visión-general)
- [PostgreSQL - Base de Datos Principal](#postgresql---base-de-datos-principal)
- [Redis - Cache y Sesiones](#redis---cache-y-sesiones)
- [RabbitMQ - Message Broker](#rabbitmq---message-broker)
- [MinIO - Object Storage](#minio---object-storage)
- [Docker Compose](#docker-compose)
- [Configuración y Puertos](#configuración-y-puertos)

---

## 🎯 Visión General

La infraestructura del sistema está compuesta por servicios de backend que proporcionan:
- Persistencia de datos (PostgreSQL)
- Cache y sesiones (Redis)
- Mensajería asíncrona (RabbitMQ)
- Almacenamiento de archivos (MinIO)

Todos los servicios están containerizados con **Docker** y orquestados con **Docker Compose**.

---

## 🐘 PostgreSQL - Base de Datos Principal

### Descripción
**PostgreSQL 16** es la base de datos relacional principal del sistema. Almacena todos los datos estructurados.

**Versión:** 16-alpine  
**Puerto:** 5432  
**Container:** `traffic-postgres`

---

### Esquemas y Tablas

#### 1. **authentication_user**
Usuario del sistema
- Campos: id, username, email, password, role, is_active, etc.
- Relaciones: 1:N con Notification, Infraction (reviewed_by)

#### 2. **devices_zone**
Zonas de monitoreo
- Campos: id, code, name, speed_limit, boundary (GeoJSON), etc.
- Relaciones: 1:N con Device, Infraction

#### 3. **devices_device**
Dispositivos/cámaras
- Campos: id, code, name, ip_address, rtsp_url, status, zone_id, etc.
- Relaciones: N:1 con Zone, 1:N con Infraction

#### 4. **vehicles_vehicle**
Vehículos
- Campos: id, license_plate, make, model, owner_name, owner_dni, etc.
- Relaciones: 1:N con Infraction

#### 5. **vehicles_driver**
Conductores
- Campos: id, document_number, first_name, last_name, license_number, etc.
- Relaciones: 1:N con Infraction

#### 6. **infractions_infraction**
Infracciones detectadas
- Campos: id, infraction_code, type, severity, device_id, zone_id, vehicle_id, detected_speed, status, etc.
- Relaciones: N:1 con Device, Zone, Vehicle, Driver, User

#### 7. **notifications_notification**
Notificaciones de usuarios
- Campos: id, user_id, title, message, type, is_read, created_at, etc.
- Relaciones: N:1 con User

---

### Configuración

**Variables de entorno:**
```bash
POSTGRES_DB=traffic_system
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123!
POSTGRES_INITDB_ARGS=-E UTF8
```

**Volumen:**
```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
  - ./infrastructure/postgres/init:/docker-entrypoint-initdb.d
```

**Health check:**
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres -d traffic_system"]
  interval: 10s
  timeout: 5s
  retries: 5
```

---

### Optimizaciones

#### Índices
- `devices_device.code` - Búsqueda rápida por código
- `devices_device.status` - Filtrado por estado
- `infractions_infraction.detected_at` - Ordenamiento por fecha
- `infractions_infraction.license_plate_detected` - Búsqueda por placa
- `infractions_infraction.status` - Filtrado por estado
- `vehicles_vehicle.license_plate` - Búsqueda por placa

#### Conexión desde servicios

**Django:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'traffic_system',
        'USER': 'postgres',
        'PASSWORD': 'postgres123!',
        'HOST': 'postgres',
        'PORT': '5432',
    }
}
```

**FastAPI (SQLAlchemy):**
```python
DATABASE_URL = "postgresql://postgres:postgres123!@postgres:5432/traffic_system"
engine = create_engine(DATABASE_URL)
```

---

### Backups

**Backup manual:**
```bash
docker exec traffic-postgres pg_dump -U postgres traffic_system > backup.sql
```

**Restore:**
```bash
docker exec -i traffic-postgres psql -U postgres traffic_system < backup.sql
```

**Backup automatizado (cron):**
```bash
# Diario a las 2 AM
0 2 * * * docker exec traffic-postgres pg_dump -U postgres traffic_system | gzip > /backups/traffic_$(date +\%Y\%m\%d).sql.gz
```

---

## 🔴 Redis - Cache y Sesiones

### Descripción
**Redis 7** es un almacén de datos en memoria usado para cache, sesiones y datos temporales.

**Versión:** 7-alpine  
**Puerto:** 6379  
**Container:** `traffic-redis`

---

### Usos en el Sistema

#### 1. **Cache de Sesiones Django**
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

#### 2. **Cache de Consultas SUNARP**
```python
# Cachear por 24 horas
cache_key = f"sunarp:vehicle:{plate}"
cached_data = redis.get(cache_key)

if cached_data:
    return json.loads(cached_data)
else:
    data = fetch_from_sunarp(plate)
    redis.setex(cache_key, 86400, json.dumps(data))  # 24 horas
    return data
```

#### 3. **Backend para Django Channels (WebSocket)**
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis', 6379)],
        },
    },
}
```

#### 4. **Cache de Respuestas API**
```python
# Cachear endpoint por 5 minutos
@cache_page(60 * 5)
def list_infractions(request):
    # ...
```

#### 5. **Rate Limiting**
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h', block=True)
def api_endpoint(request):
    # ...
```

#### 6. **Datos Temporales de Tracking**
```python
# Guardar tracking temporal (expira en 1 hora)
tracking_key = f"tracking:vehicle:{track_id}"
redis.setex(tracking_key, 3600, json.dumps(vehicle_data))
```

---

### Configuración

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
```

**Políticas de evicción:**
- `allkeys-lru` - Elimina las claves menos usadas cuando se alcanza el límite de memoria

**Persistencia:**
- `appendonly yes` - Habilita AOF (Append Only File) para persistencia

---

### Comandos Útiles

```bash
# Conectar a Redis CLI
docker exec -it traffic-redis redis-cli

# Ver todas las claves
KEYS *

# Ver info de servidor
INFO

# Vaciar base de datos
FLUSHDB

# Ver memoria usada
INFO memory

# Monitorear comandos en tiempo real
MONITOR
```

---

## 🐰 RabbitMQ - Message Broker

### Descripción
**RabbitMQ 3.12** es el message broker usado para comunicación asíncrona entre servicios.

**Versión:** 3.12-management-alpine  
**Puerto AMQP:** 5672  
**Puerto Management UI:** 15672  
**Container:** `traffic-rabbitmq`

---

### Colas (Queues)

#### 1. **infractions.detected**
**Productor:** ML Service (ViolationDetector)  
**Consumidor:** Backend Django  
**Propósito:** Notificar nueva infracción detectada

**Mensaje:**
```json
{
  "event_type": "infraction_detected",
  "violation_id": "uuid",
  "timestamp": "2025-11-02T10:30:45.123Z",
  "device_id": "CAM001",
  "zone_id": "ZN001",
  "infraction_type": "speed",
  "severity": "high",
  "vehicle": {
    "track_id": 42,
    "license_plate": "ABC-123",
    "plate_confidence": 0.87
  },
  "speed": {
    "detected": 95.5,
    "limit": 60
  },
  "evidence": {
    "snapshot_url": "...",
    "video_url": "..."
  }
}
```

---

#### 2. **vehicles.tracked**
**Productor:** Inference Service  
**Consumidor:** ML Service  
**Propósito:** Información de vehículos trackeados para análisis

**Mensaje:**
```json
{
  "event_type": "vehicle_tracked",
  "timestamp": "2025-11-02T10:30:45.123Z",
  "device_id": "CAM001",
  "vehicles": [
    {
      "track_id": 42,
      "class": "car",
      "bbox": [100, 150, 300, 400],
      "position": [320, 240],
      "velocity": 65.3
    }
  ]
}
```

---

#### 3. **plates.recognized**
**Productor:** Inference Service  
**Consumidor:** Backend Django  
**Propósito:** Placa reconocida con éxito

**Mensaje:**
```json
{
  "event_type": "plate_recognized",
  "timestamp": "2025-11-02T10:30:45.123Z",
  "device_id": "CAM001",
  "track_id": 42,
  "license_plate": "ABC-123",
  "confidence": 0.87,
  "snapshot_url": "..."
}
```

---

#### 4. **devices.status**
**Productor:** Inference Service  
**Consumidor:** Backend Django  
**Propósito:** Cambio de estado de dispositivo

**Mensaje:**
```json
{
  "event_type": "device_status_changed",
  "timestamp": "2025-11-02T10:30:45.123Z",
  "device_id": "CAM001",
  "old_status": "active",
  "new_status": "error",
  "error_message": "Connection timeout"
}
```

---

#### 5. **notifications.send**
**Productor:** Backend Django  
**Consumidor:** Notification Service (futuro)  
**Propósito:** Enviar notificación a usuarios

---

### Configuración

```yaml
rabbitmq:
  image: rabbitmq:3.12-management-alpine
  environment:
    RABBITMQ_DEFAULT_USER: admin
    RABBITMQ_DEFAULT_PASS: SecurePassword123!
    RABBITMQ_DEFAULT_VHOST: /
  ports:
    - "5672:5672"    # AMQP
    - "15672:15672"  # Management UI
  volumes:
    - rabbitmq_data:/var/lib/rabbitmq
```

---

### Uso en Servicios

#### Publicar mensaje (Python - Pika)
```python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters('rabbitmq')
)
channel = connection.channel()

channel.queue_declare(queue='infractions.detected', durable=True)

message = {
    'event_type': 'infraction_detected',
    'violation_id': 'uuid',
    # ...
}

channel.basic_publish(
    exchange='',
    routing_key='infractions.detected',
    body=json.dumps(message),
    properties=pika.BasicProperties(
        delivery_mode=2,  # Persistent
    )
)

connection.close()
```

#### Consumir mensaje (Python - Pika)
```python
def callback(ch, method, properties, body):
    message = json.loads(body)
    print(f"Received: {message}")
    
    # Procesar mensaje
    process_infraction(message)
    
    # Acknowledge
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(
    queue='infractions.detected',
    on_message_callback=callback
)

print('Waiting for messages...')
channel.start_consuming()
```

---

### Management UI

**URL:** `http://localhost:15672`  
**Usuario:** admin  
**Password:** SecurePassword123!

**Funcionalidades:**
- Ver colas y exchanges
- Monitorear mensajes
- Ver conexiones activas
- Crear/eliminar colas
- Estadísticas de rendimiento

---

## 📦 MinIO - Object Storage

### Descripción
**MinIO** es un almacenamiento de objetos compatible con S3, usado para guardar videos, imágenes y modelos ML.

**Puerto API:** 9000  
**Puerto Console:** 9001  
**Container:** `traffic-minio`

---

### Buckets

#### 1. **traffic-snapshots**
**Contenido:** Imágenes de evidencia (snapshots)  
**Política:** Download público (read-only)  
**Estructura:**
```
traffic-snapshots/
├── 2025-11-02/
│   ├── cam001_1698912345_vehicle.jpg
│   ├── cam001_1698912345_plate.jpg
│   └── cam002_1698912456_vehicle.jpg
└── 2025-11-03/
    └── ...
```

---

#### 2. **traffic-videos**
**Contenido:** Videos de evidencia  
**Política:** Download público (read-only)  
**Estructura:**
```
traffic-videos/
├── 2025-11-02/
│   ├── cam001_1698912345_10s.mp4
│   └── cam002_1698912456_10s.mp4
└── 2025-11-03/
    └── ...
```

---

#### 3. **ml-models**
**Contenido:** Modelos de machine learning  
**Política:** Privado  
**Estructura:**
```
ml-models/
├── yolo/
│   ├── yolov8n.pt
│   └── yolov8s.pt
├── ocr/
│   └── easyocr_models/
└── tracking/
    └── deepsort_weights.pt
```

---

### Configuración

```yaml
minio:
  image: minio/minio:latest
  command: server /data --console-address ":9001"
  environment:
    MINIO_ROOT_USER: admin
    MINIO_ROOT_PASSWORD: SecurePassword123!
  ports:
    - "9000:9000"  # API
    - "9001:9001"  # Console
  volumes:
    - minio_data:/data
```

---

### Inicialización de Buckets

```yaml
minio-init:
  image: minio/mc:latest
  depends_on:
    - minio
  entrypoint: >
    /bin/sh -c "
    mc alias set myminio http://minio:9000 admin SecurePassword123!;
    mc mb --ignore-existing myminio/traffic-snapshots;
    mc mb --ignore-existing myminio/traffic-videos;
    mc mb --ignore-existing myminio/ml-models;
    mc policy set download myminio/traffic-snapshots;
    mc policy set download myminio/traffic-videos;
    exit 0;
    "
```

---

### Uso en Servicios

#### Subir archivo (Python - boto3)
```python
import boto3
from datetime import datetime

s3_client = boto3.client(
    's3',
    endpoint_url='http://minio:9000',
    aws_access_key_id='admin',
    aws_secret_access_key='SecurePassword123!',
    region_name='us-east-1'
)

# Subir snapshot
file_path = '/tmp/snapshot.jpg'
bucket = 'traffic-snapshots'
object_name = f"{datetime.now().strftime('%Y-%m-%d')}/cam001_{int(datetime.now().timestamp())}.jpg"

s3_client.upload_file(file_path, bucket, object_name)

# URL pública
url = f"http://minio:9000/{bucket}/{object_name}"
```

#### Descargar archivo
```python
s3_client.download_file(bucket, object_name, '/tmp/downloaded.jpg')
```

---

### MinIO Console

**URL:** `http://localhost:9001`  
**Usuario:** admin  
**Password:** SecurePassword123!

**Funcionalidades:**
- Explorar buckets
- Subir/descargar archivos
- Ver estadísticas de uso
- Configurar políticas
- Gestionar usuarios

---

## 🐳 Docker Compose

### Archivo: `docker-compose.yml`

**Servicios definidos:**
1. `postgres` - Base de datos
2. `redis` - Cache
3. `rabbitmq` - Message broker
4. `minio` - Object storage
5. `minio-init` - Inicialización de buckets
6. `django` - Backend Django
7. `inference` - Inference Service
8. `frontend` - Frontend Dashboard (opcional)

---

### Network

```yaml
networks:
  traffic-network:
    driver: bridge
```

Todos los servicios están en la misma red `traffic-network`, permitiendo comunicación por nombre de servicio.

---

### Volumes

```yaml
volumes:
  postgres_data:      # Datos de PostgreSQL
  redis_data:         # Datos de Redis (AOF)
  rabbitmq_data:      # Datos de RabbitMQ
  minio_data:         # Objetos de MinIO
  django_static:      # Archivos estáticos Django
  django_media:       # Archivos media Django
  ml_models:          # Modelos ML
  camera_calibrations: # Calibraciones de cámara
```

---

### Comandos Docker Compose

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f django

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v

# Reiniciar un servicio
docker-compose restart django

# Ver estado
docker-compose ps

# Ejecutar comando en contenedor
docker-compose exec django python manage.py migrate
```

---

## 🔧 Configuración y Puertos

### Tabla de Puertos

| Servicio | Puerto(s) | Propósito |
|----------|-----------|-----------|
| PostgreSQL | 5432 | Base de datos |
| Redis | 6379 | Cache |
| RabbitMQ | 5672, 15672 | AMQP, Management UI |
| MinIO | 9000, 9001 | API S3, Console |
| Django | 8000 | API REST |
| Inference | 8001 | API Inference |
| Frontend | 3000 | Dashboard web |

---

### Variables de Entorno Compartidas

```bash
# .env file
DB_NAME=traffic_system
DB_USER=postgres
DB_PASSWORD=postgres123!

REDIS_PASSWORD=

RABBITMQ_USER=admin
RABBITMQ_PASSWORD=SecurePassword123!

MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=SecurePassword123!

DJANGO_SECRET_KEY=django-insecure-change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 📊 Monitoreo y Logs

### Logs de Contenedores
```bash
# Ver logs en tiempo real
docker-compose logs -f

# Últimas 100 líneas
docker-compose logs --tail=100

# Logs de un servicio
docker-compose logs -f postgres
```

### Health Checks

Todos los servicios tienen health checks configurados:
```yaml
healthcheck:
  test: ["CMD", "pg_isready", "-U", "postgres"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**Ver estado:**
```bash
docker-compose ps
```

---

## 🔒 Seguridad

### Recomendaciones de Producción

1. **Cambiar contraseñas por defecto**
2. **Usar variables de entorno secretas**
3. **Habilitar SSL/TLS** en todos los servicios
4. **Configurar firewall** (solo puertos necesarios)
5. **Backups automatizados** de PostgreSQL
6. **Limitar acceso a Management UIs**
7. **Implementar rotación de logs**
8. **Usar secrets de Docker/Kubernetes**

---

**Ver también:**
- [ARQUITECTURA.md](./ARQUITECTURA.md) - Visión general
- [BACKEND-DJANGO.md](./BACKEND-DJANGO.md) - Uso de PostgreSQL
- [INFERENCE-SERVICE.md](./INFERENCE-SERVICE.md) - Uso de MinIO

---

**Última actualización:** Noviembre 2025
