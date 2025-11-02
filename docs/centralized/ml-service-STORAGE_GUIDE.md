# Sistema de Almacenamiento y Gestión de Datos - Documentación

## Descripción General

El sistema de almacenamiento proporciona una solución integral para la gestión de datos del sistema de análisis de tráfico, incluyendo almacenamiento local, cloud storage, base de datos y cache distribuido.

## Arquitectura

### Componentes Principales

1. **StorageManager** - Gestores específicos para cada tipo de almacenamiento
   - `LocalStorageManager` - Almacenamiento en sistema de archivos local
   - `CloudStorageManager` - Almacenamiento en S3/MinIO
   - `DatabaseManager` - Gestión de base de datos PostgreSQL
   - `CacheManager` - Cache distribuido con Redis

2. **StorageService** - Servicio unificado de alto nivel
   - Estrategias de almacenamiento inteligentes
   - Placement automático de datos
   - Gestión de ciclo de vida
   - Sincronización entre backends

3. **DataUtils** - Utilidades de gestión de datos
   - `DataValidator` - Validación de calidad de datos
   - `DataLifecycleManager` - Gestión de retención y archivado
   - `DataMigrationManager` - Migración entre sistemas
   - `DataAnalyzer` - Análisis de patrones y calidad
   - `DataExporter` - Exportación en múltiples formatos

4. **API Server** - Servidor REST para gestión de almacenamiento
   - Endpoints para upload/download de archivos
   - Gestión de registros de violaciones
   - Análisis y estadísticas
   - Operaciones de mantenimiento

## Configuración

### StorageConfig

```python
config = StorageConfig(
    # Almacenamiento local
    local_base_path="/data/traffic_analysis",
    max_local_size_gb=100.0,
    
    # Base de datos
    db_host="localhost",
    db_port=5432,
    db_name="traffic_system",
    db_user="admin",
    db_password="password",
    
    # S3/MinIO
    s3_endpoint="http://localhost:9000",
    s3_access_key="access_key",
    s3_secret_key="secret_key",
    s3_bucket="traffic-evidence",
    
    # Redis
    redis_host="localhost",
    redis_port=6379,
    redis_db=0,
    
    # Políticas de retención
    image_retention_days=90,
    video_retention_days=30,
    metadata_retention_days=365,
    
    # Configuración de rendimiento
    compression_enabled=True,
    parallel_uploads=4
)
```

## Estrategias de Almacenamiento

### StorageStrategy

- **LOCAL_ONLY** - Solo almacenamiento local
- **CLOUD_ONLY** - Solo almacenamiento en cloud
- **LOCAL_THEN_CLOUD** - Local primero, cloud cuando se llena
- **CLOUD_WITH_CACHE** - Cloud con cache local
- **HYBRID** - Distribución inteligente basada en tamaño y tipo

## Uso del Sistema

### Inicialización

```python
from src.storage import StorageService, StorageConfig, StorageStrategy

# Configuración
config = StorageConfig(
    local_base_path="/data/traffic",
    s3_access_key="your_key",
    s3_secret_key="your_secret"
)

# Servicio de almacenamiento
storage = StorageService(config, StorageStrategy.HYBRID)
```

### Almacenar Evidencias de Violación

```python
# Crear registro de violación
violation_record = ViolationRecord(
    violation_id="V001",
    device_id="cam_001",
    violation_type="speed",
    timestamp=datetime.now(),
    vehicle_bbox=[100, 100, 200, 200],
    vehicle_class="car",
    confidence=0.95,
    image_path="",  # Se asignará automáticamente
    camera_info={"location": "Main St"},
    processing_time_ms=150.0,
    model_versions={"detector": "yolov8"}
)

# Almacenar evidencias completas
stored_files = await storage.store_violation_evidence(
    violation_record=violation_record,
    image=evidence_image,          # numpy array
    video_segment=video_bytes      # bytes (opcional)
)

print(f"Archivos almacenados: {list(stored_files.keys())}")
```

### Almacenar Archivos Individuales

```python
# Almacenar imagen
image_metadata = await storage.store_image(
    image=frame,
    file_id="detection_001",
    metadata={"device_id": "cam_001", "timestamp": "2025-11-01T10:00:00"}
)

# Almacenar video
video_metadata = await storage.store_video_segment(
    video_data=video_bytes,
    file_id="segment_001",
    duration_seconds=10.0
)

# Almacenar metadatos
metadata_file = await storage.store_metadata(
    data={"detections": [...], "analysis_results": {...}},
    file_id="analysis_001"
)
```

