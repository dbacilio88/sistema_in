# Plan de Desarrollo - Sistema de Detección de Infracciones de Tránsito

## 1. Roadmap General

### Fase 1: Fundamentos y PoC (Sprint 1-3) - 6 semanas
**Objetivo**: Validar viabilidad técnica con detección básica de un tipo de infracción

### Fase 2: Sistema Completo (Sprint 4-7) - 8 semanas
**Objetivo**: Implementar detección de los 3 tipos de infracciones con precisión objetivo

### Fase 3: Integración y Analítica (Sprint 8-10) - 6 semanas
**Objetivo**: Integrar SUNARP, implementar ML predictivo, optimizar rendimiento

### Fase 4: Producción y Escalado (Sprint 11-12) - 4 semanas
**Objetivo**: Despliegue en producción, monitoreo, documentación, capacitación

**Duración Total**: 24 semanas (6 meses)

---

## 2. Planificación Detallada por Sprints

### **SPRINT 1: Infraestructura Base y Setup** (2 semanas)

#### Objetivos
- Configurar entorno de desarrollo y repositorio
- Implementar estructura de microservicios básica
- Conectar cámara IoT y obtener stream RTSP
- Setup de base de datos PostgreSQL

#### Historias de Usuario
1. **Setup del Repositorio (3 puntos)**
   - Inicializar repo en GitHub con estructura de monorepo
   - Configurar .gitignore, README.md, CONTRIBUTING.md
   - Setup de pre-commit hooks (black, flake8, mypy)
   - Configurar GitHub Actions para CI básico

2. **Infraestructura Docker (5 puntos)**
   - Crear docker-compose.yml con servicios: postgres, redis, rabbitmq, minio
   - Configurar networks y volumes
   - Crear .env.example con variables de entorno
   - Documentar proceso de setup local

3. **Django Admin Service - Base (8 puntos)**
   - Crear proyecto Django 5.0
   - Configurar Django REST Framework
   - Implementar modelo User con autenticación JWT
   - Crear endpoints /api/auth/login, /api/auth/logout
   - Tests unitarios de autenticación

4. **FastAPI Inference Service - Base (8 puntos)**
   - Crear proyecto FastAPI
   - Implementar endpoint /api/inference/health
   - Conectar a cámara via RTSP con OpenCV
   - Endpoint POST /api/inference/stream/start
   - Verificar recepción de frames

5. **PostgreSQL Setup (5 puntos)**
   - Crear esquema inicial de base de datos (users, devices, zones)
   - Configurar migraciones con Alembic (FastAPI) y Django migrations
   - Instalar extensiones: PostGIS, TimescaleDB, uuid-ossp
   - Script de seed data (usuarios, zona de prueba, cámara demo)

6. **Conexión EZVIZ H6C Pro 2K (5 puntos)**
   - Configurar cámara en red local
   - Obtener URL RTSP funcional
   - Verificar calidad de stream (2K @ 30fps)
   - Probar visión nocturna y detección de movimiento
   - Documentar configuración de cámara

#### Entregables
- Repositorio configurado con CI/CD básico
- Docker compose funcional con todos los servicios
- Django API con autenticación JWT
- FastAPI recibiendo stream RTSP de cámara
- Base de datos PostgreSQL con schema inicial
- Documentación de setup en README.md

#### Definition of Done
- [ ] Todos los servicios levantan con `docker-compose up`
- [ ] Tests de autenticación pasan (coverage ≥80%)
- [ ] Stream RTSP se visualiza correctamente
- [ ] Migraciones de DB aplicadas sin errores
- [ ] Documentación actualizada

---

### **SPRINT 2: Detección de Vehículos y Tracking** (2 semanas)

#### Objetivos
- Implementar detección de vehículos con YOLOv8
- Implementar tracking con DeepSort
- Almacenar frames procesados en MinIO

#### Historias de Usuario
7. **Integración YOLOv8 (8 puntos)**
   - Descargar y convertir modelo YOLOv8x a ONNX
   - Implementar clase VehicleDetector con ONNX Runtime
   - Optimizar inferencia con TensorRT (FP16)
   - Medir latencia y throughput (objetivo <100ms/frame)
   - Tests con imágenes de prueba

8. **Sistema de Tracking (8 puntos)**
   - Integrar DeepSort o ByteTrack
   - Implementar asignación de IDs únicos a vehículos
   - Mantener trayectorias de últimos 60 frames
   - Calcular vectores de velocidad
   - Visualizar bounding boxes y track IDs

