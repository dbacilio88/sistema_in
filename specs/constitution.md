# Constitution - Sistema Inteligente de Detección de Infracciones de Tránsito

## 1. Visión y Propósito

### 1.1 Misión
Desarrollar un sistema inteligente automatizado de monitoreo y detección de infracciones de tránsito que combine tecnologías de visión artificial, IoT y aprendizaje automático para mejorar la seguridad vial, reducir accidentes y optimizar la aplicación de normativas de tránsito en vías públicas urbanas.

### 1.2 Objetivos Estratégicos
- **Detección Automática**: Identificar con precisión ≥90% infracciones de tránsito (exceso de velocidad, invasión de carril, paso con luz roja) en condiciones diurnas y ≥80% en condiciones nocturnas.
- **Procesamiento en Tiempo Real**: Procesar streams de video con latencia <250 ms por frame en dispositivos edge con GPU.
- **Trazabilidad Completa**: Registrar evidencia multimedia (video, imágenes, metadatos) de cada infracción para procesos legales.
- **Escalabilidad**: Soportar despliegue de 50+ cámaras IoT distribuidas en múltiples puntos estratégicos.
- **Inteligencia Predictiva**: Analizar patrones de conducción y predecir riesgos de accidentes o reincidencia con modelos ML.
- **Interoperabilidad**: Integración con API SUNARP para enriquecimiento automático de datos de vehículos y propietarios.

### 1.3 Valores Fundamentales
- **Precisión**: Minimizar falsos positivos (<5%) y falsos negativos (<10%).
- **Transparencia**: Registrar y auditar todas las decisiones del sistema con trazabilidad completa.
- **Privacidad**: Cumplir con normativas de protección de datos personales (Ley N° 29733 Perú).
- **Fiabilidad**: Disponibilidad del sistema ≥99.5% (downtime máximo ~3.6 horas/mes).
- **Escalabilidad**: Arquitectura cloud-native preparada para crecimiento horizontal.

## 2. Alcance del Sistema

### 2.1 Funcionalidades Principales

#### 2.1.1 Detección de Infracciones
- **Exceso de Velocidad**: Cálculo de velocidad mediante tracking temporal de vehículos, comparación con límite de zona (configurable 30-100 km/h).
- **Invasión de Carril**: Detección de cruces indebidos de líneas de carril mediante análisis de trayectorias y segmentación de vía.
- **Paso con Luz Roja**: Identificación de vehículos cruzando intersecciones semaforizadas durante fase roja mediante OCR de estado de semáforo o integración con controladores de semáforos.

#### 2.1.2 Reconocimiento Automático de Placas
- OCR robusto con PaddleOCR/EasyOCR optimizado para placas peruanas (formato ABC-123, ABC-1234).
- Preprocesamiento: corrección de perspectiva, normalización de iluminación, eliminación de ruido.
- Validación de formato y verificación de integridad mediante checksum.

#### 2.1.3 Enriquecimiento de Datos
- Consulta automática a API SUNARP para obtener:
  - Datos del propietario (nombre, DNI, dirección).
  - Datos del vehículo (marca, modelo, año, color, estado).
- Cache de consultas para reducir latencia y costos de API.
- Manejo de errores: placas no encontradas, vehículos con deuda, registros múltiples.

#### 2.1.4 Analítica Predictiva
- Modelo de riesgo de reincidencia basado en:
  - Historial de infracciones (cantidad, tipo, recencia).
  - Patrones temporales (hora del día, día de semana).
  - Condiciones ambientales (clima, visibilidad).
  - Características del conductor (edad, experiencia).
- Predicción de probabilidad de accidente en zonas críticas.
- Scoring de conductores de alto riesgo para priorización de intervenciones.

#### 2.1.5 Gestión Administrativa (Django)
- Panel de administración con roles: Administrador, Supervisor, Operador, Auditor.
- CRUD de usuarios, dispositivos (cámaras), zonas, límites de velocidad.
- Visualización de infracciones: filtros por fecha, tipo, ubicación, estado.
- Generación de reportes: estadísticas diarias/mensuales, exportación PDF/Excel.
- Gestión de evidencia multimedia: visualización de videos e imágenes.
- Control de dispositivos: configuración de cámaras, calibración, estado de conexión.

#### 2.1.6 Microservicio de Inferencia (FastAPI)
- API REST para recepción de streams RTSP/ONVIF desde cámaras IoT.
- Pipeline de procesamiento:
  1. Decodificación de frames (OpenCV, FFmpeg).
  2. Detección de objetos (YOLOv8).
  3. Tracking de vehículos (DeepSort/ByteTrack).
  4. Detección de placas y OCR.
  5. Clasificación de infracciones.
  6. Generación de eventos y almacenamiento.
- Endpoints para consulta de eventos, estadísticas en tiempo real y health checks.

### 2.2 Infraestructura IoT

