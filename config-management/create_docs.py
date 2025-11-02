"""
Documentación del Sistema de Configuración Avanzada
===================================================

Guía completa para el uso y administración del sistema de configuración.
"""

# Crear documentación
readme_content = """# Sistema de Configuración Avanzada

Sistema centralizado para gestionar toda la configuración del sistema de detección de infracciones de tráfico.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Instalación](#instalación)
- [Uso](#uso)
- [API](#api)
- [CLI](#cli)
- [Interfaz Web](#interfaz-web)
- [Configuración](#configuración)
- [Ejemplos](#ejemplos)
- [Troubleshooting](#troubleshooting)

## 🚀 Características

### Gestión Centralizada
- **Configuración del Sistema**: Settings globales, conexiones DB, cache, logging
- **Configuración de Cámaras**: Gestión completa de cámaras RTSP, calibración, zonas
- **Configuración ML**: Modelos YOLO, parámetros de detección, optimizaciones
- **Configuración de Detección**: Umbrales, filtros, tracking, OCR

### Interfaces Múltiples
- **API REST**: Endpoints completos para CRUD de configuraciones
- **CLI**: Command Line Interface para administración por terminal
- **Interfaz Web**: Dashboard moderno con React y TypeScript
- **WebSocket**: Notificaciones en tiempo real de cambios

### Funciones Avanzadas
- **Validación**: Verificación automática de configuraciones
- **Import/Export**: Respaldo e importación en YAML/JSON
- **Versionado**: Control de cambios y rollback
- **Monitoreo**: Métricas y health checks integrados

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │       CLI       │    │   External API  │
│    (React TS)   │    │    (Click)      │    │   Integrations  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴───────────┐
                    │     FastAPI Server      │
                    │   (Configuration API)   │
                    └─────────────┬───────────┘
                                  │
                    ┌─────────────┴───────────┐
                    │   Configuration Manager │
                    │     (Core Engine)       │
                    └─────────────┬───────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
   ┌──────┴──────┐    ┌──────────┴──────────┐    ┌───────┴───────┐
   │ YAML Files  │    │   Database Config   │    │ Environment   │
   │ (Local)     │    │   (PostgreSQL)      │    │ Variables     │
   └─────────────┘    └─────────────────────┘    └───────────────┘
```

## 📦 Instalación

### Requisitos
- Python 3.8+
- Node.js 16+ (para interfaz web)
- PostgreSQL (opcional, para config persistente)
- Redis (para cache)

### Backend (API + Core)

```bash
# Clonar repositorio
git clone <repo-url>
cd config-management

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones
```

### Frontend (Interfaz Web)

```bash
cd web
npm install
```

## 🖥️ Uso

### Iniciar Servicios

```bash
# Backend API
uvicorn api:app --host 0.0.0.0 --port 8080 --reload

# Frontend (en otra terminal)
cd web
npm run dev
```

### Acceder a Interfaces
- **API Docs**: http://localhost:8080/docs
- **Web Interface**: http://localhost:3000
- **CLI**: `python cli.py --help`

## 🔌 API

### Endpoints Principales

#### Sistema
```http
GET /config/system                    # Obtener configuración del sistema
PUT /config/system                    # Actualizar configuración del sistema
```

#### Cámaras
```http
GET /config/cameras                   # Listar todas las cámaras
GET /config/cameras/{camera_id}       # Obtener cámara específica
POST /config/cameras/{camera_id}      # Crear nueva cámara
PUT /config/cameras/{camera_id}       # Actualizar cámara
DELETE /config/cameras/{camera_id}    # Eliminar cámara
PATCH /config/cameras/{camera_id}/status # Activar/desactivar cámara
```

#### Modelos ML
```http
GET /config/ml                        # Listar modelos ML
GET /config/ml/{model_name}           # Obtener modelo específico
POST /config/ml/{model_name}          # Crear nuevo modelo
PUT /config/ml/{model_name}           # Actualizar modelo
DELETE /config/ml/{model_name}        # Eliminar modelo
```

#### Detección
```http
GET /config/detection                 # Obtener configuración de detección
PUT /config/detection                 # Actualizar configuración de detección
PATCH /config/detection/threshold/{type} # Actualizar umbral específico
```

#### Utilidades
```http
POST /config/validate                 # Validar configuraciones
GET /config/export?format=yaml       # Exportar configuraciones
POST /config/import                   # Importar configuraciones
GET /config/backup                    # Crear backup
```

### Autenticación

```bash
# Todas las llamadas requieren token JWT
curl -H "Authorization: Bearer <token>" \
     http://localhost:8080/config/system
```

## 💻 CLI

### Comandos Básicos

```bash
# Inicializar configuración
python cli.py init

# Validar configuraciones
python cli.py validate

# Ver estado del sistema
python cli.py status
python cli.py status --watch  # Modo continuo
```

### Configuración del Sistema

```bash
# Ver configuración
python cli.py system show

# Modificar valores
python cli.py system set database_url "postgresql://..."
python cli.py system set log_level "DEBUG"
```

### Gestión de Cámaras

```bash
# Listar cámaras
python cli.py cameras list
python cli.py cameras list --active-only

# Ver cámara específica
python cli.py cameras show CAM001

# Agregar nueva cámara
python cli.py cameras add CAM002 \
  --name "Cámara Av. Brasil" \
  --rtsp-url "rtsp://192.168.1.101:554/stream1" \
  --lat -12.0864 \
  --lon -77.0365 \
  --speed-limit 50

# Activar/desactivar cámara
python cli.py cameras enable CAM001
python cli.py cameras disable CAM001
```

### Modelos ML

```bash
# Listar modelos
python cli.py models list

# Ver modelo específico
python cli.py models show yolov8n_vehicles
```

### Configuración de Detección

```bash
# Ver configuración
python cli.py detection show

# Actualizar umbrales
python cli.py detection set-threshold speed_threshold_warning 8
python cli.py detection set-threshold ocr_confidence_threshold 0.85
```

### Import/Export

```bash
# Exportar configuración
python cli.py config export --format yaml --output backup.yaml

# Importar configuración
python cli.py config import backup.yaml --format yaml

# Crear backup con timestamp
python cli.py config backup --output-dir /backups
```

## 🌐 Interfaz Web

### Dashboard Principal
- **Resumen del Sistema**: Estado general, métricas clave
- **Mapa de Cámaras**: Visualización geográfica de cámaras activas
- **Gráficos en Tiempo Real**: Estadísticas de detección

### Gestión de Configuraciones
- **Editor Visual**: Formularios intuitivos para cada tipo de configuración
- **Validación en Tiempo Real**: Verificación inmediata de valores
- **Preview de Cambios**: Vista previa antes de aplicar cambios

### Características Avanzadas
- **Drag & Drop**: Importación de archivos de configuración
- **Búsqueda Global**: Búsqueda across todas las configuraciones
- **Historial de Cambios**: Log de todas las modificaciones
- **Roles y Permisos**: Control de acceso por usuario

## ⚙️ Configuración

### Variables de Entorno

```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/traffic_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key-here
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### Archivos de Configuración

```yaml
# config/system.yaml
system_name: "Traffic Violation Detection System"
version: "1.0.0"
environment: "production"
database_url: "postgresql://..."
redis_url: "redis://..."
log_level: "INFO"
metrics_enabled: true
```

```yaml
# config/cameras/CAM001.yaml
camera_id: "CAM001"
name: "Av. Javier Prado - San Isidro"
rtsp_url: "rtsp://admin:password@192.168.1.100:554/stream1"
location:
  lat: -12.0864
  lon: -77.0365
active: true
speed_limit: 60
detection_zones:
  - name: "lane1"
    polygon: [[100, 200], [500, 200], [500, 400], [100, 400]]
```

## 📚 Ejemplos

### Uso Programático

```python
from config_manager import config_manager, CameraConfig

# Cargar configuraciones
await config_manager.load_configurations()

# Obtener configuración de cámara
camera_config = config_manager.get_camera_config("CAM001")
if camera_config:
    print(f"Speed limit: {camera_config.speed_limit}")

# Crear nueva cámara
new_camera = CameraConfig(
    camera_id="CAM003",
    name="Nueva Cámara",
    rtsp_url="rtsp://192.168.1.103:554/stream1",
    location={"lat": -12.100, "lon": -77.050},
    speed_limit=40
)

# Guardar configuración
config_manager.camera_configs["CAM003"] = new_camera
await config_manager.save_camera_config("CAM003", new_camera)
```

### API con cURL

```bash
# Obtener todas las cámaras
curl -H "Authorization: Bearer <token>" \
     http://localhost:8080/config/cameras

# Crear nueva cámara
curl -X POST \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "camera_id": "CAM004",
       "name": "Test Camera",
       "rtsp_url": "rtsp://test:password@192.168.1.104:554/stream1",
       "location": {"lat": -12.050, "lon": -77.030},
       "speed_limit": 50
     }' \
     http://localhost:8080/config/cameras/CAM004

# Exportar configuración
curl -H "Authorization: Bearer <token>" \
     "http://localhost:8080/config/export?format=yaml" \
     > backup.yaml
```

### WebSocket para Notificaciones

```javascript
// Frontend JavaScript
const ws = new WebSocket('ws://localhost:8080/ws/config-updates')

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  if (data.type === 'config_change') {
    console.log('Configuration changed:', data.event, data.data)
    // Actualizar UI según el cambio
  }
}
```

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Error de Conexión a Base de Datos
```bash
# Verificar conexión
python -c "
from config_manager import config_manager
import asyncio
asyncio.run(config_manager.load_configurations())
"
```

#### 2. Configuraciones No Se Cargan
```bash
# Verificar permisos de archivos
ls -la config/
chmod -R 644 config/*.yaml

# Validar formato YAML
python -c "import yaml; yaml.safe_load(open('config/system.yaml'))"
```

#### 3. API No Responde
```bash
# Verificar servicio
curl http://localhost:8080/health

# Ver logs
tail -f logs/config-api.log
```

#### 4. WebSocket No Conecta
```bash
# Verificar puertos
netstat -an | grep 8080

# Verificar firewall
sudo ufw status
```

### Logs y Debugging

```bash
# Habilitar debug logging
export LOG_LEVEL=DEBUG

# Ver logs en tiempo real
tail -f /var/log/traffic-system.log

# Logs estructurados
grep "ERROR" /var/log/traffic-system.log | jq .
```

### Performance Tuning

```yaml
# config/system.yaml - Optimizaciones
database_pool_size: 20
database_max_overflow: 30
cache_ttl_default: 7200
cache_max_memory: "1gb"
metrics_enabled: true
```

## 📞 Soporte

### Documentación Adicional
- [API Reference](api-docs.md)
- [CLI Reference](cli-docs.md)
- [Web Interface Guide](web-guide.md)
- [Development Guide](dev-guide.md)

### Contacto
- **Email**: support@traffic-system.com
- **Slack**: #config-management
- **GitHub**: [Issues](https://github.com/org/repo/issues)

---

**Nota**: Este sistema es parte del Traffic Violation Detection System v1.0.0
"""

# Crear requirements.txt
requirements_content = """# Config Management System Requirements

# Core dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Configuration formats
pyyaml==6.0.1
toml==0.10.2
configparser==5.3.0

# Database and Storage
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
alembic==1.13.1

# HTTP and WebSocket
httpx==0.25.2
websockets==12.0
aiofiles==23.2.1

# CLI
click==8.1.7
rich==13.7.0
typer==0.9.0

# Authentication and Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Utilities
python-dotenv==1.0.0
structlog==23.2.0
colorama==0.4.6

# Development and Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.11.0
isort==5.12.0
flake8==6.1.0
mypy==1.7.1

# Optional: Monitoring and Metrics
prometheus-client==0.19.0
opentelemetry-api==1.21.0
"""

# Crear archivos de documentación
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)

with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write(requirements_content)

print("✅ Documentación y requirements creados exitosamente")