9. **Almacenamiento de Evidencia (5 puntos)**
   - Configurar MinIO como storage de objetos
   - Implementar clase StorageClient
   - Subir snapshots a bucket `traffic-snapshots`
   - Generar URLs pre-firmadas (expiración 7 días)
   - Tests de upload/download

10. **Pipeline de Procesamiento (13 puntos)**
    - Implementar InferencePipeline con stages:
      1. Frame decoding
      2. Detection
      3. Tracking
      4. Storage
    - Procesamiento asíncrono con asyncio
    - Buffer de frames para suavizar procesamiento
    - Manejo de reconexión en caso de pérdida de stream
    - Logging detallado de cada stage

11. **Modelo de Datos - Devices y Events (5 puntos)**
    - Implementar tablas: devices, events
    - CRUD de devices en Django Admin
    - Endpoint GET /api/devices/
    - Inserción de eventos en TimescaleDB
    - Queries de agregación (eventos por hora)

#### Entregables
- YOLOv8 detectando vehículos en tiempo real
- DeepSort trackeando objetos con IDs persistentes
- Snapshots almacenándose en MinIO
- Pipeline completo procesando 30 fps
- Panel Django para ver cámaras registradas

#### Definition of Done
- [ ] Detección con precisión ≥85% en dataset de prueba
- [ ] Tracking mantiene IDs por ≥5 segundos
- [ ] Latencia de pipeline <150ms por frame
- [ ] Snapshots accesibles vía URL
- [ ] Tests de integración pasan

---

### **SPRINT 3: PoC - Detección de Exceso de Velocidad** (2 semanas)

#### Objetivos
- Implementar calibración de cámara
- Calcular velocidad de vehículos
- Detectar infracciones de exceso de velocidad
- Dashboard básico para visualizar infracciones

#### Historias de Usuario
12. **Calibración de Cámara (13 puntos)**
    - Implementar herramienta de calibración manual
    - Colocar marcadores de referencia en vía de prueba
    - Calcular matriz de homografía (píxeles → metros)
    - Almacenar calibración en tabla devices.calibration_matrix
    - Endpoint POST /api/devices/{id}/calibrate
    - Validar precisión con vehículos de velocidad conocida

13. **Cálculo de Velocidad (8 puntos)**
    - Implementar SpeedCalculator con homografía
    - Calcular distancia recorrida en ventana temporal (1 segundo)
    - Filtrar ruido con media móvil
    - Validar con velocímetro real (error <5%)
    - Tests unitarios con trayectorias simuladas

14. **Detección de Infracción de Velocidad (8 puntos)**
    - Implementar SpeedViolationDetector
    - Comparar velocidad calculada vs límite de zona
    - Generar evento de infracción al detectar exceso
    - Capturar snapshot del vehículo infractor
    - Publicar evento a RabbitMQ (cola: infractions.speed)

15. **Modelo de Datos - Infractions (5 puntos)**
    - Implementar tabla infractions
    - Consumer de RabbitMQ en Django
    - Persistir infracciones en PostgreSQL
    - Endpoint GET /api/infractions/
    - Filtros por tipo, fecha, cámara

16. **Dashboard de Infracciones (8 puntos)**
    - Pantalla de listado de infracciones en Django Admin
    - Visualización de snapshot y video
    - Filtros: fecha, tipo, estado, cámara
    - Acción: validar/rechazar infracción
    - Estadísticas básicas: total por día, promedio de velocidad

#### Entregables
- Cámara calibrada con precisión <5% error
- Sistema detectando exceso de velocidad automáticamente
- Infracciones almacenadas en PostgreSQL
- Dashboard mostrando infracciones en tiempo real

#### Definition of Done
- [ ] Velocidad calculada con error <5%
- [ ] Infracciones detectadas correctamente (no falsos positivos)
- [ ] Dashboard funcional y accesible
- [ ] Documentación de proceso de calibración
- [ ] Demo exitoso con vehículo real

---

### **SPRINT 4: OCR de Placas** (2 semanas)

#### Objetivos
- Detectar región de placa en vehículo
- Implementar OCR con PaddleOCR/EasyOCR
- Validar formato de placas peruanas

#### Historias de Usuario
17. **Detector de Placas (8 puntos)**
    - Entrenar/fine-tune YOLOv8 para detección de placas
    - Dataset: 1000+ imágenes de placas peruanas
    - Precisión objetivo: ≥90% mAP@0.5
    - Implementar PlateDetector
    - Detectar placa en crop de vehículo

