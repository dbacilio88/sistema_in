# ⚡ INICIALIZAR BASE DE DATOS - INSTRUCCIONES RÁPIDAS

## 🎯 El Problema

La base de datos está **VACÍA** por eso no se guardan las infracciones.

---

## ✅ SOLUCIÓN (3 minutos)

### Opción 1: Windows (PowerShell/CMD)

```cmd
REM 1. Abrir PowerShell o CMD en la raíz del proyecto
cd C:\ruta\a\sistema_in

REM 2. Ejecutar script de Windows
setup-database-windows.bat
```

### Opción 2: WSL/Linux/Mac (Terminal)

```bash
# 1. Abrir terminal en la raíz del proyecto
cd ~/github.com/sistema_in

# 2. Ejecutar script bash
chmod +x setup-database.sh
./setup-database.sh
```

### Opción 3: Python directo (Cualquier sistema)

```bash
# 1. Ir a backend-django
cd backend-django

# 2. Ejecutar script de inicialización
python init_database.py
```

---

## 📋 Qué hace el script

1. ✅ Verifica que PostgreSQL esté corriendo
2. ✅ Ejecuta migraciones (crea tablas)
3. ✅ Crea superusuario: `admin` / `admin123`
4. ✅ Crea zona y dispositivo de prueba
5. ✅ Configura tipos de infracciones

**Tiempo: ~30 segundos**

---

## 🧪 Verificar que Funcionó

### Test 1: Ver en Admin Panel

```
1. Abrir: http://localhost:8000/admin/
2. Login: admin / admin123
3. Ver sección "Infractions" → debería estar vacía pero lista
```

### Test 2: Probar API

```bash
# Crear infracción de prueba
curl -X POST http://localhost:8000/api/infractions/ \
  -H "Content-Type: application/json" \
  -d '{
    "infraction_type": "speed",
    "detected_at": "2025-11-04T10:00:00Z",
    "severity": "high",
    "status": "pending",
    "detected_speed": 95,
    "speed_limit": 60
  }'

# Si responde con JSON y código 201 → ¡Funciona!
```

### Test 3: Ver infracciones

```bash
curl http://localhost:8000/api/infractions/
```

---

## 🚀 Después de Inicializar

1. **Reiniciar Backend Django** (si estaba corriendo):
   ```bash
   cd backend-django
   python manage.py runserver
   ```

2. **Reiniciar Inference Service** (si estaba corriendo):
   ```bash
   cd inference-service
   uvicorn app.main:app --reload --port 8001
   ```

3. **Probar detección**:
   - Ir al dashboard
   - Activar detección con video o webcam
   - Abrir consola (F12)
   - Ver logs: `✅ Infraction created successfully`

---

## 🐛 Si algo falla

### PostgreSQL no inicia
```bash
docker-compose up -d postgres
# Esperar 10 segundos
docker ps | grep postgres
```

### Python no encontrado
```bash
# Verificar instalación
python --version
# o
python3 --version

# Instalar si falta
```

### Error de permisos en scripts
```bash
chmod +x setup-database.sh
chmod +x verify-database-connection.sh
```

---

## ✨ Resultado Final

Después de ejecutar el script verás:

```
==========================================
✅ INICIALIZACIÓN COMPLETA
==========================================

📊 Estadísticas:
  👥 Usuarios: 1
  📍 Zonas: 1
  📹 Dispositivos: 1
  🚗 Vehículos: 0
  🚨 Infracciones: 0

📋 Tipos de infracción disponibles:
  • speed        - Exceso de velocidad
  • red_light    - Cruce de semáforo en rojo
  • wrong_lane   - Invasión de carril
  • no_helmet    - Sin casco
  • parking      - Estacionamiento indebido
  • phone_use    - Uso de teléfono
  • seatbelt     - Sin cinturón
  • other        - Otras infracciones

✨ La base de datos está lista para usar
```

---

## 🎯 Comandos de Una Línea

### Inicialización completa:
```bash
cd backend-django && python init_database.py
```

### Verificación completa:
```bash
./verify-database-connection.sh
```

### Resetear todo (⚠️ CUIDADO - borra datos):
```bash
cd backend-django && python manage.py flush && python init_database.py
```

---

**¿Listo?** → Ejecuta uno de los scripts y tendrás la base de datos inicializada en 30 segundos! 🚀
