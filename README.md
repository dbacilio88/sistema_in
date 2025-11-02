# Sistema Inteligente de Detección de Infracciones de Tránsito 🚦🚗

Sistema automatizado de monitoreo y detección de infracciones de tránsito que combina tecnologías de visión artificial, IoT y aprendizaje automático para mejorar la seguridad vial.

## 🎯 Características Principales

- **Detección Automática de Infracciones**
  - 🏎️ Exceso de velocidad (precisión ≥90% diurna, ≥80% nocturna)
  - 🚧 Invasión de carril
  - 🚦 Paso con luz roja

- **Reconocimiento de Placas (OCR)**
  - Detección automática con PaddleOCR/EasyOCR
  - Precisión ≥85% en placas peruanas
  - Validación de formato ABC-123 / ABC-1234

- **Integración SUNARP**
  - Consulta automática de datos de vehículos
  - Cache inteligente con Redis
  - Enriquecimiento de información del propietario

- **Analítica Predictiva con ML**
  - Predicción de riesgo de reincidencia (XGBoost)
  - Análisis de patrones de conducción
  - Scoring de conductores de alto riesgo

## 🏗️ Arquitectura

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Cámaras    │────▶│   FastAPI    │────▶│  PostgreSQL │
│  EZVIZ H6C  │     │  (Inference) │     │  + PostGIS  │
│  2K + PTZ   │     │   + YOLOv8   │     │+ TimescaleDB│
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                    ┌──────▼────────┐
                    │    Django     │
                    │    Admin +    │
                    │  REST API     │
                    └───────────────┘
```

### Stack Tecnológico

**Backend:**
- Django 5.0 - Framework administrativo
- FastAPI 0.110 - Microservicio de inferencia
- PostgreSQL 16 - Base de datos principal
- Redis 7 - Cache y sesiones
- RabbitMQ 3.12 - Message broker

**Machine Learning & Visión Artificial:**
- YOLOv8 (Ultralytics) - Detección de vehículos
- DeepSort/ByteTrack - Tracking multi-objeto
- PaddleOCR/EasyOCR - OCR de placas
- XGBoost - Modelos predictivos
- MLflow - Gestión de modelos

**Infraestructura:**
- Docker & Docker Compose
- Kubernetes - Orquestación
- MinIO/S3 - Almacenamiento de objetos
- Prometheus + Grafana - Monitoreo
- ELK Stack - Logging centralizado

**IoT:**
- EZVIZ H6C Pro 2K - Cámara IP 2K con PTZ
- RTSP/ONVIF - Protocolos de streaming
- Edge processing (opcional con NVIDIA Jetson)

## 📋 Requisitos Previos

- Python 3.11+
- Docker 24+ y Docker Compose
- PostgreSQL 16 (o usar Docker)
- GPU NVIDIA con CUDA 11.8+ (recomendado RTX 3060 Ti o superior)
- 16 GB RAM mínimo (32 GB recomendado)

## 🚀 Instalación y Setup

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/sistema-infracciones-transito.git
cd sistema-infracciones-transito
```

### 2. Configurar Variables de Entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 3. Levantar Servicios con Docker Compose

```bash
docker-compose up -d
```

### 4. Inicializar Base de Datos

```bash
# Django migrations
docker-compose exec django python manage.py migrate

# Seed data
docker-compose exec django python manage.py loaddata seed_data.json
```

### 5. Acceder a las Aplicaciones

- **Django Admin:** http://localhost:8000/admin
  - Usuario: `admin`
  - Contraseña: `Admin123!`

- **FastAPI Docs:** http://localhost:8001/docs
- **RabbitMQ Management:** http://localhost:15672
- **MinIO Console:** http://localhost:9001

## 🛠️ Desarrollo Local

### Setup de Entorno Virtual

```bash
# Backend Django
cd backend-django
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# Inference Service
cd ../inference-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Pre-commit Hooks

Instalamos hooks para mantener calidad de código:

```bash
pip install pre-commit
pre-commit install
```

Los hooks ejecutarán automáticamente:
- **Black** - Formateo de código
- **Flake8** - Linting
- **isort** - Ordenamiento de imports
- **mypy** - Type checking

### Ejecutar Tests

```bash
# Django
cd backend-django
pytest --cov=. --cov-report=html