18. **OCR de Placas (13 puntos)**
    - Integrar PaddleOCR (idioma inglés + español)
    - Preprocesamiento: corrección de perspectiva, contraste adaptativo
    - Implementar OCREngine con post-procesamiento
    - Validación de formato: ABC-123, ABC-1234
    - Manejo de placas borrosas (confianza <0.7 → rechazar)
    - Tests con dataset de 500 placas reales

19. **Integración en Pipeline (5 puntos)**
    - Añadir stage de detección de placas en InferencePipeline
    - Ejecutar OCR solo en vehículos infractores
    - Almacenar crop de placa junto con snapshot
    - Registrar confianza de OCR en evento

20. **Modelo de Datos - Vehicles (5 puntos)**
    - Implementar tabla vehicles
    - Relación: infractions.plate → vehicles.plate
    - Endpoint GET /api/vehicles/{plate}
    - CRUD de vehículos en Django Admin

#### Entregables
- Detector de placas con ≥90% precisión
- OCR reconociendo placas con ≥85% precisión
- Infracciones con placa identificada automáticamente

#### Definition of Done
- [ ] OCR con precisión ≥85% en dataset de prueba
- [ ] Formato de placa validado correctamente
- [ ] Crop de placa almacenado en MinIO
- [ ] Tests de OCR con casos edge (placas sucias, borrosas)

---

### **SPRINT 5: Detección de Invasión de Carril** (2 semanas)

#### Objetivos
- Segmentar líneas de carril
- Detectar cruces indebidos
- Integrar detección en pipeline

#### Historias de Usuario
21. **Segmentación de Carriles (13 puntos)**
    - Implementar detección de líneas con Hough Transform
    - Alternativamente: modelo de segmentación semántica (UNet)
    - Definir ROI (región de interés) en configuración de cámara
    - Almacenar geometría de carriles en devices.metadata
    - Visualizar líneas detectadas en dashboard

22. **Detección de Invasión (8 puntos)**
    - Implementar LaneInvasionDetector
    - Detectar cuando trayectoria de vehículo cruza línea
    - Ignorar cambios de carril legítimos (usar direccionales si es posible)
    - Generar evento de infracción
    - Tests con trayectorias simuladas

23. **Modelo de Datos - Zones (5 puntos)**
    - Añadir campo zones.lane_config (JSONB con geometría de carriles)
    - Endpoint POST /api/zones/{id}/configure-lanes
    - Herramienta de configuración visual (interfaz web)

#### Entregables
- Líneas de carril detectadas y visualizadas
- Sistema detectando invasiones de carril
- Configuración de carriles por zona

#### Definition of Done
- [ ] Carriles detectados con precisión
- [ ] Invasiones identificadas sin falsos positivos
- [ ] Herramienta de configuración funcional
- [ ] Tests de integración

---

### **SPRINT 6: Detección de Paso con Luz Roja** (2 semanas)

#### Objetivos
- Integrar con controladores de semáforos o detectar estado de semáforo
- Detectar vehículos cruzando en rojo
- Completar detección de los 3 tipos de infracciones

#### Historias de Usuario
24. **Detección de Estado de Semáforo (13 puntos)**
    - Opción A: Integración con controlador de semáforo (API)
    - Opción B: Detección visual de semáforo (clasificador CNN)
    - Entrenar clasificador: rojo, amarillo, verde (dataset sintético + real)
    - Implementar TrafficLightDetector
    - Precisión objetivo: ≥95%

25. **Detección de Paso en Rojo (8 puntos)**
    - Implementar RedLightViolationDetector
    - Definir línea de alto en configuración de zona
    - Detectar vehículos cruzando línea durante fase roja
    - Generar evento de infracción
    - Capturar evidencia: frame antes, durante y después

26. **Optimización de Rendimiento (8 puntos)**
    - Profiling de pipeline completo
    - Identificar cuellos de botella
    - Optimizaciones:
      - Batch inference para detección
      - Skip frames en escenas estáticas
      - Cache de resultados
    - Objetivo: latencia <250ms por frame

#### Entregables
- Detección de los 3 tipos de infracciones funcionando
- Sistema cumpliendo con latencia objetivo (<250ms)
- Evidencia multimedia completa por infracción