#### 2.2.1 Especificaciones de Cámara EZVIZ H6C Pro 2K
- **Resolución**: 2K (2560×1440 @ 30 fps).
- **Campo de Visión**: 340° horizontal (PTZ), 75° vertical.
- **Visión Nocturna**: IR hasta 10 metros, modo color con luz blanca.
- **Protocolos**: ONVIF Profile S, RTSP, HTTP.
- **Conectividad**: Wi-Fi 802.11b/g/n (2.4 GHz), Ethernet RJ45.
- **Detección**: Movimiento, humanos, vehículos (IA embebida básica).
- **Almacenamiento Local**: MicroSD hasta 512 GB (backup).

#### 2.2.2 Configuración de Conexión RTSP
```
URL RTSP Principal: rtsp://{username}:{password}@{ip}:{port}/h264/ch1/main/av_stream
URL RTSP Substream: rtsp://{username}:{password}@{ip}:{port}/h264/ch1/sub/av_stream

Ejemplo:
rtsp://admin:Abc123456@192.168.1.100:554/h264/ch1/main/av_stream
```

#### 2.2.3 Protocolo ONVIF
- **Discovery**: WS-Discovery para detección automática de cámaras en red local.
- **PTZ Control**: Comandos ONVIF para ajuste remoto de pan/tilt/zoom.
- **Configuración**: Ajuste de bitrate, resolución, FPS mediante SOAP API.

### 2.3 Stack Tecnológico

#### 2.3.1 Backend
- **Django 5.0**: Framework principal para backend administrativo, ORM, autenticación, panel admin.
- **FastAPI 0.110**: Microservicio de inferencia, endpoints asíncronos, WebSockets para streaming.
- **Celery + Redis**: Procesamiento asíncrono de tareas (consultas SUNARP, entrenamiento de modelos).
- **PostgreSQL 16**: Base de datos relacional principal con extensiones PostGIS (geolocalización), TimescaleDB (series temporales).

#### 2.3.2 Visión Artificial & ML
- **YOLOv8** (Ultralytics): Detección de vehículos, placas, semáforos.
- **DeepSort/ByteTrack**: Tracking multi-objeto para cálculo de velocidad y trayectorias.
- **PaddleOCR/EasyOCR**: Reconocimiento óptico de caracteres para placas.
- **XGBoost/LightGBM**: Modelos predictivos de riesgo de reincidencia.
- **MLflow**: Gestión de experimentos, versionamiento de modelos, registro de métricas.
- **ONNX Runtime**: Inferencia optimizada en producción.

#### 2.3.3 Infraestructura
- **Docker 24+**: Contenedorización de servicios.
- **Kubernetes (K8s)**: Orquestación, escalado automático (HPA), balanceo de carga.
- **Nginx**: Reverse proxy, balanceo de carga HTTP/RTSP.
- **MinIO/S3**: Almacenamiento de objetos para videos e imágenes.

#### 2.3.4 Monitoreo & Observabilidad
- **Prometheus**: Métricas de rendimiento (latencia, throughput, uso de GPU/CPU).
- **Grafana**: Dashboards de monitoreo en tiempo real.
- **ELK Stack** (Elasticsearch, Logstash, Kibana): Logging centralizado.
- **Jaeger**: Tracing distribuido para debugging.
- **Sentry**: Monitoreo de errores y excepciones.

#### 2.3.5 Seguridad
- **TLS/SSL**: Certificados Let's Encrypt para comunicación cifrada.
- **JWT**: Autenticación basada en tokens para APIs.
- **OAuth2/OIDC**: Integración con proveedores de identidad externos.
- **RBAC**: Control de acceso basado en roles (Django permissions).
- **Secrets Management**: HashiCorp Vault o AWS Secrets Manager.

## 3. Principios Arquitectónicos

### 3.1 Diseño
- **Microservicios**: Separación de responsabilidades (admin, inferencia, ML, storage).
- **API First**: Todas las funcionalidades expuestas mediante APIs REST/GraphQL.
- **Event-Driven**: Comunicación asíncrona mediante RabbitMQ/Kafka para eventos de infracciones.
- **Stateless**: Servicios sin estado para facilitar escalado horizontal.
- **Idempotencia**: Operaciones repetibles sin efectos secundarios.

### 3.2 Datos
- **Single Source of Truth**: PostgreSQL como base de datos principal.
- **Data Lake**: MinIO para almacenamiento de raw data (videos, logs).
- **Cache**: Redis para datos de alta frecuencia (sesiones, consultas SUNARP).
- **Time-Series**: TimescaleDB para métricas de rendimiento y eventos temporales.

### 3.3 Calidad
- **Testing**: Cobertura mínima 80% (unit tests, integration tests, e2e tests).
- **CI/CD**: GitHub Actions con pipelines automatizados (lint, test, build, deploy).
- **Code Quality**: Pre-commit hooks, SonarQube para análisis estático.
- **Documentation**: Swagger/OpenAPI para APIs, docstrings en código Python.

