# Arquitectura del Sistema - Visión General

## Introducción

El Sistema de Detección de Infracciones de Tráfico está diseñado como una arquitectura de microservicios distribuida que permite escalabilidad, mantenibilidad y alta disponibilidad. El sistema combina tecnologías modernas de machine learning, procesamiento en tiempo real y interfaces de usuario intuitivas.

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
  - Autenticación y autorización
  - Gestión de usuarios y permisos
  - CRUD de entidades principales
  - Orquestación de workflows
  - Generación de reportes

**Arquitectura Interna:**
```
Backend API (Django)
├── Authentication/        # Gestión de usuarios y permisos
├── Vehicles/             # Gestión de vehículos
├── Infractions/          # Gestión de infracciones
├── Devices/              # Gestión de dispositivos
├── Reports/              # Generación de reportes
└── Config/               # Configuración del sistema
```

#### 2. ML Service (FastAPI)
- **Propósito**: Servicios de machine learning e IA
- **Tecnologías**: FastAPI, PyTorch, OpenCV, YOLO
- **Responsabilidades**:
  - Detección de placas vehiculares
  - Clasificación de vehículos
  - Detección de infracciones
  - Análisis de video en tiempo real
  - Calibración de cámaras

**Pipeline de ML:**
```
Input (Image/Video) → Preprocessing → Model Inference → Postprocessing → Output
                         ↓               ↓               ↓
                    Normalization   License Plate    Filtering &
                    Augmentation    Detection        Validation
                    Resizing        Vehicle Class.
                                   Infraction Det.
```

#### 3. Config Service (FastAPI)
- **Propósito**: Gestión centralizada de configuración
- **Tecnologías**: FastAPI, WebSocket, File Watchers
- **Responsabilidades**:
  - Almacenamiento de configuraciones
  - Distribución de cambios en tiempo real
  - Validación de configuraciones
  - Versionado y rollback
  - API REST y WebSocket

### Data Layer

#### 1. PostgreSQL (Base de Datos Principal)
- **Propósito**: Almacenamiento persistente de datos estructurados
- **Esquema Principal**:
  - Usuarios y permisos
  - Vehículos y propietarios
  - Infracciones y evidencias
  - Configuraciones y logs
  - Dispositivos y ubicaciones

#### 2. Redis (Cache y Sesiones)
- **Propósito**: Cache de alta velocidad y almacenamiento de sesiones
- **Uso**:
  - Cache de queries frecuentes
  - Sesiones de usuario
  - Rate limiting
  - Resultados temporales de ML

#### 3. MinIO (Almacenamiento de Objetos)
- **Propósito**: Almacenamiento de archivos multimedia
- **Contenido**:
  - Imágenes de evidencia
  - Videos de infracciones
  - Modelos de ML entrenados
  - Reportes generados
  - Backups

#### 4. RabbitMQ (Message Broker)
- **Propósito**: Comunicación asíncrona entre servicios
- **Colas Principales**:
  - `infraction.detection`: Nuevas detecciones
  - `notification.email`: Notificaciones por email
  - `report.generation`: Generación de reportes
  - `config.updates`: Actualizaciones de configuración

## Patrones de Comunicación

### 1. Síncrono (HTTP/REST)
```
Frontend → Load Balancer → Backend API → Database
                        → ML Service  → Model
                        → Config Service → Config Store
```

### 2. Asíncrono (Message Queue)
```
Backend API → RabbitMQ → Celery Workers → External Services
ML Service  → RabbitMQ → Notification Service
```

### 3. Tiempo Real (WebSocket)
```
Frontend ←─ WebSocket ─→ Backend API
Config UI ←─ WebSocket ─→ Config Service
```

### 4. Event Streaming
```
Detection Event → Event Bus → Multiple Subscribers
                              ├── Notification Service
                              ├── Analytics Service
                              └── Audit Service
```

## Seguridad

### 1. Autenticación y Autorización
- **JWT Tokens**: Para autenticación de APIs
- **RBAC**: Control de acceso basado en roles
- **OAuth 2.0**: Para integraciones externas
- **API Keys**: Para servicios externos

### 2. Comunicación Segura
- **TLS/SSL**: Encriptación en tránsito
- **mTLS**: Autenticación mutua entre servicios
- **API Gateway**: Punto único de entrada seguro
- **Network Policies**: Aislamiento de red en Kubernetes

### 3. Datos
- **Encriptación en reposo**: Base de datos y archivos
- **Secrets Management**: Kubernetes Secrets/Vault
- **Data Masking**: Enmascaramiento de datos sensibles
- **Backup Encryption**: Backups encriptados

## Escalabilidad

### 1. Horizontal Scaling
```
Backend API: 2-20 instancias (según carga)
ML Service: 1-10 instancias (CPU/GPU intensivo)
Config Service: 2-5 instancias (alta disponibilidad)
```

### 2. Vertical Scaling
```
Database: Escalamiento de recursos según datos
Cache: Incremento de memoria según uso
Storage: Expansión según crecimiento de archivos
```

### 3. Auto-scaling
```yaml
HPA (Horizontal Pod Autoscaler):
- CPU: 70% threshold
- Memory: 80% threshold
- Custom metrics: Requests/second
```

## Observabilidad

### 1. Métricas (Prometheus)
- **Sistema**: CPU, memoria, disco, red
- **Aplicación**: Requests/sec, latencia, errores
- **Negocio**: Infracciones/día, precisión ML

### 2. Logs (Fluentd + ELK)
- **Structured Logging**: JSON format
- **Log Levels**: DEBUG, INFO, WARN, ERROR
- **Correlation IDs**: Trazabilidad de requests

### 3. Trazas (Jaeger)
- **Distributed Tracing**: Seguimiento entre servicios
- **Performance Analysis**: Identificación de cuellos de botella
- **Error Analysis**: Debugging de errores distribuidos

### 4. Alertas (AlertManager)
- **SLA Monitoring**: Disponibilidad y performance
- **Error Rate**: Tasa de errores por servicio
- **Resource Usage**: Uso de recursos críticos

## Disaster Recovery

### 1. Backup Strategy
- **Database**: Backup diario con retención de 30 días
- **Files**: Replicación a múltiples zonas
- **Configuration**: Versionado en Git
- **Code**: Repositorios distribuidos

### 2. High Availability
- **Multi-AZ Deployment**: Distribución en múltiples zonas
- **Load Balancing**: Distribución de carga
- **Circuit Breakers**: Prevención de cascading failures
- **Graceful Degradation**: Funcionamiento parcial en fallos

### 3. Recovery Procedures
- **RTO (Recovery Time Objective)**: 1 hora
- **RPO (Recovery Point Objective)**: 15 minutos
- **Automated Failover**: Para servicios críticos
- **Manual Procedures**: Para casos complejos

## Evolución de la Arquitectura

### Próximas Mejoras
1. **Service Mesh**: Istio para comunicación entre servicios
2. **Event Sourcing**: Para auditabilía completa
3. **CQRS**: Separación de lectura y escritura
4. **GraphQL**: API más flexible para frontends
5. **Edge Computing**: Procesamiento en dispositivos IoT

### Consideraciones de Migración
- **Backward Compatibility**: Mantenimiento de APIs v1
- **Database Migration**: Estrategias de migración gradual
- **Zero-Downtime Deployment**: Blue-green deployments
- **Feature Flags**: Control granular de funcionalidades

Esta arquitectura proporciona una base sólida para el crecimiento y evolución del sistema, manteniendo la flexibilidad necesaria para adaptarse a nuevos requisitos y tecnologías.