#### Definition of Done
- [ ] Detección de semáforo con precisión ≥95%
- [ ] Infracciones de luz roja detectadas correctamente
- [ ] Latencia de pipeline <250ms
- [ ] Throughput de 30 fps sostenido

---

### **SPRINT 7: Generación de Video Clips y UI Mejorada** (2 semanas)

#### Objetivos
- Generar clips de video de 15 segundos por infracción
- Mejorar dashboard de operadores
- Implementar flujo de validación manual

#### Historias de Usuario
27. **Generación de Video Clips (8 puntos)**
    - Implementar VideoClipGenerator
    - Buffer circular de últimos 10 segundos
    - Al detectar infracción: guardar 10s antes + 5s después
    - Codificar con H.264 (FFmpeg)
    - Subir a MinIO bucket `traffic-videos`
    - Comprimir para optimizar almacenamiento

28. **Dashboard de Validación (13 puntos)**
    - Pantalla de revisión de infracciones pendientes
    - Reproductor de video embebido
    - Visualización de metadatos: velocidad, placa, confianza
    - Botones: Validar, Rechazar, Marcar para revisión
    - Campo de notas del operador
    - Teclado shortcuts para agilizar validación

29. **Reportes Básicos (8 puntos)**
    - Endpoint GET /api/reports/daily
    - Estadísticas: total por tipo, horario pico, top infractores
    - Gráficos: Chart.js o Plotly
    - Exportar a PDF con ReportLab
    - Exportar a Excel con openpyxl

30. **Sistema de Notificaciones (5 puntos)**
    - Notificación in-app al detectar infracción
    - WebSocket para actualizaciones en tiempo real
    - Badge de contador en menú
    - (Opcional) Email a supervisor al final del día

#### Entregables
- Clips de video de 15s por infracción
- Dashboard completo de validación
- Reportes diarios exportables
- Notificaciones en tiempo real

#### Definition of Done
- [ ] Videos generados correctamente (10s antes + 5s después)
- [ ] Dashboard usable y responsive
- [ ] Reportes con datos precisos
- [ ] WebSocket funcionando sin pérdida de mensajes

---

### **SPRINT 8: Integración SUNARP** (2 semanas)

#### Objetivos
- Integrar API de SUNARP para enriquecimiento de datos
- Implementar cache de consultas
- Procesar enriquecimiento de forma asíncrona

#### Historias de Usuario
31. **Cliente de SUNARP API (8 puntos)**
    - Implementar SUNARPClient
    - Parsear respuesta de API (JSON)
    - Manejo de errores: timeout, placa no encontrada, rate limiting
    - Tests con API real (sandbox si está disponible)
    - Documentación de formato de respuesta

32. **Cache de Consultas (5 puntos)**
    - Configurar Redis como cache
    - TTL de 24 horas para consultas exitosas
    - Key pattern: `sunarp:{plate}`
    - Invalidar cache al actualizar manualmente

33. **Enriquecimiento Asíncrono (8 puntos)**
    - Implementar Celery task: enrich_vehicle_data
    - Trigger al crear infracción con placa nueva
    - Actualizar vehicle y driver en DB
    - Retry logic: 3 intentos con backoff exponencial
    - Logging de consultas exitosas/fallidas

34. **Modelo de Datos - Drivers (5 puntos)**
    - Implementar tabla drivers
    - Relación: infractions.driver_dni → drivers.dni
    - CRUD de conductores en Django Admin
    - Endpoint GET /api/drivers/{dni}

35. **UI de Enriquecimiento (5 puntos)**
    - Botón "Consultar SUNARP" en detalle de infracción
    - Mostrar datos de vehículo y propietario
    - Indicador de "Consultando..." mientras carga
    - Manejo de errores: "Placa no encontrada"

#### Entregables
- Integración funcional con API SUNARP
- Enriquecimiento automático de infracciones
- Cache de consultas para optimizar costos
- UI mostrando datos de propietario

#### Definition of Done
- [ ] Consultas SUNARP exitosas en ≥95% de casos
- [ ] Cache reduciendo consultas repetidas en ≥60%
- [ ] Celery tasks ejecutándose sin errores
- [ ] UI mostrando datos enriquecidos

---

### **SPRINT 9: Machine Learning Predictivo** (2 semanas)

#### Objetivos
- Implementar modelo de predicción de reincidencia
- Integrar MLflow para gestión de modelos
- Calcular score de riesgo por conductor

