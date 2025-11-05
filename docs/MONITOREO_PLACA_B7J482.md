# Guía de Monitoreo de Placa B7J-482

## 🎯 Objetivo
Monitorear y verificar que la placa **B7J-482** se detecte correctamente y se guarde como registro único en la base de datos.

## 📊 Logs Implementados

### 1. Logs de Detección de Infracción
Cuando se detecta una infracción, verás:
```
🚨 INFRACTION DETECTED: speed for car
   📍 Frame: 125, Vehicle Index: #2
   📦 BBox: [245, 156, 389, 245], Confidence: 0.87
```

### 2. Logs de OCR (Detección de Placa)
```
🔤 Attempting OCR for speed infraction...
📋 ✅ PLATE DETECTED: 'B7J-482' (confidence: 0.89)
```

### 3. Logs de Deduplicación
#### Primera detección (Nueva):
```
🔍 Checking deduplication for plate: 'B7J-482'
📊 Currently tracking 0 plates in cooldown:
✅ ✨ NEW UNIQUE INFRACTION REGISTERED: speed for plate 'B7J-482' 
   (frame 125). Will be saved to database.
```

#### Detección duplicada (Rechazada):
```
🔍 Checking deduplication for plate: 'B7J-482'
📊 Currently tracking 1 plates in cooldown:
   - 'B7J-482': speed (45 frames ago)
⏭️  🚫 DUPLICATE DETECTED: Plate 'B7J-482' already has speed infraction 
   from 45 frames ago (cooldown: 90 frames). SKIPPING SAVE.
```

### 4. Logs de Guardado en Base de Datos
```
💾 ====== SAVING INFRACTIONS TO DATABASE ======
💾 Total infractions to save: 1
   1. speed - Plate: 'B7J-482' - Vehicle: car

💾 [1/1] Saving to database...
   📋 Plate: 'B7J-482', Type: speed
   ✅ SUCCESS - Infraction saved with code: INF-2024-000123
      ID: 123, Status: pending

💾 ====== DATABASE SAVE COMPLETE ======
💾 Total saved: 1/1

💾 📊 Summary of saved infractions:
   1. Code: INF-2024-000123 | Type: speed | Plate: 'B7J-482' | Speed: 85.3 km/h
```

## 🛠️ Herramientas de Monitoreo

### Opción 1: Script de Monitoreo en Tiempo Real
Monitorea los logs del contenedor filtrando solo información relevante para B7J-482:

```bash
cd inference-service
./monitor_plate_b7j482.sh
```

Esto mostrará en tiempo real:
- ✅ Detección de placa B7J-482
- 🚨 Infracciones detectadas
- 🚫 Duplicados rechazados
- 💾 Guardado en base de datos
- ✅ Códigos de infracción generados

### Opción 2: Verificar Base de Datos
Consulta directamente la BD para ver las infracciones guardadas:

```bash
cd inference-service
python3 check_plate_b7j482_db.py
```

Esto mostrará:
- Total de infracciones en BD
- Infracciones específicas para B7J-482
- Detalles completos (código, tipo, fecha, velocidad, metadata)
- Comparación con otras placas detectadas

### Opción 3: Logs Completos del Contenedor
Ver todos los logs (sin filtro):

```bash
docker logs -f 83bc8d718fc7
```

### Opción 4: Logs con Grep Manual
Filtrar logs específicos:

```bash
# Solo placas detectadas
docker logs -f 83bc8d718fc7 2>&1 | grep "PLATE DETECTED"

# Solo infracciones únicas registradas
docker logs -f 83bc8d718fc7 2>&1 | grep "NEW UNIQUE INFRACTION"

# Solo duplicados rechazados
docker logs -f 83bc8d718fc7 2>&1 | grep "DUPLICATE DETECTED"

# Solo guardado en BD
docker logs -f 83bc8d718fc7 2>&1 | grep "database save"
```

## 🎬 Flujo de Prueba Completo