### Recuperar Archivos

```python
# Recuperar archivo por ID
file_data, metadata = await storage.retrieve_file("detection_001")

# Recuperar imagen decodificada
image, metadata = await storage.retrieve_image("detection_001")

# Generar URL de acceso temporal
access_url = storage.generate_access_url("detection_001", expires_in=3600)
```

### Consultar Violaciones

```python
# Obtener violaciones con filtros
violations = storage.get_violation_records(
    device_id="cam_001",
    violation_type="speed",
    start_time=datetime.now() - timedelta(days=7),
    limit=100
)

for violation in violations:
    print(f"Violación {violation['violation_id']}: {violation['violation_type']}")
```

## Validación de Datos

### DataValidator

```python
from src.storage import DataValidator

validator = DataValidator()

# Validar registro de violación
validation_result = validator.validate_violation_record(violation_record)

if validation_result["valid"]:
    print(f"Registro válido (score: {validation_result['score']})")
else:
    print(f"Errores: {validation_result['errors']}")
    print(f"Advertencias: {validation_result['warnings']}")

# Validar imagen
image_validation = validator._validate_image_data(image)
print(f"Métricas de imagen: {image_validation['metrics']}")
```

## Gestión del Ciclo de Vida

### DataLifecycleManager

```python
from src.storage import DataLifecycleManager

lifecycle = DataLifecycleManager(storage)

# Aplicar políticas de retención
retention_results = await lifecycle.apply_retention_policies()
print(f"Archivos eliminados: {retention_results['files_deleted']}")

# Crear snapshot de datos
snapshot_result = await lifecycle.create_data_snapshot("daily_backup_001")
print(f"Snapshot creado: {snapshot_result['snapshot_location']}")
```

## Análisis de Datos

### DataAnalyzer

```python
from src.storage import DataAnalyzer

analyzer = DataAnalyzer(storage)

# Análisis de calidad de datos
quality_analysis = await analyzer.analyze_data_quality(sample_size=1000)
print(f"Score promedio: {quality_analysis['average_quality_score']}")
print(f"Registros válidos: {quality_analysis['valid_records']}")

# Análisis de patrones de almacenamiento
storage_patterns = await analyzer.analyze_storage_patterns()
print(f"Eficiencia de almacenamiento: {storage_patterns['storage_efficiency']}")
```

## Migración de Datos

### DataMigrationManager

```python
from src.storage import DataMigrationManager

# Migrar entre sistemas de almacenamiento
source_storage = StorageService(config_old, StorageStrategy.LOCAL_ONLY)
target_storage = StorageService(config_new, StorageStrategy.CLOUD_ONLY)

migrator = DataMigrationManager(source_storage, target_storage)

# Migrar datos de violaciones
migration_results = await migrator.migrate_violation_data(
    start_date=datetime(2025, 10, 1),
    end_date=datetime(2025, 11, 1)
)

print(f"Registros migrados: {migration_results['migrated_records']}")
print(f"Archivos migrados: {migration_results['migrated_files']}")
```

## Exportación de Datos

### DataExporter

```python
from src.storage import DataExporter

exporter = DataExporter(storage)

# Exportar violaciones a CSV
csv_result = await exporter.export_violations_csv(
    start_date=datetime(2025, 11, 1),
    end_date=datetime(2025, 11, 2),
    output_path="/exports/violations_2025_11.csv"
)

# Exportar estadísticas a JSON
json_result = await exporter.export_statistics_json(
    output_path="/exports/system_stats.json"
)
```

## API REST

### Servidor de Almacenamiento

```python
from src.storage.api_server import create_storage_app
import uvicorn

# Crear aplicación FastAPI
app = create_storage_app(config)

# Ejecutar servidor
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Endpoints Principales

#### Upload de Archivos
- `POST /files/upload/image` - Subir imagen
- `POST /files/upload/video` - Subir video

#### Gestión de Archivos
- `GET /files/{file_id}` - Descargar archivo
- `GET /files/{file_id}/url` - Obtener URL temporal

#### Violaciones
- `POST /violations` - Crear registro de violación
- `GET /violations` - Consultar violaciones

#### Estadísticas
- `GET /storage/stats` - Estadísticas de almacenamiento
- `GET /analytics/quality` - Análisis de calidad
- `GET /analytics/storage` - Análisis de patrones

#### Mantenimiento
- `POST /storage/cleanup` - Limpieza de datos
- `POST /lifecycle/snapshot` - Crear snapshot
- `POST /lifecycle/retention` - Aplicar retención

## Ejemplos de Uso con API

### Upload de Imagen

```bash
curl -X POST "http://localhost:8001/files/upload/image" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@evidence.jpg" \
  -F "device_id=cam_001" \
  -F "violation_id=V001"