#### Historias de Usuario
36. **Feature Engineering (8 puntos)**
    - Implementar extract_features(driver_dni)
    - Features: historial de infracciones, recencia, patrones temporales
    - Almacenar features en tabla para entrenamiento
    - Generar dataset sintético inicial (basado en distribuciones realistas)

37. **Entrenamiento de Modelo (13 puntos)**
    - Configurar MLflow tracking server
    - Implementar train_recidivism_model con XGBoost
    - Hyperparameter tuning con Optuna
    - Validación cruzada (5-fold)
    - Métricas: accuracy, precision, recall, AUC
    - Objetivo: AUC ≥0.75

38. **Inferencia y Deployment (8 puntos)**
    - Implementar ML Service con FastAPI
    - Endpoint POST /api/ml/predict/recidivism
    - Cargar modelo desde MLflow Model Registry
    - Calcular score al validar infracción
    - Almacenar en infractions.recidivism_risk

39. **Modelo de Datos - ML Models (5 puntos)**
    - Implementar tabla ml_models
    - Versionamiento de modelos
    - Metadata: métricas, hiperparámetros, path
    - Endpoint GET /api/ml/models/

40. **UI de Analítica Predictiva (5 puntos)**
    - Sección "Análisis de Riesgo" en detalle de conductor
    - Visualizar score de reincidencia (0-100)
    - Gráfico de evolución de score en el tiempo
    - Top factores de riesgo (Feature importance)

#### Entregables
- Modelo de ML entrenado con AUC ≥0.75
- Predicción de riesgo calculándose automáticamente
- MLflow registrando experimentos y modelos
- Dashboard mostrando scores de riesgo

#### Definition of Done
- [ ] Modelo con AUC ≥0.75 en test set
- [ ] Predicciones ejecutándose en <100ms
- [ ] MLflow tracking configurado
- [ ] UI mostrando scores de forma comprensible

---

### **SPRINT 10: Optimización y Calidad** (2 semanas)

#### Objetivos
- Optimizar rendimiento para cumplir SLAs
- Aumentar cobertura de tests a ≥80%
- Implementar monitoreo completo

#### Historias de Usuario
41. **Optimización de Inferencia (8 puntos)**
    - Profiling con cProfile y line_profiler
    - Optimizar preprocessing de imágenes
    - Batch inference para YOLOv8
    - Cuantización de modelos (INT8)
    - Medir impacto en latencia y throughput

42. **Testing Exhaustivo (13 puntos)**
    - Unit tests para todos los módulos críticos
    - Integration tests del pipeline completo
    - E2E tests con Playwright/Selenium
    - Load testing con Locust (simular 50 cámaras)
    - Coverage report ≥80%

43. **Monitoreo con Prometheus & Grafana (8 puntos)**
    - Instrumentar código con prometheus_client
    - Métricas: fps, latency, detections, GPU utilization
    - Configurar Grafana dashboards
    - Alertas: latencia >300ms, GPU >90%, stream down

44. **Logging Centralizado (5 punts)**
    - Configurar ELK Stack (Elasticsearch, Logstash, Kibana)
    - Structured logging con structlog
    - Niveles: DEBUG, INFO, WARNING, ERROR
    - Índices por servicio: inference-*, django-*

45. **Documentación Técnica (5 puntos)**
    - README.md completo con guía de instalación
    - API documentation con Swagger/Redoc
    - Architecture Decision Records (ADRs)
    - Troubleshooting guide

#### Entregables
- Sistema optimizado cumpliendo SLAs
- Cobertura de tests ≥80%
- Monitoreo completo con alertas
- Documentación técnica exhaustiva

#### Definition of Done
- [ ] Latencia <250ms sostenida
- [ ] Tests con coverage ≥80%
- [ ] Dashboards de Grafana configurados
- [ ] Documentación revisada y aprobada

---

### **SPRINT 11: Despliegue en Producción** (2 semanas)

#### Objetivos
- Configurar infraestructura de producción
- Desplegar en Kubernetes
- Implementar CI/CD completo

#### Historias de Usuario
46. **Infraestructura Kubernetes (13 puntos)**
    - Crear cluster EKS/GKE/AKS
    - Configurar node pools: CPU, GPU
    - Deployments, Services, Ingress
    - ConfigMaps, Secrets
    - Persistent Volumes para PostgreSQL, models

47. **CI/CD Pipeline (8 puntos)**
    - GitHub Actions workflows:
      - Lint & Test en cada PR
      - Build & Push images a Docker Registry
      - Deploy a staging automático
      - Deploy a producción con aprobación manual
    - Rollback automático en caso de fallo

