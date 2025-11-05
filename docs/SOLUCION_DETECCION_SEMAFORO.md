# 🎉 Solución: Detección de Semáforos

## ✅ Diagnóstico Completado

### Resultados del Test:
- **✅ YOLO SÍ detecta semáforos**: 130 detecciones en 19 frames
- **✅ Tamaño promedio**: 1102 px² (≈ 33x33 píxeles) - Suficiente
- **⚠️ Problema**: Confianza promedio 38.2% (muchos < 30%)

### Clases Detectadas en tu Video:
1. **persons** (295): 👥 Personas
2. **car** (289): 🚗 Autos
3. **traffic light** (130): 🚦 **Semáforos detectados!**
4. **truck** (7): 🚚 Camiones
5. **handbag** (5): 👜 Carteras
6. **umbrella** (3): ☂️ Paraguas

---

## 🛠️ Cambios Aplicados

### 1. Umbrales Reducidos

#### `traffic_light_detector.py`:
```python
# Antes
yolo_confidence_threshold = 0.2
min_color_percentage = 5.0
hsv_ranges['red']['lower1'] = [0, 100, 50]

# Ahora
yolo_confidence_threshold = 0.15  # ✅ Detecta desde 16% (tu video)
min_color_percentage = 3.0        # ✅ Menos estricto
hsv_ranges['red']['lower1'] = [0, 80, 40]  # ✅ Detecta rojos oscuros
```

#### `LocalWebcamDetection.tsx`:
```typescript
// Antes
confidence_threshold: 0.3
yolo_confidence_threshold: 0.25

// Ahora
confidence_threshold: 0.2         // ✅ Acepta detecciones > 20%
yolo_confidence_threshold: 0.15   // ✅ Acepta detecciones > 15%
```

### 2. Rangos HSV Más Permisivos

```python
'red': {
    'lower1': [0, 80, 40],      # Detecta rojos oscuros/apagados
    'upper1': [10, 255, 255],
    'lower2': [160, 80, 40],    # Rango amplio
    'upper2': [180, 255, 255]
},
'yellow': {
    'lower': [15, 60, 60],      # Más permisivo
    'upper': [45, 255, 255]
},
'green': {
    'lower': [40, 50, 40],      # Más permisivo
    'upper': [95, 255, 255]
}
```

### 3. Logs Mejorados

Ahora muestra:
- Todas las clases detectadas por YOLO
- Scores de color (red, yellow, green) para cada semáforo
- Tamaño de cada detección en píxeles
- Razones por las que se filtran detecciones

### 4. Optimización de Rendimiento

```typescript
skipFrames: 5              // Procesa 1 de cada 6 frames (antes 1 de cada 3)
scale: 0.4                 // 40% resolución (antes 50%)
jpeg_quality: 0.5          // Calidad 50% (antes 60%)
```

**Resultado esperado**: 12-20 FPS (antes 5-7 FPS)

---

## 🚀 Cómo Probar Ahora

### Paso 1: Reiniciar Servicios

```bash
# Terminal 1: Backend Django
cd ~/github.com/sistema_in/backend-django
python3 manage.py runserver

# Terminal 2: Inference Service (reiniciar Docker o local)
docker restart 83bc8d718fc7

# O si corre local:
cd ~/github.com/sistema_in/inference-service
python3 -m uvicorn app.main:app --reload --port 8001

# Terminal 3: Frontend
cd ~/github.com/sistema_in/frontend-dashboard
npm run dev
```

### Paso 2: Configuración en el Dashboard

1. Accede a: http://localhost:3002
2. Configura:
   - ✅ **"🎬 Archivo de Video"**
   - ✅ **"🚦 Detección Semáforo"** activado
   - ❌ **"Simular Infracciones"** desactivado
   - Límite velocidad: 60 km/h
   - Stop Line Y: 300-400 (ajustar según video)
3. Selecciona tu `VIDEO1.mp4`
4. Click **"Iniciar Detección"**

### Paso 3: Monitorear Consola (F12)

Busca logs como:

```javascript
// Detección YOLO
🔍 YOLO detected classes in frame: car(15), person(8), traffic light(7)

// Scores de color
Color scores for 44x125 ROI: red=0.245, yellow=0.031, green=0.018

// Detección de semáforo
🚦 Traffic Light: 🔴 RED (conf: 0.75, detections: 3)

// Detección de vehículo
🚗 Detections: [{type: 'car', confidence: 0.87, hasInfraction: false}]

// Infracción!
🚨 INFRACTIONS DETECTED: 1
   Infraction #1: {
     "type": "red_light",
     "vehicle": "car",
     "confidence": "0.87",
     ...
   }

✅ Infraction created successfully: code=INF-20251105-0001
```