# FastAPI
cd inference-service
pytest --cov=app --cov-report=html
```

## 📁 Estructura del Proyecto

```
sistema-infracciones-transito/
├── backend-django/          # Servicio Django Admin
│   ├── authentication/      # App de autenticación
│   ├── devices/            # App de dispositivos
│   ├── infractions/        # App de infracciones
│   ├── vehicles/           # App de vehículos
│   └── manage.py
├── inference-service/       # Servicio FastAPI de inferencia
│   ├── app/
│   │   ├── api/            # Endpoints REST
│   │   ├── core/           # Config y utilidades
│   │   ├── models/         # Modelos de ML
│   │   ├── services/       # Lógica de negocio
│   │   └── main.py
│   └── tests/
├── ml-service/             # Servicio de ML predictivo
│   ├── training/           # Scripts de entrenamiento
│   ├── models/             # Modelos entrenados
│   └── mlflow/             # Tracking de experimentos
├── infrastructure/         # Configuración de infra
│   ├── docker/             # Dockerfiles
│   ├── kubernetes/         # Manifiestos K8s
│   └── terraform/          # IaC (opcional)
├── specs/                  # Especificaciones técnicas
│   ├── constitution.md
│   ├── spec.md
│   ├── plan.md
│   ├── tasks.md
│   └── data-model.md
├── docs/                   # Documentación adicional
├── tests/                  # Tests de integración E2E
├── docker-compose.yml
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
└── README.md
```

## 🧪 Testing

El proyecto mantiene una cobertura mínima de **80%** en tests.

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov --cov-report=html

# Tests específicos
pytest tests/test_detection.py -v
```

## 📊 Monitoreo y Observabilidad

### Prometheus Metrics

Métricas expuestas en `/metrics`:
- `infractions_detected_total` - Total de infracciones detectadas
- `inference_latency_seconds` - Latencia de inferencia por stage
- `gpu_utilization_percent` - Utilización de GPU
- `frames_processed_total` - Frames procesados por cámara

### Grafana Dashboards

Acceder a http://localhost:3000 (credenciales en `.env`)

Dashboards disponibles:
- **Traffic Inference System** - Métricas de inferencia
- **Database Performance** - PostgreSQL metrics
- **Infrastructure Overview** - CPU, memoria, network

## 🎯 Roadmap

### ✅ Fase 1: PoC (Sprint 1-3) - Completado
- [x] Infraestructura base
- [x] Detección de vehículos con YOLOv8
- [x] Cálculo de velocidad
- [x] Detección de exceso de velocidad

### 🚧 Fase 2: Sistema Completo (Sprint 4-7) - En Progreso
- [x] OCR de placas
- [ ] Detección de invasión de carril
- [ ] Detección de paso con luz roja
- [ ] Dashboard de validación

### 📅 Fase 3: Integración (Sprint 8-10) - Planeado
- [ ] Integración SUNARP
- [ ] ML predictivo
- [ ] Optimización de rendimiento

### 📅 Fase 4: Producción (Sprint 11-12) - Planeado
- [ ] Despliegue en Kubernetes
- [ ] CI/CD completo
- [ ] Capacitación de usuarios

## 📈 Métricas de Éxito

- **Precisión de Detección:** ≥90% (diurna), ≥80% (nocturna)
- **Latencia:** <250 ms por frame
- **Throughput:** 30 fps por cámara
- **False Positive Rate:** ≤5%
- **Uptime:** ≥99.5%

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Convenciones de Código

- Seguir PEP 8 para Python
- Usar type hints en todas las funciones
- Documentar con docstrings (Google style)
- Tests para toda nueva funcionalidad

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👥 Equipo

- **Tech Lead:** [Nombre]
- **Backend Engineers:** [Nombres]
- **ML Engineers:** [Nombres]
- **DevOps Engineer:** [Nombre]
- **QA Engineer:** [Nombre]

## 📞 Soporte

Para reportar bugs o solicitar features, crear un issue en GitHub:
https://github.com/tu-usuario/sistema-infracciones-transito/issues

## 📚 Documentación Adicional

- [Especificación Técnica Completa](specs/spec.md)
- [Plan de Desarrollo](specs/plan.md)
- [Modelo de Datos](specs/data-model.md)
- [Backlog de Tareas](specs/tasks.md)
- [Constitution del Proyecto](specs/constitution.md)

---

**Versión:** 1.0.0  
**Última Actualización:** 2025-11-01  
**Estado:** 🚧 En Desarrollo Activo