### 3.4 Performance
- **Latencia**: <250 ms para inferencia por frame.
- **Throughput**: Procesamiento de 30 fps por cámara.
- **Concurrencia**: Soporte para 50+ streams simultáneos.
- **GPU Utilization**: >70% para optimizar costos de hardware.

### 3.5 Resiliencia
- **High Availability**: Réplicas múltiples de servicios críticos (N+1).
- **Fault Tolerance**: Circuit breakers, retry logic con backoff exponencial.
- **Graceful Degradation**: Funcionalidad parcial en caso de fallo de componentes no críticos.
- **Backup**: Backups automáticos diarios de PostgreSQL, replicación continua de videos.

## 4. Restricciones y Limitaciones

### 4.1 Técnicas
- Procesamiento de video limitado por capacidad de GPU (NVIDIA RTX 3060 Ti o superior recomendado).
- Precisión de OCR afectada por condiciones climáticas adversas (lluvia intensa, niebla).
- Latencia de red puede afectar tiempo de respuesta en cámaras remotas.

### 4.2 Legales y Regulatorias
- Cumplimiento de Ley de Protección de Datos Personales (Ley N° 29733 Perú).
- Retención de evidencia multimedia por 5 años según normativa de tránsito.
- Anonimización de datos en reportes públicos y estadísticas.

### 4.3 Operacionales
- Mantenimiento de cámaras cada 3 meses (limpieza de lentes, calibración).
- Reentrenamiento de modelos ML cada 6 meses con datos actualizados.
- Actualizaciones de firmware de cámaras gestionadas por equipo de soporte.

### 4.4 Presupuestarias
- Límite de consultas a API SUNARP: 10,000 consultas/mes (plan estándar).
- Costos de almacenamiento: retención de video 30 días en hot storage, migración a cold storage después.

## 5. Stakeholders y Roles

### 5.1 Equipo de Desarrollo
- **Tech Lead**: Arquitectura, revisión de código, decisiones técnicas.
- **Backend Engineers (2)**: Desarrollo Django/FastAPI, integraciones.
- **ML Engineers (2)**: Entrenamiento de modelos, optimización de inferencia.
- **DevOps Engineer**: Infraestructura, CI/CD, monitoreo.
- **QA Engineer**: Testing, automatización, validación de precisión.

### 5.2 Stakeholders Externos
- **Municipalidad**: Cliente principal, define políticas de tránsito y zonas de monitoreo.
- **Policía de Tránsito**: Usuarios finales del sistema, validan infracciones.
- **SUNARP**: Proveedor de API para datos de vehículos.
- **Conductores**: Sujetos monitoreados, receptores de notificaciones.

## 6. Criterios de Éxito

### 6.1 Métricas Técnicas
- **Precisión**: ≥90% detección diurna, ≥80% detección nocturna.
- **Recall**: ≥85% (no perder infracciones reales).
- **False Positive Rate**: ≤5%.
- **Latencia**: <250 ms por frame.
- **Uptime**: ≥99.5%.

### 6.2 Métricas de Negocio
- Reducción de 30% en reincidencia de infracciones en zonas monitoreadas (6 meses).
- Procesamiento de 500+ infracciones diarias con precisión validada.
- ROI positivo en 18 meses (reducción de accidentes vs inversión).

### 6.3 Métricas de Usuario
- Tiempo de resolución de incidente: <5 minutos desde detección hasta registro.
- Satisfacción de operadores: ≥4/5 en usabilidad del panel admin.
- Tiempo de consulta de evidencia: <10 segundos para cargar video de infracción.

## 7. Gobierno del Proyecto

### 7.1 Metodología
- **Scrum**: Sprints de 2 semanas, daily standups, sprint reviews y retrospectivas.
- **GitFlow**: Branches main, develop, feature/*, hotfix/*.
- **Definition of Done**: Tests passing, code reviewed, documentación actualizada, deployado en staging.

### 7.2 Comunicación
- **Daily Standup**: 15 minutos, 9:00 AM, sincrónico.
- **Sprint Planning**: 2 horas, inicio de sprint, presencial/remoto.
- **Sprint Review**: 1 hora, fin de sprint, demo al cliente.
- **Retrospectiva**: 1 hora, fin de sprint, mejora continua.

### 7.3 Documentación
- **Technical Docs**: Confluence/Notion, arquitectura, ADRs (Architecture Decision Records).
- **User Docs**: Manual de usuario, guías de operación.
- **API Docs**: Swagger UI autogenerado, Postman collections.

### 7.4 Control de Cambios
- Todo cambio de alcance debe ser aprobado por Tech Lead y Product Owner.
- Registro de cambios en CHANGELOG.md siguiendo Semantic Versioning.
- RFCs (Request for Comments) para decisiones arquitectónicas mayores.

---

**Versión**: 1.0  
**Fecha**: 2025-11-01  
**Autores**: Equipo de Arquitectura - Sistema de Detección de Infracciones  
**Estado**: Aprobado