```

### Crear Violación Completa

```bash
curl -X POST "http://localhost:8001/violations" \
  -H "Content-Type: multipart/form-data" \
  -F "violation_id=V001" \
  -F "device_id=cam_001" \
  -F "violation_type=speed" \
  -F "timestamp=2025-11-01T10:00:00" \
  -F "vehicle_bbox=[100,100,200,200]" \
  -F "vehicle_class=car" \
  -F "confidence=0.95" \
  -F "processing_time_ms=150" \
  -F "image_file=@evidence.jpg" \
  -F "video_file=@segment.mp4"
```

### Consultar Violaciones

```bash
curl "http://localhost:8001/violations?device_id=cam_001&start_date=2025-11-01T00:00:00&limit=50"
```

### Obtener Estadísticas

```bash
curl "http://localhost:8001/storage/stats"
```

## Monitoreo y Mantenimiento

### Estadísticas del Sistema

```python
# Obtener estadísticas completas
stats = storage.get_storage_statistics()

print(f"Uso local: {stats['local_storage']['usage_percentage']}%")
print(f"Archivos procesados: {stats['operation_stats']['files_stored']}")
print(f"Cache hits: {stats['operation_stats']['cache_hits']}")
```

### Limpieza Automática

```python
# Limpieza de datos expirados
cleanup_results = await storage.cleanup_expired_data(dry_run=False)
print(f"Archivos eliminados: {cleanup_results['local_files_deleted']}")

# Verificación de integridad
integrity_results = await storage.verify_data_integrity()
print(f"Archivos verificados: {integrity_results['files_checked']}")
```

## Mejores Prácticas

### Configuración de Producción

1. **Almacenamiento**
   - Usar SSD para almacenamiento local
   - Configurar backup automático a cloud
   - Establecer políticas de retención apropiadas

2. **Base de Datos**
   - Configurar réplicas para alta disponibilidad
   - Implementar backup automático
   - Monitorear rendimiento de consultas

3. **Cache**
   - Usar Redis Cluster para escalabilidad
   - Configurar TTL apropiados
   - Monitorear uso de memoria

4. **Seguridad**
   - Encriptar datos sensibles
   - Configurar acceso con roles específicos
   - Implementar audit logging

### Optimización de Rendimiento

1. **Compresión**
   - Habilitar compresión para archivos grandes
   - Usar formatos optimizados (WebP para imágenes)

2. **Caching**
   - Cache resultados de detección frecuentes
   - Implementar cache de metadatos

3. **Distribución**
   - Distribuir archivos por fecha y tipo
   - Usar múltiples buckets S3 por región

4. **Monitoreo**
   - Alertas por uso de almacenamiento
   - Métricas de rendimiento de API
   - Logs de errores y excepciones

## Troubleshooting

### Problemas Comunes

1. **Espacio en disco insuficiente**
   - Ejecutar limpieza manual
   - Migrar archivos antiguos a cloud
   - Ajustar políticas de retención

2. **Errores de conexión a base de datos**
   - Verificar configuración de red
   - Revisar credenciales
   - Comprobar estado del servicio

3. **Fallos en upload a S3**
   - Verificar credenciales AWS
   - Comprobar permisos de bucket
   - Revisar configuración de red

4. **Cache Redis no disponible**
   - El sistema funciona sin cache (degraded)
   - Verificar estado del servicio Redis
   - Revisar configuración de conexión

### Logs y Debugging

```python
import logging

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Los módulos de storage generarán logs detallados
storage = StorageService(config, StorageStrategy.HYBRID)
```

## Roadmap y Extensiones

### Funcionalidades Futuras

1. **Inteligencia Artificial**
   - Clasificación automática de archivos
   - Deduplicación inteligente
   - Predicción de patrones de acceso

2. **Escalabilidad**
   - Sharding automático de base de datos
   - Load balancing de APIs
   - Clustering de almacenamiento

3. **Integración**
   - Webhook notifications
   - APIs de terceros
   - Plugins personalizados

4. **Analytics Avanzados**
   - Machine Learning para optimización
   - Predicción de crecimiento
   - Análisis de costos

Este sistema de almacenamiento proporciona una base sólida y escalable para gestionar todos los datos del sistema de análisis de tráfico, con capacidades avanzadas de validación, análisis y mantenimiento.