48. **Configuración de Seguridad (8 puntos)**
    - TLS/SSL con Let's Encrypt
    - Certificados para APIs
    - Secrets management con HashiCorp Vault
    - RBAC en Kubernetes
    - Network policies

49. **Backup y Disaster Recovery (5 puntos)**
    - Backup automático de PostgreSQL (diario)
    - Replicación de videos a cold storage (S3 Glacier)
    - Plan de recuperación ante desastres
    - RTO: 4 horas, RPO: 24 horas

50. **Health Checks y Readiness Probes (3 puntos)**
    - Liveness probes en todos los servicios
    - Readiness probes considerando dependencias
    - Graceful shutdown

#### Entregables
- Sistema desplegado en producción
- CI/CD funcionando sin intervención manual
- Seguridad implementada (TLS, secrets, RBAC)
- Backups automáticos configurados

#### Definition of Done
- [ ] Cluster K8s en producción operativo
- [ ] CI/CD desplegando automáticamente
- [ ] Certificados SSL válidos
- [ ] Backups exitosos por 7 días consecutivos

---

### **SPRINT 12: Capacitación y Go-Live** (2 semanas)

#### Objetivos
- Capacitar a operadores y administradores
- Realizar pruebas de aceptación de usuario (UAT)
- Go-live con monitoreo intensivo

#### Historias de Usuario
51. **Manual de Usuario (5 puntos)**
    - Crear manual para operadores (PDF + video)
    - Secciones: login, revisar infracciones, validar/rechazar, reportes
    - Screenshots y anotaciones
    - Glosario de términos

52. **Capacitación Presencial (8 puntos)**
    - Sesiones de 2 horas con operadores (3 grupos)
    - Demostración en vivo del sistema
    - Ejercicios prácticos: validar 20 infracciones
    - Q&A y recolección de feedback
    - Material de referencia: cheat sheet

53. **Pruebas de Aceptación de Usuario (13 puntos)**
    - Definir casos de prueba con cliente
    - Ejecutar UAT en ambiente de staging
    - Documentar bugs y issues
    - Resolver issues críticos
    - Aprobación formal del cliente

54. **Go-Live (8 puntos)**
    - Desplegar en producción en horario de baja carga
    - Monitoreo intensivo 24/7 durante primera semana
    - Equipo de guardia para incidentes
    - Comunicación a stakeholders
    - Registro de issues post-lanzamiento

55. **Post-Mortem y Lecciones Aprendidas (3 puntos)**
    - Reunión de retrospectiva del proyecto
    - Documentar lecciones aprendidas
    - Identificar mejoras para futuras iteraciones
    - Actualizar procesos y documentación

#### Entregables
- Operadores capacitados y certificados
- UAT aprobado por cliente
- Sistema en producción procesando infracciones reales
- Documentación de lecciones aprendidas

#### Definition of Done
- [ ] 100% operadores capacitados
- [ ] UAT aprobado sin issues críticos
- [ ] Go-live exitoso sin incidentes mayores
- [ ] Retroalimentación post-go-live recolectada

---

## 3. Resumen de Estimaciones

| Sprint | Duración | Story Points | Equipo Requerido |
|--------|----------|--------------|------------------|
| 1 | 2 semanas | 34 | 4 devs |
| 2 | 2 semanas | 39 | 4 devs |
| 3 | 2 semanas | 42 | 4 devs |
| 4 | 2 semanas | 36 | 4 devs |
| 5 | 2 semanas | 26 | 3 devs |
| 6 | 2 semanas | 29 | 3 devs |
| 7 | 2 semanas | 34 | 4 devs |
| 8 | 2 semanas | 31 | 3 devs |
| 9 | 2 semanas | 39 | 4 devs |
| 10 | 2 semanas | 39 | 4 devs |
| 11 | 2 semanas | 37 | 3 devs + 1 DevOps |
| 12 | 2 semanas | 37 | 2 devs + 1 PM |
| **Total** | **24 semanas** | **393 SP** | **Promedio 3.5 devs** |

**Velocity estimado**: 35-40 story points por sprint (equipo de 4 desarrolladores)

---

## 4. Hitos y Entregas Clave

