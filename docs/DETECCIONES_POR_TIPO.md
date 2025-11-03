# 🎯 Sistema de Almacenamiento de Detecciones por Tipo

## ✅ Implementación Completada

Se ha implementado un sistema completo para **almacenar TODAS las detecciones** en la base de datos, organizadas por tipo de vehículo.

## 📊 Nuevos Modelos

### 1. **VehicleDetection** (`backend-django/infractions/models_detection.py`)

Almacena **cada detección** individual:

**Campos principales:**
- `vehicle_type`: car, truck, bus, motorcycle, bicycle, person, other
- `confidence`: Confianza de la detección (0-1)
- `device`: Dispositivo que realizó la detección
- `zone`: Zona donde ocurrió
- `bbox_x1, bbox_y1, bbox_x2, bbox_y2`: Coordenadas del bounding box (normalizado 0-1)
- `license_plate_detected`: Placa detectada (si aplica)
- `estimated_speed`: Velocidad estimada (si aplica)
- `has_infraction`: Boolean indicando si tiene infracción asociada
- `infraction`: FK a Infraction (si tiene)
- `source`: Fuente (camera, webcam_local, etc)
- `detected_at`: Timestamp de detección
- `metadata`: JSON con datos adicionales

### 2. **DetectionStatistics** (`backend-django/infractions/models_detection.py`)

Estadísticas agregadas por período:

**Campos principales:**
- `period_type`: hourly, daily, weekly, monthly
- `car_count, truck_count, bus_count`, etc: Conteo por tipo
- `total_detections`: Total de detecciones
- `total_with_plate`: Detecciones con placa identificada
- `total_infractions`: Total con infracciones
- `avg_confidence`: Promedio de confianza
- `avg_speed`: Promedio de velocidad

## 🔌 Nuevos Endpoints API

### 1. Crear Detecciones en Bulk

**POST** `/api/infractions/detections/bulk_create/`

**Payload:**
```json
{
  "detections": [
    {
      "vehicle_type": "car",
      "confidence": 0.95,
      "bbox": [0.1, 0.2, 0.3, 0.4],
      "license_plate": "ABC-123",
      "license_plate_confidence": 0.85,
      "speed": 65.5,
      "has_infraction": false,
      "metadata": {}
    }
  ],
  "device_id": "uuid-optional",
  "zone_id": "uuid-optional",
  "source": "webcam_local"
}
```

**Respuesta:**
```json
{
  "status": "success",
  "created_count": 1,
  "detections": [...]
}
```

### 2. Ver Resumen de Detecciones

**GET** `/api/infractions/detections/summary/?hours=24`

**Respuesta:**
```json
{
  "total_detections": 1523,
  "by_vehicle_type": {
    "car": 1200,
    "truck": 150,
    "motorcycle": 100,
    "bus": 73
  },
  "by_hour": {
    "0h_ago": 45,
    "1h_ago": 62,
    ...
  },
  "avg_confidence": 0.87,
  "with_license_plate": 856,
  "with_infractions": 23
}
```

### 3. Detecciones Recientes

**GET** `/api/infractions/detections/recent/?limit=50`

### 4. Detecciones por Tipo

**GET** `/api/infractions/detections/by_type/?hours=24`

**Respuesta:**
```json
[
  {
    "vehicle_type": "car",
    "total": 1200,
    "with_plate": 780,
    "with_infraction": 15,
    "avg_confidence": 0.92
  },
  {
    "vehicle_type": "truck",
    "total": 150,
    "with_plate": 120,
    "with_infraction": 5,
    "avg_confidence": 0.88
  }
]
```

### 5. Listar Todas las Detecciones

**GET** `/api/infractions/detections/`

Soporta filtros:
- `?vehicle_type=car`
- `?has_infraction=true`
- `?device=uuid`
- `?source=webcam_local`

### 6. Estadísticas

**GET** `/api/infractions/detection-stats/`

Filtros:
- `?period_type=hourly`
- `?device=uuid`
- `?zone=uuid`

## 🔄 Flujo de Datos

```
Webcam → WebSocket → Inference Service
                           ↓
                    YOLOv8 Detection
                           ↓
              ┌────────────┴────────────┐
              ↓                         ↓
    ALL Detections              Only Infractions
              ↓                         ↓
  POST /detections/bulk_create/   POST /infractions/from_detection/
              ↓                         ↓
    VehicleDetection table        Infraction table
```

## 📦 Archivos Creados

1. ✅ `backend-django/infractions/models_detection.py` - Modelos
2. ✅ `backend-django/infractions/serializers_detection.py` - Serializers
3. ✅ `backend-django/infractions/views_detection.py` - Views/ViewSets
4. ✅ `backend-django/infractions/urls.py` - URLs (actualizado)
5. ✅ `backend-django/infractions/admin.py` - Admin (actualizado)

## 🚀 Pasos para Activar

### 1. Crear las Migraciones

