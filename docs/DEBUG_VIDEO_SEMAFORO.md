# 🎥 Guía de Detección con Video de Semáforo en Rojo

## ✅ Cambios Realizados

### 1. **Video ya NO se reinicia automáticamente**
- ❌ Antes: `video.loop = true` (reiniciaba constantemente)
- ✅ Ahora: `video.loop = false` (se detiene al terminar)
- ➕ Agregado: Botón "🔄 Reiniciar Video" para reiniciar manualmente

### 2. **Mejorada la detección de semáforo**
- ✅ Umbral de confianza reducido: `0.3` (antes era `0.5`)
- ✅ YOLO confidence threshold: `0.25` (detecta semáforos con menor certeza)
- ✅ Solo habilita detecciones basadas en toggles activados
- ✅ Logs mejorados para debugging

---

## 📋 Pasos para Probar la Detección de Semáforo en Rojo

### 1. **Asegúrate de que los servicios estén corriendo:**

#### Terminal 1 - Backend Django:
```bash
cd ~/github.com/sistema_in/backend-django
python3 manage.py runserver
```

#### Terminal 2 - Inference Service:
```bash
cd ~/github.com/sistema_in/inference-service
python3 -m uvicorn app.main:app --reload --port 8001
```

#### Terminal 3 - Frontend:
```bash
cd ~/github.com/sistema_in/frontend-dashboard
npm run dev
```

### 2. **Accede al Dashboard:**
```
http://localhost:3002
```

### 3. **Configura la Detección:**

1. ✅ Activa el toggle **"🚦 Detección de Semáforo"**
2. ❌ Desactiva **"Simular Infracciones"** (para pruebas reales)
3. ✅ Selecciona **"🎬 Archivo de Video"** (no webcam)
4. 📁 Click en **"Seleccionar Video"** y elige tu video de semáforo
5. 🎯 Click en **"Iniciar Detección"**

### 4. **Observa la Consola del Navegador (F12):**

Deberías ver logs como:

```javascript
// Cuando detecta el semáforo:
🚦 Traffic Light: 🔴 RED (conf: 0.85, detections: 2)

// Cuando detecta vehículo en rojo:
🚨 INFRACTIONS DETECTED: 1
   Infraction #1: {
     "type": "red_light",
     "vehicle": "car",
     "confidence": "0.87",
     ...
   }

✅ Infraction created successfully: code=INF-20251104-0001
```

---

## 🐛 Troubleshooting - Si No Detecta el Semáforo

### Problema 1: No ve ningún semáforo

**Síntoma:**
```
🚦 Traffic Light: ⚪ NO DETECTED (enabled but not found in frame)
```

**Soluciones:**

1. **Verifica que el video tiene un semáforo visible:**
   - El semáforo debe estar claro en el frame
   - No debe estar muy pequeño (mínimo 40x40 píxeles)
   - No debe estar muy borroso

2. **Reduce aún más el umbral de confianza:**

   En `frontend-dashboard/src/components/LocalWebcamDetection.tsx` línea ~420:
   ```typescript
   confidence_threshold: 0.2, // ✅ Más bajo = detecta más
   yolo_confidence_threshold: 0.15 // ✅ Más bajo = detecta más
   ```

3. **Verifica el modelo YOLO en el inference service:**

   ```bash
   cd ~/github.com/sistema_in/inference-service
   python3 -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt'); print('Clases:', model.names); print('Semáforo:', model.names.get(9))"
   ```

   Debe mostrar:
   ```
   Clases: {0: 'person', ..., 9: 'traffic light', ...}
   Semáforo: traffic light
   ```

### Problema 2: Detecta semáforo pero no el color rojo

**Síntoma:**
```
🚦 Traffic Light: ⚪ UNKNOWN (conf: 0.85, detections: 1)
```

**Soluciones:**

1. **Verifica el rango HSV en el traffic light detector:**

   Archivo: `inference-service/app/services/traffic_light_detector.py`

   Verifica que los rangos HSV sean correctos:
   ```python
   # Rojo (dos rangos porque está en los extremos del espectro)
   lower_red1 = np.array([0, 120, 70])    # H: 0-10
   upper_red1 = np.array([10, 255, 255])
   
   lower_red2 = np.array([170, 120, 70])  # H: 170-180
   upper_red2 = np.array([180, 255, 255])
   ```

2. **Prueba con una imagen estática:**

   Crea un script de prueba:
   ```python
   # test_traffic_light.py
   import cv2
   import numpy as np
   
   # Cargar frame del video
   cap = cv2.VideoCapture('tu_video.mp4')
   ret, frame = cap.read()
   
   # Extraer región donde está el semáforo (ajusta coordenadas)
   roi = frame[100:200, 300:400]  # y1:y2, x1:x2
   
   # Convertir a HSV
   hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
   
   # Detectar rojo
   lower_red1 = np.array([0, 120, 70])
   upper_red1 = np.array([10, 255, 255])
   mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
   
   lower_red2 = np.array([170, 120, 70])
   upper_red2 = np.array([180, 255, 255])
   mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
   
   mask = cv2.bitwise_or(mask1, mask2)
   red_pixels = cv2.countNonZero(mask)
   
   print(f"Píxeles rojos: {red_pixels}")
   print(f"Total píxeles: {roi.shape[0] * roi.shape[1]}")
   print(f"Porcentaje rojo: {red_pixels / (roi.shape[0] * roi.shape[1]) * 100:.2f}%")
   ```

