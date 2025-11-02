# FastAPI Inference Service

Microservicio para procesamiento de video en tiempo real y detección de infracciones de tránsito.

## 🚀 Características

- **FastAPI**: Framework moderno y rápido para APIs REST
- **Procesamiento RTSP**: Conexión a cámaras IoT via RTSP con OpenCV
- **Streaming asíncrono**: Manejo de múltiples streams simultáneos
- **Health checks**: Monitoreo de estado de servicios
- **Logging estructurado**: Logs JSON con structlog
- **Tests**: Cobertura >80% con pytest
- **Docker**: Contenedor optimizado con OpenCV

## 📋 Endpoints

### Health Check
- `GET /api/health` - Estado del servicio y dependencias
- `GET /api/` - Información básica del servicio

### Stream Management
- `POST /api/inference/stream/start` - Iniciar procesamiento de stream RTSP
- `POST /api/inference/stream/stop/{stream_id}` - Detener stream
- `GET /api/inference/stream/status/{stream_id}` - Estado de stream específico
- `GET /api/inference/streams` - Lista de todos los streams activos

## 🛠️ Desarrollo Local

### Requisitos
- Python 3.11+
- Docker & Docker Compose
- OpenCV dependencies

### Instalación

1. **Instalar dependencias**:
```bash
cd inference-service
pip install -r requirements.txt
```

2. **Configurar variables de entorno**:
```bash
cp .env.example .env
# Editar .env con configuración local
```

3. **Ejecutar tests**:
```bash
pytest
```

4. **Ejecutar localmente**:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Con Docker

1. **Build y ejecutar**:
```bash
docker build -t traffic-inference .
docker run -p 8001:8001 --env-file .env traffic-inference
```

2. **Con docker-compose** (desde raíz del proyecto):
```bash
docker-compose up inference
```

## 📖 Documentación API

Una vez ejecutando el servicio, la documentación interactiva está disponible en:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI Schema**: http://localhost:8001/api/openapi.json

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app

# Tests específicos
pytest tests/test_api.py
pytest tests/test_services.py
```

## 📁 Estructura del Proyecto

```
inference-service/
├── app/
│   ├── api/              # Endpoints REST
│   │   ├── health.py     # Health checks
│   │   └── inference.py  # Stream management
│   ├── core/             # Configuración
│   │   ├── config.py     # Settings
│   │   └── logging.py    # Structured logging
│   ├── models/           # Pydantic schemas
│   │   └── schemas.py    # Request/Response models
│   ├── services/         # Lógica de negocio
│   │   ├── health.py     # Health service
│   │   └── stream.py     # Stream management
│   └── main.py           # FastAPI app
├── tests/                # Tests unitarios
├── Dockerfile            # Container config
├── requirements.txt      # Python dependencies
└── README.md            # Esta documentación
```

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `APP_NAME` | Nombre del servicio | Traffic Inference Service |
| `DEBUG` | Modo debug | false |
| `HOST` | Host del servidor | 0.0.0.0 |
| `PORT` | Puerto del servidor | 8001 |
| `DATABASE_URL` | URL PostgreSQL | postgresql+asyncpg://... |
| `REDIS_URL` | URL Redis | redis://redis:6379/0 |
| `RABBITMQ_URL` | URL RabbitMQ | amqp://admin:...@rabbitmq:5672/ |
| `MINIO_ENDPOINT` | Endpoint MinIO | minio:9000 |
| `MAX_CONCURRENT_STREAMS` | Streams simultáneos máx | 10 |
| `LOG_LEVEL` | Nivel de logging | INFO |
| `LOG_FORMAT` | Formato logs | json |

### Logging

El servicio usa **structlog** para logging estructurado:

- **Desarrollo**: Logs con formato console coloreado
- **Producción**: Logs en formato JSON para agregación

Niveles disponibles: DEBUG, INFO, WARNING, ERROR, CRITICAL

## 🚀 Próximas Funcionalidades

- **YOLOv8 Integration**: Detección de vehículos
- **DeepSort Tracking**: Seguimiento de objetos  
- **OCR de Placas**: Extracción de números de placa
- **Event Publishing**: Publicación a RabbitMQ
- **MinIO Storage**: Almacenamiento de evidencia
- **WebSocket Streaming**: Stream en tiempo real

## 🐛 Troubleshooting

### Errores Comunes

1. **OpenCV no funciona en Docker**:
```bash
# Verificar que las librerías están instaladas
apt-get update && apt-get install -y libgl1-mesa-glx
```

2. **No se puede conectar a RTSP**:
```bash
# Verificar URL y credenciales
ffplay rtsp://username:password@camera-ip:554/stream
```

3. **Tests fallan**:
```bash
# Verificar dependencias de test
pip install pytest pytest-asyncio pytest-cov httpx
```

## 📝 Logging Examples

```python
from app.core import get_logger

logger = get_logger(__name__)

# Info con contexto
logger.info("Stream started", stream_id="123", camera_id="CAM001")

# Error con detalles
logger.error("Stream failed", stream_id="123", error=str(e))

# Timing
with logger.bind(operation="health_check"):
    logger.info("Starting health check")
    # ... operación
    logger.info("Health check completed", duration_ms=125.5)
```