### Paso 1: Iniciar Monitoreo
En una terminal:
```bash
cd inference-service
./monitor_plate_b7j482.sh
```

### Paso 2: Cargar Video con Placa B7J-482
En el frontend:
1. Ir a `http://localhost:3000/local-detection`
2. Cargar VIDEO2.mp4 (tiene la placa B7J-482)
3. Activar detección de velocidad
4. Observar logs en tiempo real

### Paso 3: Verificar Deduplicación
Observa que:
- **Primera detección**: Se muestra "NEW UNIQUE INFRACTION" y se guarda
- **Detecciones posteriores**: Se muestran como "DUPLICATE DETECTED" y NO se guardan
- **Cooldown**: Después de 90 frames (~3 segundos), la placa se limpia del tracking

### Paso 4: Verificar Base de Datos
```bash
python3 check_plate_b7j482_db.py
```

Debe mostrar:
- ✅ **1 infracción única** para B7J-482 (no múltiples)
- Código de infracción (ej: INF-2024-000123)
- Tipo de infracción (speed, red_light, etc)
- Metadata completa (velocidad, bbox, timestamp)

## 🔍 Qué Buscar en los Logs

### ✅ Comportamiento Correcto
1. **Primera detección**:
   - `PLATE DETECTED: 'B7J-482'`
   - `NEW UNIQUE INFRACTION REGISTERED`
   - `SUCCESS - Infraction saved`
   - **1 registro en BD**

2. **Detecciones subsecuentes** (mismo vehículo):
   - `PLATE DETECTED: 'B7J-482'`
   - `DUPLICATE DETECTED`
   - `SKIPPING SAVE`
   - **NO se crea nuevo registro**

3. **Después del cooldown** (90 frames):
   - Placa se limpia: `Removed expired plate from cooldown: B7J-482`
   - Nueva detección se permite

### ❌ Problemas Potenciales
1. **Múltiples registros de la misma placa**:
   - Verificar que el cooldown (90 frames) sea suficiente
   - Confirmar que `infraction_plates` dict se está actualizando

2. **Placa no detectada**:
   - Ver logs de OCR: `OCR failed`
   - Revisar calidad del frame/bbox
   - Considerar preprocesamiento de imagen

3. **No se guarda en BD**:
   - Verificar conexión con Django backend
   - Revisar logs de `_save_infractions_to_database`
   - Confirmar que Django está corriendo en puerto 8000

## 📈 Métricas de Éxito
- ✅ OCR detecta "B7J-482" con confianza > 0.6
- ✅ Primera detección se marca como "NEW UNIQUE"
- ✅ Detecciones subsecuentes se marcan como "DUPLICATE"
- ✅ Solo 1 registro en BD por vehículo (dentro del cooldown)
- ✅ Código de infracción generado (INF-YYYY-NNNNNN)
- ✅ Metadata completa guardada (vehicle_type, bbox, timestamp)

## 🐛 Debug Tips
1. **Ver estado del tracking en tiempo real**:
   ```bash
   docker logs -f 83bc8d718fc7 2>&1 | grep "Currently tracking"
   ```

2. **Contar infracciones guardadas**:
   ```bash
   docker logs 83bc8d718fc7 2>&1 | grep "SUCCESS - Infraction saved" | wc -l
   ```

3. **Ver todos los códigos generados**:
   ```bash
   docker logs 83bc8d718fc7 2>&1 | grep "Code:" | tail -20
   ```

4. **Verificar limpieza de cooldown**:
   ```bash
   docker logs 83bc8d718fc7 2>&1 | grep "Removed expired plate"
   ```

## 📝 Notas Importantes
- **Cooldown**: 90 frames = ~3 segundos @ 30fps
- **Formato de placa**: El sistema acepta "B7J-482", "B7J482", "B7J 482"
- **Sin placa**: Si no se detecta placa, se guarda como "UNKNOWN-{frame}"
- **Deduplicación**: Se basa en la placa, no en el vehículo (tracking ID)