### Problema 3: Detecta semáforo pero no registra la infracción

**Síntoma:**
```
🚦 Traffic Light: 🔴 RED (conf: 0.85, detections: 2)
🚗 Detections: [{type: 'car', confidence: 0.87, ...}]
// ❌ Pero NO muestra: 🚨 INFRACTIONS DETECTED
```

**Soluciones:**

1. **Verifica que hay un vehículo detectado:**
   - Debe haber al menos un vehículo en el frame
   - El vehículo debe estar DESPUÉS de la línea de parada (`stop_line_y`)

2. **Ajusta la línea de parada:**
   
   En el frontend, ajusta el valor de `Stop Line Y` (posición vertical):
   - Valores más bajos = línea más arriba en la imagen
   - Valores más altos = línea más abajo en la imagen
   - El vehículo debe estar ABAJO de esta línea cuando el semáforo esté rojo

3. **Verifica la lógica de detección:**

   Archivo: `inference-service/app/services/model_service.py`

   Busca la función que detecta infracciones de semáforo:
   ```python
   async def detect_red_light_violation(self, ...):
       # Debe verificar:
       # 1. Semáforo en rojo (traffic_light_state == 'red')
       # 2. Vehículo detectado
       # 3. Vehículo DESPUÉS de stop_line_y
   ```

### Problema 4: Se reinicia constantemente

**Ya CORREGIDO**, pero si persiste:

1. **Verifica que el cambio se aplicó:**
   ```typescript
   video.loop = false; // ✅ Debe ser false
   ```

2. **Limpia el caché del navegador:**
   - Ctrl + Shift + R (recarga forzada)
   - O abre en ventana privada/incógnito

3. **Verifica que no hay múltiples useEffect conflictivos:**
   - Busca `useEffect` que contenga `videoUrl` o `videoFile`
   - Asegúrate de que no limpia el video constantemente

---

## 📊 Verificar Infracciones en la Base de Datos

Después de detectar infracciones:

### Opción 1: Panel Admin
```
http://localhost:8000/admin/
Login: admin / admin123
```
Ve a **INFRACTIONS → Infractions**

### Opción 2: API REST
```bash
curl http://localhost:8000/api/infractions/
```

### Opción 3: Script de verificación
```bash
cd ~/github.com/sistema_in/backend-django
python3 -c "from infractions.models import Infraction; print(f'Total: {Infraction.objects.count()}'); [print(f'{i.infraction_code}: {i.infraction_type}') for i in Infraction.objects.all()[:5]]"
```

---

## 💡 Consejos para Mejor Detección

### 1. **Calidad del Video:**
- ✅ Resolución mínima: 720p (1280x720)
- ✅ Semáforo visible y enfocado
- ✅ Buena iluminación
- ✅ Semáforo NO demasiado lejos (mínimo 40x40 píxeles)

### 2. **Configuración Óptima:**
```typescript
confidence_threshold: 0.3,           // Detección general
yolo_confidence_threshold: 0.25,     // Detección de semáforo
stop_line_y: 400,                    // Ajustar según video
```

### 3. **Debugging en Tiempo Real:**

Abre la consola del navegador (F12) y filtra por:
- `🚦` para logs de semáforo
- `🚨` para logs de infracciones
- `❌` para errores

### 4. **Orden de Verificación:**
1. ✅ Servicios corriendo (backend, inference, frontend)
2. ✅ Toggle "Detección de Semáforo" activado
3. ✅ Video cargado y reproduciéndose
4. ✅ Logs en consola mostrando frames enviados
5. ✅ Detección de semáforo en logs: `🚦 Traffic Light: 🔴 RED`
6. ✅ Detección de vehículo: `🚗 Detections: [...]`
7. ✅ Infracción registrada: `🚨 INFRACTIONS DETECTED`
8. ✅ Guardado en BD: `✅ Infraction created successfully`

---

## 🆘 Si Nada Funciona

1. **Reinicia todos los servicios:**
   ```bash
   # Detener todo (Ctrl + C en cada terminal)
   
   # Reiniciar backend
   cd ~/github.com/sistema_in/backend-django
   python3 manage.py runserver
   
   # Reiniciar inference (nueva terminal)
   cd ~/github.com/sistema_in/inference-service
   python3 -m uvicorn app.main:app --reload --port 8001
   
   # Reiniciar frontend (nueva terminal)
   cd ~/github.com/sistema_in/frontend-dashboard
   npm run dev
   ```

2. **Verifica las conexiones:**
   ```bash
   # Backend
   curl http://localhost:8000/health/
   
   # Inference
   curl http://localhost:8001/health
   
   # Frontend
   curl http://localhost:3002
   ```

3. **Comparte los logs:**
   - Logs de la consola del navegador (F12)
   - Logs del terminal del inference service
   - Descripción del video (resolución, duración, tipo de semáforo)

---

**¿Sigue sin funcionar?** Comparte:
1. Logs de la consola (F12) con filtro "🚦"
2. Captura del video (frame donde está el semáforo)
3. Configuración actual (toggles activados)

¡Te ayudaré a resolverlo! 🚀