```bash
cd /home/bacsystem/github.com/sistema_in/backend-django
python manage.py makemigrations infractions
python manage.py migrate
```

### 2. Agregar Método a django_api.py

Agregar al archivo `inference-service/app/services/django_api.py`:

```python
async def create_vehicle_detections(
    self,
    detections: list,
    device_id: Optional[str] = None,
    source: str = "webcam_local"
) -> Optional[Dict[str, Any]]:
    """
    Create vehicle detections (all detections, not just infractions)
    """
    try:
        payload = {
            'detections': detections,
            'source': source
        }
        
        if device_id:
            payload['device_id'] = device_id
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/infractions/detections/bulk_create/",
                json=payload
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(
                    f"Created {result.get('created_count', 0)} vehicle detections"
                )
                return result
            else:
                logger.error(
                    "Failed to create vehicle detections",
                    status_code=response.status_code,
                    response=response.text
                )
                return None
                
    except Exception as e:
        logger.error(f"Error creating vehicle detections: {str(e)}", exc_info=True)
        return None
```

### 3. Reiniciar Servicios

```bash
# Reiniciar Django
ps aux | grep "manage.py runserver" | grep -v grep | awk '{print $2}' | xargs sudo kill
cd /home/bacsystem/github.com/sistema_in/backend-django
python manage.py runserver 0.0.0.0:8000 &

# Reiniciar Inference Service
docker restart traffic-inference
```

## 📊 Queries Útiles

### Ver Últimas Detecciones

```sql
SELECT 
    vehicle_type,
    confidence,
    license_plate_detected,
    has_infraction,
    detected_at
FROM infractions_vehicledetection
ORDER BY detected_at DESC
LIMIT 20;
```

### Contar por Tipo de Vehículo

```sql
SELECT 
    vehicle_type,
    COUNT(*) as total,
    COUNT(CASE WHEN license_plate_detected != '' THEN 1 END) as with_plate,
    COUNT(CASE WHEN has_infraction = true THEN 1 END) as with_infraction,
    AVG(confidence) as avg_confidence
FROM infractions_vehicledetection
WHERE detected_at >= NOW() - INTERVAL '24 hours'
GROUP BY vehicle_type
ORDER BY total DESC;
```

### Detecciones por Hora

```sql
SELECT 
    DATE_TRUNC('hour', detected_at) as hour,
    vehicle_type,
    COUNT(*) as count
FROM infractions_vehicledetection
WHERE detected_at >= NOW() - INTERVAL '24 hours'
GROUP BY hour, vehicle_type
ORDER BY hour DESC, count DESC;
```

## 🎯 Ventajas del Sistema

1. **Análisis de Tráfico**: Datos completos de flujo vehicular
2. **Machine Learning**: Data para entrenar y mejorar modelos
3. **Estadísticas**: Conteos por tipo, hora, ubicación
4. **Auditoría**: Registro completo de todas las detecciones
5. **Optimización**: Identificar patrones y mejorar detección
6. **Reportes**: Generar reportes detallados de tráfico

## 📈 Uso de Memoria

- **VehicleDetection**: ~300 bytes por registro
- **1000 detecciones/hora**: ~300 KB/hora = 7.2 MB/día
- **Con índices**: ~10 MB/día
- **Recomendación**: Limpiar registros > 30 días periódicamente

## 🔧 Configuración Adicional

### Desactivar Almacenamiento de Detecciones

Si solo quieres infracciones, comenta en `websocket.py`:

```python
# if detections:
#     asyncio.create_task(
#         self._save_all_detections_to_database(detections)
#     )
```

### Filtrar por Confianza Mínima

Modificar en `views_detection.py`:

```python
MIN_CONFIDENCE = 0.7  # Solo guardar detecciones > 70% confianza

for det_data in detections_data:
    if det_data['confidence'] < MIN_CONFIDENCE:
        continue  # Skip low confidence detections
    # ... resto del código
```

## ✅ Checklist de Implementación

- [x] Modelos creados (VehicleDetection, DetectionStatistics)
- [x] Serializers creados
- [x] Views/ViewSets creados
- [x] URLs registradas
- [x] Admin configurado
- [ ] Migraciones creadas y aplicadas (PENDIENTE)
- [ ] Método django_api agregado (PENDIENTE)
- [ ] Servicios reiniciados (PENDIENTE)
- [ ] Pruebas realizadas (PENDIENTE)

## 🧪 Testing

```bash
# Test endpoint detecciones
curl -X POST http://localhost:8000/api/infractions/detections/bulk_create/ \
  -H "Content-Type: application/json" \
  -d '{
    "detections": [
      {
        "vehicle_type": "car",
        "confidence": 0.95,
        "bbox": [0.1, 0.2, 0.3, 0.4],
        "license_plate": "TEST-123",
        "has_infraction": false
      }
    ],
    "source": "test"
  }'

# Ver resumen
curl http://localhost:8000/api/infractions/detections/summary/

# Ver por tipo
curl http://localhost:8000/api/infractions/detections/by_type/
```