| Hito | Sprint | Fecha Estimada | Entregable |
|------|--------|----------------|------------|
| **M1: PoC Funcional** | 3 | Semana 6 | Detección de exceso de velocidad funcionando con 1 cámara |
| **M2: Detección Completa** | 6 | Semana 12 | 3 tipos de infracciones detectándose automáticamente |
| **M3: Enriquecimiento** | 8 | Semana 16 | Integración SUNARP y datos completos de vehículos |
| **M4: ML Predictivo** | 9 | Semana 18 | Modelo de reincidencia en producción |
| **M5: Producción** | 11 | Semana 22 | Sistema desplegado en Kubernetes |
| **M6: Go-Live** | 12 | Semana 24 | Sistema operativo con usuarios reales |

---

## 5. Dependencias y Riesgos

### 5.1 Dependencias Externas
1. **API SUNARP**: Disponibilidad y estabilidad de la API
   - Mitigación: Implementar fallback manual para consultas
2. **Cámaras EZVIZ**: Suministro y configuración en tiempo
   - Mitigación: Comprar cámaras con 2 semanas de antelación
3. **Infraestructura Cloud**: Aprovisionamiento de GPUs
   - Mitigación: Reservar instancias GPU con anticipación

### 5.2 Riesgos Técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Precisión de OCR baja en condiciones nocturnas | Media | Alto | Entrenar con dataset aumentado, iluminación IR |
| Latencia >250ms por frame | Media | Alto | Optimización continua, hardware adecuado (RTX 3060 Ti+) |
| Falsos positivos >10% | Alta | Medio | Ajustar thresholds, validación manual inicial |
| Pérdida de stream RTSP | Media | Medio | Reconexión automática, buffer local en cámara |
| Sobrecarga de API SUNARP | Baja | Medio | Cache agresivo, rate limiting, plan premium |
| Drift de modelo ML | Baja | Bajo | Monitoreo de métricas, reentrenamiento trimestral |

### 5.3 Riesgos de Proyecto

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Cambios de alcance durante desarrollo | Alta | Alto | Change control process, aprobación formal |
| Rotación de personal clave | Baja | Alto | Documentación exhaustiva, pair programming |
| Retrasos en UAT | Media | Medio | Comenzar UAT en Sprint 10, feedback temprano |
| Resistencia al cambio de operadores | Media | Medio | Capacitación temprana, involucramiento en diseño |

---

## 6. Recursos y Presupuesto

### 6.1 Equipo de Desarrollo

| Rol | Cantidad | Dedicación | Duración | Costo Estimado (USD) |
|-----|----------|------------|----------|---------------------|
| Tech Lead | 1 | 100% | 6 meses | $36,000 |
| Backend Engineers | 2 | 100% | 6 meses | $48,000 |
| ML Engineers | 2 | 100% | 6 meses | $48,000 |
| DevOps Engineer | 1 | 50% | 6 meses | $18,000 |
| QA Engineer | 1 | 100% | 4 meses | $16,000 |
| UX/UI Designer | 1 | 25% | 3 meses | $4,500 |
| **Subtotal Personal** | | | | **$170,500** |

### 6.2 Infraestructura (6 meses)

| Recurso | Especificación | Cantidad | Costo Mensual | Total 6 meses |
|---------|----------------|----------|---------------|---------------|
| Servidor GPU (Inferencia) | NVIDIA RTX 3060 Ti, 32GB RAM | 2 | $800 | $9,600 |
| Servidor CPU (Django) | 8 vCPU, 16GB RAM | 2 | $200 | $2,400 |
| PostgreSQL (RDS) | db.m5.xlarge | 1 | $300 | $1,800 |
| Redis (ElastiCache) | cache.m5.large | 1 | $100 | $600 |
| MinIO/S3 Storage | 10 TB | 1 | $250 | $1,500 |
| Kubernetes Cluster | 5 nodes | 1 | $500 | $3,000 |
| Monitoring (Grafana Cloud) | Pro plan | 1 | $50 | $300 |
| **Subtotal Infra** | | | | **$19,200** |

### 6.3 Cámaras IoT

| Item | Especificación | Cantidad | Costo Unitario | Total |
|------|----------------|----------|----------------|-------|
| EZVIZ H6C Pro 2K | Cámara IP 2K, PTZ, IR | 10 | $150 | $1,500 |
| Soporte de montaje | Poste/pared | 10 | $30 | $300 |
| Cableado y accesorios | Ethernet, PoE | 10 | $50 | $500 |
| **Subtotal Hardware IoT** | | | | **$2,300** |

### 6.4 Licencias y APIs

