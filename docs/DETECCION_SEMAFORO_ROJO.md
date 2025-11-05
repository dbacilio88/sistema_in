# 🚦 Sistema de Detección de Infracciones por Semáforo en Rojo

## 📋 Resumen

El sistema detecta automáticamente cuando un vehículo cruza la línea de parada mientras el semáforo está en rojo, generando una infracción de tipo `red_light`.

---

## 🏗️ Arquitectura

### Componentes Implementados

#### 1. **ML Service - Traffic Light Detector**
- **Ubicación**: `ml-service/src/detection/traffic_light_detector.py`
- **Función**: Detecta el estado del semáforo (rojo/amarillo/verde) usando análisis de color HSV
- **Tecnología**: OpenCV + análisis HSV (no requiere modelo ML adicional)
- **Características**:
  - Detección por color en espacio HSV
  - Suavizado temporal (historial de 5 frames)
  - Soporte para ROI configurable
  - Opción futura para modelo YOLO especializado

#### 2. **Inference Service - Integration**
- **Ubicación**: `inference-service/app/services/`
- **Archivos**:
  - `traffic_light_detector.py`: Detector simplificado para inference
  - `model_service.py`: Integración con el pipeline de detección
- **Función**: 
  - Carga el detector de semáforos
  - Detecta estado en cada frame
  - Valida cruces de línea de parada

#### 3. **WebSocket Handler**
- **Ubicación**: `inference-service/app/api/websocket.py`
- **Función**:
  - Recibe frames del frontend
  - Detecta estado del semáforo si está habilitado
  - Compara posición del vehículo vs línea de parada
  - Genera infracción si el vehículo cruza con luz roja
  - Envía datos al backend Django

#### 4. **Backend Django**
- **Ubicación**: `backend-django/infractions/`
- **Modelo**: `Infraction` con tipo `red_light`
- **Severidad**: `high` (ya configurado)
- **Procesamiento**: Automático vía `InfractionService`

#### 5. **Frontend Dashboard**
- **Ubicación**: `frontend-dashboard/src/components/LocalWebcamDetection.tsx`
- **Características**:
  - Toggle para habilitar detección de semáforo
  - Configuración de línea de parada (coordenada Y)
  - Logs detallados en consola del navegador
  - Visualización de infracciones en tiempo real

---

## 🚀 Uso

### 1. Configuración en el Frontend

```typescript
// Al iniciar la webcam, habilita la detección de semáforo
const config = {
  enable_traffic_light: true,  // Activar detección
  stop_line_y: 400,             // Coordenada Y de la línea de parada
  traffic_light_roi: null,      // Opcional: [x1, y1, x2, y2] del semáforo
  infractions: ['red_light']    // Incluir en tipos de infracción
};
```

### 2. Parámetros de Configuración

| Parámetro | Tipo | Descripción | Default |
|-----------|------|-------------|---------|
| `enable_traffic_light` | boolean | Activar detección de semáforo | `false` |
| `stop_line_y` | number | Coordenada Y de línea de parada | - |
| `traffic_light_roi` | array | ROI del semáforo `[x1, y1, x2, y2]` | auto |
| `infractions` | array | Debe incluir `'red_light'` | `[]` |

### 3. Lógica de Detección

```python
# Pseudocódigo de la lógica
if traffic_light_state == 'red' and 'red_light' in config.infractions:
    vehicle_center_y = vehicle_bbox[1] + vehicle_bbox[3] / 2
    
    if vehicle_center_y > stop_line_y:
        # INFRACCIÓN DETECTADA
        create_infraction(
            type='red_light',
            vehicle=vehicle,
            metadata={
                'traffic_light_state': 'red',
                'stop_line_y': stop_line_y,
                'vehicle_position_y': vehicle_center_y
            }
        )
```

---

## 🔍 Detección del Estado del Semáforo

### Método: Análisis HSV

El detector utiliza rangos de color en espacio HSV para identificar el estado:

```python
# Rangos HSV
hsv_ranges = {
    'red': {
        'lower1': [0, 100, 100],    # Rojo bajo
        'upper1': [10, 255, 255],
        'lower2': [160, 100, 100],  # Rojo alto (wraparound)
        'upper2': [180, 255, 255]
    },
    'yellow': {
        'lower': [15, 100, 100],
        'upper': [35, 255, 255]
    },
    'green': {
        'lower': [40, 50, 50],
        'upper': [90, 255, 255]
    }
}
```

### Ventajas del Método HSV

✅ **No requiere modelo ML adicional** → Más rápido, menos recursos
✅ **Robusto a cambios de iluminación** → HSV separa color de intensidad
✅ **Baja latencia** → ~5-10ms por detección
✅ **Configurable** → Ajustar rangos según semáforos específicos

### Limitaciones

⚠️ **Requiere ROI del semáforo** → Debe estar en el campo visual
⚠️ **Sensible a oclusiones** → Objetos que tapen el semáforo
⚠️ **Calibración inicial** → Ajustar rangos HSV por entorno

---

## 📊 Estructura de Datos

### Infracción de Luz Roja

```json
{
  "infraction_code": "INF-20251104-0012",
  "infraction_type": "red_light",
  "severity": "high",
  "device": "CAM-001",
  "zone": "Main St & 5th Ave",
  "license_plate_detected": "ABC-1234",
  "license_plate_confidence": 0.89,
  "detected_speed": null,
  "speed_limit": null,
  "evidence_metadata": {
    "traffic_light_state": "red",
    "stop_line_y": 400,
    "vehicle_position_y": 450,
    "traffic_light_confidence": 0.85
  },
  "status": "pending",
  "detected_at": "2025-11-04T10:30:45Z"
}
```

---

## 🧪 Testing

### Script de Prueba

```bash
# Ejecutar pruebas de infracciones de luz roja
chmod +x test-red-light.sh
./test-red-light.sh
```

### Verificaciones

1. **Detección de estado**:
   - Abrir consola del navegador (F12)
   - Buscar logs: `🚦 Traffic light detected: red`

2. **Infracción generada**:
   - Log: `🚨 RED LIGHT VIOLATION: Vehicle crossed stop line`

3. **Almacenamiento en BD**:
   ```sql
   SELECT * FROM infractions_infraction 
   WHERE infraction_type = 'red_light' 
   ORDER BY detected_at DESC LIMIT 5;
   ```

4. **Frontend**:
   - Dashboard debe mostrar infracciones con borde rojo
   - Etiqueta: `⚠️ red_light`

---

## 🎯 Logs de Consola (Inspección)

### Frontend (Navegador - F12)

```javascript
// WebSocket recibe frame
📥 Received from server: {
  type: "frame",
  detectionCount: 3,
  infractions: 1,
  trafficLight: "red"
}

// Detecciones procesadas
🚗 Detections: [
  { type: "car", confidence: "0.89", hasInfraction: true, infractionType: "red_light" }
]

// Infracción detectada
🚨 INFRACTIONS DETECTED: 1
   Infraction #1: {
     type: "red_light",
     vehicle: "car",
     data: {
       traffic_light_state: "red",
       stop_line_y: 400,
       vehicle_position_y: 450
     }
   }
```

### Backend Inference (Terminal)

```
INFO: 🚦 Traffic light detected: red (confidence=0.85)
INFO: 🚨 RED LIGHT VIOLATION: Vehicle crossed stop line (line=400, vehicle=450)
INFO: ✅ Infraction registered with Django backend
```

### Backend Django (Terminal)

```python
INFO: Processing red_light infraction for vehicle CAR
INFO: Created infraction INF-20251104-0012 with severity=high
INFO: Vehicle ABC-1234 registered with infraction
```

---

## ⚙️ Configuración Avanzada

### Ajustar Detección de Color

Si el semáforo no se detecta correctamente:

```python
# En inference-service/app/services/traffic_light_detector.py
# Ajustar rangos HSV
self.hsv_ranges['red']['lower1'] = np.array([0, 80, 80])  # Más permisivo
self.hsv_ranges['red']['upper1'] = np.array([15, 255, 255])
```

### ROI Automático vs Manual

```python
# Automático (área superior central)
roi = None  # Usa (40%, 0, 60%, 30%) del frame

# Manual (coordenadas específicas)
roi = (500, 50, 600, 150)  # x1, y1, x2, y2 en píxeles
```

### Suavizado Temporal

```python
# Ajustar historial para estabilidad
self.max_history = 5  # Más frames = más estable pero menos responsive
```

---

## 🔮 Mejoras Futuras

### 1. Modelo YOLO Especializado
- Entrenar YOLOv8 para detectar semáforos
- Dataset: semáforos en diferentes ángulos/iluminación
- Ventaja: Detección robusta sin ROI manual

### 2. Integración con Controladores
- API directa con controladores de semáforo de la ciudad
- Estado en tiempo real sin análisis de imagen
- Mayor precisión y menor latencia

### 3. Predicción de Trayectoria
- Detectar intención de cruzar antes del cruce
- Alertas preventivas
- Reducir falsos positivos

### 4. Múltiples Semáforos
- Soportar intersecciones con varios semáforos
- Tracking de carril específico
- Asociar vehículo con semáforo correcto

---

## 📚 Referencias

### Archivos Relacionados

```
ml-service/
├── src/detection/traffic_light_detector.py  # Detector completo ML
└── tests/                                    # Tests unitarios

inference-service/
├── app/services/traffic_light_detector.py   # Detector simplificado
├── app/services/model_service.py            # Integración
└── app/api/websocket.py                     # WebSocket handler

backend-django/
├── infractions/models.py                    # Modelo Infraction
├── infractions/services.py                  # Procesamiento
└── infractions/serializers_detection.py     # Serialización

frontend-dashboard/
└── src/components/LocalWebcamDetection.tsx  # UI + controles

tests/
└── test-red-light.sh                        # Script de pruebas
```

### Documentación Adicional

- [`DETECCIONES_POR_TIPO.md`](./DETECCIONES_POR_TIPO.md): Sistema de almacenamiento
- [`RESUMEN_INFRACCIONES.md`](./RESUMEN_INFRACCIONES.md): Sistema completo de infracciones
- [`INFERENCE-SERVICE.md`](./INFERENCE-SERVICE.md): Detección en tiempo real

---

## 🆘 Troubleshooting

### Semáforo no detectado

```bash
# Verificar logs en consola
🚦 Traffic light detected: unknown (confidence=0.00)

# Solución:
1. Ajustar ROI del semáforo
2. Verificar iluminación
3. Revisar rangos HSV
```

### Infracciones no se guardan

```bash
# Verificar backend Django
curl http://localhost:8000/api/infractions/ | jq '.results[] | select(.infraction_type=="red_light")'

# Si no hay resultados:
1. Revisar logs de Django
2. Verificar configuración de zona
3. Ejecutar test-red-light.sh
```

### False Positives

```bash
# Vehículo detenido detectado como infracción

# Solución:
1. Ajustar stop_line_y más allá de la línea
2. Implementar tracking de movimiento
3. Verificar confidence threshold del semáforo
```

---

## ✅ Checklist de Implementación

- [x] TrafficLightDetector implementado (ML Service)
- [x] Detector simplificado para inference service
- [x] Integración en ModelService
- [x] Lógica de detección en WebSocket
- [x] Procesamiento en backend Django
- [x] Logs detallados en frontend y backend
- [x] Controles UI en frontend
- [x] Script de prueba (`test-red-light.sh`)
- [x] Documentación completa
- [ ] Modelo YOLO especializado (futuro)
- [ ] Integración con controladores (futuro)
- [ ] Tests unitarios completos

---

**Autor**: Sistema BAC - Traffic Infraction Detection System
**Fecha**: Noviembre 4, 2025
**Versión**: 1.0.0
