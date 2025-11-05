# Fix: Detección de Placas en Infracciones wrong_lane

## 🐛 Problema Identificado

La placa **B7J-482** no se estaba detectando en infracciones de `wrong_lane` porque:

1. ✅ El OCR **SÍ** se estaba ejecutando
2. ❌ El formato del `bbox` era incorrecto
3. ❌ Se enviaba array `[x, y, w, h]` pero OCR esperaba dict `{x, y, width, height}`

### Logs del Problema
```
🚨 LANE INVASION: car crossed center line
🚨 INFRACTION DETECTED: wrong_lane for car
🔤 Attempting OCR for wrong_lane infraction...
⚠️ Infraction wrong_lane detected but NO LICENSE PLATE found
```

## ✅ Solución Implementada

### 1. Detección de Infracciones del Frontend
Agregado soporte para infracciones detectadas en el cliente (ej: invasión de carril detectada por canvas del frontend):

```python
# PRIORIDAD 1: Verificar si el FRONTEND ya detectó una infracción
if vehicle.get('has_infraction') and vehicle.get('infraction_type'):
    infraction_type = vehicle.get('infraction_type')
    infraction_data = vehicle.get('infraction_data', {})
    logger.info(f"🎯 INFRACTION FROM FRONTEND: {infraction_type}")
```

### 2. Conversión de Formato de BBox para OCR
Agregada conversión automática de bbox array → dict:

```python
# Convertir bbox a formato dict si viene como array [x, y, w, h]
bbox = vehicle['bbox']
if isinstance(bbox, list):
    bbox_dict = {
        'x': int(bbox[0]),
        'y': int(bbox[1]),
        'width': int(bbox[2]),
        'height': int(bbox[3])
    }
```

### 3. Logs Detallados
Agregados logs extensos para debugging:

```
🎯 INFRACTION FROM FRONTEND: wrong_lane for car (client-side detection)
🔤 Attempting OCR for wrong_lane infraction...
   📦 Vehicle bbox format: [172, 121, 125, 110]
   📦 Converted bbox to dict: {'x': 172, 'y': 121, 'width': 125, 'height': 110}
📋 ✅ PLATE DETECTED: 'B7J-482' (confidence: 0.89)
🔍 Checking deduplication for plate: 'B7J-482'
✅ ✨ NEW UNIQUE INFRACTION REGISTERED: wrong_lane for plate 'B7J-482'
💾 ====== SAVING INFRACTIONS TO DATABASE ======
   ✅ SUCCESS - Infraction saved with code: INF-2024-000123
```

## 🎬 Cómo Probar

### Opción 1: Monitoreo en Tiempo Real

1. **Abrir terminal de monitoreo**:
   ```bash
   cd inference-service
   ./monitor_wrong_lane.sh
   ```

2. **Cargar video con placa B7J-482** en el frontend:
   - VIDEO2.mp4 (tiene la placa B7J-482)
   - Activar: "Lane Detection" ✅
   - Activar: "OCR" ✅

3. **Observar logs en tiempo real**:
   - `🎯 INFRACTION FROM FRONTEND` - Si el frontend detecta
   - `🚨 LANE INVASION` - Si el backend detecta
   - `📋 ✅ PLATE DETECTED: 'B7J-482'` - OCR exitoso
   - `✅ ✨ NEW UNIQUE INFRACTION` - Primera detección
   - `🚫 DUPLICATE DETECTED` - Detecciones posteriores rechazadas

### Opción 2: Verificar Base de Datos

```bash
cd inference-service
python3 check_plate_b7j482_db.py
```

Debe mostrar:
- ✅ **1 infracción única** para B7J-482
- Código: INF-2024-NNNNNN
- Tipo: wrong_lane
- Placa: B7J-482
- Metadata completa

### Opción 3: Test con Script

```bash
docker exec 83bc8d718fc7 python3 test_lane_invasion_ocr.py //app/test_videos/VIDEO2.mp4
```

Resultados esperados:
```
🚨 INVASIÓN DETECTADA (Frame 65)
   Vehículo: car
   📋 Placa: B7J-482 (conf: 0.64)
   ✅ NUEVA INFRACCIÓN REGISTRADA (#1)

🚨 INVASIÓN DETECTADA (Frame 145)
   📋 Placa: B7J-482 (conf: 0.89)
   ⏭️  DUPLICADO: Placa B7J-482 ya registrada
```

## 📊 Formato de Datos

### BBox Array → Dict Conversion

**Entrada (YOLO format)**:
```python
bbox = [172.3, 121.0, 125.3, 110.3]  # [x, y, width, height]
```

**Salida (OCR format)**:
```python
bbox_dict = {
    'x': 172,
    'y': 121,
    'width': 125,
    'height': 110
}
```

### Infracción Completa con Placa

```json
{
  "infraction_type": "wrong_lane",
  "license_plate_detected": "B7J-482",
  "license_plate_confidence": 0.89,
  "detected_at": "2025-11-05T06:50:10.738Z",
  "status": "pending",
  "severity": "medium",
  "evidence_metadata": {
    "vehicle_type": "car",
    "confidence": 0.87,
    "bbox": [172, 121, 125, 110],
    "subtype": "crossed_left_line",
    "lane_crossed": "left",
    "distance": 24.3
  }
}
```

## 🔍 Debugging

### Ver Conversión de BBox
```bash
docker logs -f 83bc8d718fc7 2>&1 | grep "Converted bbox"
```

### Ver Todas las Placas Detectadas
```bash
docker logs -f 83bc8d718fc7 2>&1 | grep "PLATE DETECTED"
```

### Ver Solo B7J-482
```bash
docker logs -f 83bc8d718fc7 2>&1 | grep -i "b7j"
```

### Ver Duplicados Rechazados
```bash
docker logs -f 83bc8d718fc7 2>&1 | grep "DUPLICATE DETECTED"
```

## ✅ Checklist de Validación

- [ ] OCR se ejecuta para infracciones wrong_lane
- [ ] BBox se convierte correctamente a formato dict
- [ ] Placa B7J-482 se detecta con confianza > 0.6
- [ ] Primera detección se marca como "NEW UNIQUE"
- [ ] Detecciones posteriores se rechazan como "DUPLICATE"
- [ ] Solo 1 registro en BD por placa (dentro de cooldown)
- [ ] Código de infracción generado (INF-YYYY-NNNNNN)
- [ ] Metadata completa en evidence_metadata

## 🎯 Próximos Pasos

1. **Probar en frontend** con VIDEO2.mp4
2. **Verificar logs** en tiempo real con monitor_wrong_lane.sh
3. **Confirmar BD** con check_plate_b7j482_db.py
4. **Ajustar cooldown** si es necesario (actualmente 90 frames = ~3 segundos)

## 📝 Notas Técnicas

- **Formato BBox**: YOLO retorna `[x, y, width, height]`, OCR espera dict
- **Cooldown**: 90 frames @ 30fps = 3 segundos
- **OCR Engine**: EasyOCR con inglés, CPU mode
- **Deduplicación**: Por license_plate, no por vehicle tracking ID
- **Fallback**: Si no hay placa, usa "UNKNOWN-{frame}" para deduplicación por frame