| Item | Tipo | Costo |
|------|------|-------|
| API SUNARP | 20,000 consultas/mes × 6 meses | $1,200 |
| GitHub Enterprise | 10 usuarios × 6 meses | $252 |
| Sentry | Team plan × 6 meses | $156 |
| MLflow (Databricks) | Community (gratis) | $0 |
| **Subtotal Licencias** | | **$1,608** |

### 6.5 Presupuesto Total

| Categoría | Costo (USD) |
|-----------|-------------|
| Personal | $170,500 |
| Infraestructura Cloud | $19,200 |
| Hardware IoT | $2,300 |
| Licencias y APIs | $1,608 |
| Contingencia (10%) | $19,360 |
| **TOTAL** | **$212,968** |

---

## 7. Criterios de Aceptación por Fase

### Fase 1: PoC (Sprint 1-3)
- [x] Stream RTSP de cámara recibido y visualizado
- [x] YOLOv8 detectando vehículos con precisión ≥85%
- [x] Tracking manteniendo IDs por ≥5 segundos
- [x] Velocidad calculada con error <5%
- [x] Al menos 1 infracción de exceso de velocidad detectada y almacenada
- [x] Dashboard mostrando infracciones detectadas

### Fase 2: Sistema Completo (Sprint 4-7)
- [x] OCR de placas con precisión ≥85%
- [x] Detección de 3 tipos de infracciones funcionando
- [x] Latencia de pipeline <250ms por frame
- [x] Clips de video de 15 segundos generados automáticamente
- [x] Dashboard de validación completo y usable
- [x] Reportes diarios exportables a PDF

### Fase 3: Integración y Analítica (Sprint 8-10)
- [x] Integración SUNARP enriqueciendo datos automáticamente
- [x] Modelo ML con AUC ≥0.75
- [x] Scores de riesgo calculados por conductor
- [x] Cobertura de tests ≥80%
- [x] Monitoreo con Prometheus y Grafana operativo
- [x] Documentación técnica completa

### Fase 4: Producción (Sprint 11-12)
- [x] Sistema desplegado en Kubernetes
- [x] CI/CD desplegando automáticamente
- [x] TLS/SSL configurado
- [x] Backups automáticos funcionando
- [x] Operadores capacitados
- [x] UAT aprobado por cliente
- [x] Go-live exitoso

---

## 8. Plan de Comunicación

### 8.1 Stakeholder Meetings

| Reunión | Frecuencia | Asistentes | Objetivo |
|---------|------------|------------|----------|
| Daily Standup | Diaria | Equipo Dev | Sincronización diaria |
| Sprint Planning | Cada 2 semanas | Equipo + PO | Planificar sprint |
| Sprint Review | Cada 2 semanas | Equipo + Cliente | Demo de funcionalidades |
| Retrospectiva | Cada 2 semanas | Equipo | Mejora continua |
| Steering Committee | Mensual | Tech Lead + Stakeholders | Alineación estratégica |

### 8.2 Canales de Comunicación

- **Slack**: Comunicación diaria del equipo
- **Jira**: Tracking de tareas y bugs
- **Confluence**: Documentación y decisiones
- **GitHub**: Code reviews y discusiones técnicas
- **Email**: Comunicación formal con cliente

---

## 9. Métricas de Éxito del Proyecto

### 9.1 Durante Desarrollo

| Métrica | Objetivo | Medición |
|---------|----------|----------|
| Velocity | 35-40 SP/sprint | Burndown chart |
| Bug Rate | <5 bugs críticos/sprint | Jira reports |
| Code Coverage | ≥80% | CI pipeline |
| On-time Delivery | 100% milestones | Gantt chart |

### 9.2 Post Go-Live (primeros 3 meses)

| Métrica | Objetivo | Medición |
|---------|----------|----------|
| Precisión de Detección | ≥90% diurna, ≥80% nocturna | Manual validation (sample 100/día) |
| Uptime | ≥99.5% | Prometheus |
| Latencia Promedio | <250ms | Prometheus |
| Satisfacción de Usuarios | ≥4/5 | Encuesta mensual |
| Infracciones Procesadas | ≥500/día | Dashboard |
| False Positive Rate | ≤5% | Manual validation |

---

**Versión**: 1.0  
**Fecha**: 2025-11-01  
**Aprobado por**: [Tech Lead / Product Owner]  
**Próxima Revisión**: Sprint 6 (Semana 12)