---

## 📊 Qué Esperar

### Con estos cambios:

#### ✅ Mejoras:
1. **Más detecciones**: Acepta semáforos con confianza > 15%
2. **Mejor HSV**: Detecta rojos oscuros/apagados
3. **FPS mejorados**: 12-20 FPS (2-3x más rápido)
4. **Logs detallados**: Puedes ver exactamente qué detecta

#### ⚠️ Posibles Problemas que AÚN pueden ocurrir:

1. **No detecta el COLOR rojo**:
   - Aunque YOLO detecta el semáforo
   - El análisis HSV no encuentra suficientes píxeles rojos
   - Solución: Ajustar rangos HSV o usar ROI más enfocada

2. **Semáforo detectado pero sin vehículo**:
   - Semáforo en rojo pero no hay autos cerca
   - O el auto está ANTES de la línea de parada (stop_line_y)
   - Solución: Ajustar `stop_line_y` en el dashboard

3. **FPS aún bajos**:
   - Hardware lento
   - Solución: Reducir más la resolución o procesar menos frames

---

## 🐛 Troubleshooting

### Problema 1: Detecta semáforo pero no el color

**Síntoma:**
```
🚦 Traffic Light: ⚪ UNKNOWN (conf: 0.00, detections: 3)
```

**Solución:**
1. Verifica los logs de scores:
   ```
   Color scores for 44x125 ROI: red=0.015, yellow=0.008, green=0.005
   ```
   
2. Si todos los scores son < 0.03, el semáforo está:
   - Muy oscuro/apagado
   - Borroso
   - Demasiado pequeño para análisis HSV
   
3. **Aumenta el brillo del video** o **reduce umbral HSV** aún más:
   ```python
   # En traffic_light_detector.py
   if max_score < 0.01:  # Reducir de 0.03 a 0.01
   ```

### Problema 2: Detecta verde/amarillo en lugar de rojo

**Síntoma:**
```
🚦 Traffic Light: 🟢 GREEN (conf: 0.65, detections: 1)
```

**Solución:**
Ajusta los rangos HSV en `traffic_light_detector.py`:
```python
# Hacer rojo más dominante
'red': {
    'lower1': [0, 70, 30],     # Aún más permisivo
    'upper1': [12, 255, 255],  # Rango más amplio
    'lower2': [155, 70, 30],   # Rango más amplio
    'upper2': [180, 255, 255]
}
```

### Problema 3: FPS siguen bajos (< 10)

**Solución:**
```typescript
// En LocalWebcamDetection.tsx

// Procesar menos frames
skipFramesRef.current < 8  // 1 de cada 9 frames

// Menor resolución
const scale = 0.3;  // 30% en lugar de 40%

// Menor calidad
const imageData = tempCanvas.toDataURL('image/jpeg', 0.4);
```

### Problema 4: Muchos falsos positivos

**Síntoma:**
```
🚦 Traffic Light: 🔴 RED cuando realmente es verde/apagado
```

**Solución:**
```python
# Aumentar umbrales
yolo_confidence_threshold = 0.25  # De 0.15 a 0.25
min_color_percentage = 5.0        # De 3.0 a 5.0
```

---

## 📝 Siguiente Paso: Prueba Real

### 1. Reinicia todo:
```bash
# Docker inference service
docker restart 83bc8d718fc7

# O local
cd ~/github.com/sistema_in/inference-service
# Ctrl+C para detener
python3 -m uvicorn app.main:app --reload --port 8001

# Frontend
cd ~/github.com/sistema_in/frontend-dashboard
# Ctrl+C para detener
npm run dev
```

### 2. Abre el dashboard y prueba

### 3. Comparte:
- ✅ Logs de la consola del navegador (F12)
- ✅ FPS que obtienes ahora
- ✅ Si detecta el semáforo en rojo
- ✅ Si registra las infracciones

---

## 💡 Tips Adicionales

### Para mejor detección:
1. **Videos con buena iluminación** (día)
2. **Semáforos grandes** en la imagen (> 40x40 px)
3. **Semáforos enfocados** (no borrosos)
4. **Colores saturados** (no apagados)

### Para mejor rendimiento:
1. **Hardware**: GPU mejora mucho YOLO
2. **Resolución baja**: 640x360 es suficiente
3. **Menos frames**: 1 de cada 10 frames sigue siendo útil

### Alternativa - ROI Manual:
Si YOLO no funciona bien, puedo implementar que tú definas manualmente dónde está el semáforo:
```typescript
trafficLightROI: { x: 200, y: 20, width: 50, height: 130 }
```

---

**¿Probaste con los nuevos cambios? ¿Qué resultado obtienes ahora?** 🚀
