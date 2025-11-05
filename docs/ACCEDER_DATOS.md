# 🌐 Cómo Acceder a los Datos en localhost:8000

## ❌ Problema

Cuando accedes a `http://localhost:8000` no ves datos.

## ✅ Solución

Necesitas acceder a las **URLs específicas** de la API:

---

## 📍 URLs Correctas

### 1. **Ver Estadísticas del Sistema**
```
http://localhost:8000/api/
```
Muestra:
- Cantidad de usuarios, zonas, dispositivos, vehículos e infracciones
- Lista de todos los endpoints disponibles

### 2. **Panel de Administración (Interfaz visual)**
```
http://localhost:8000/admin/
```
**Login:** `admin` / `admin123`

Aquí puedes ver, editar, crear y eliminar:
- Usuarios
- Zonas
- Dispositivos
- Vehículos
- Infracciones
- Notificaciones

### 3. **API REST - Zonas**
```
http://localhost:8000/api/devices/zones/
```
Lista todas las zonas registradas en formato JSON.

### 4. **API REST - Dispositivos (Cámaras)**
```
http://localhost:8000/api/devices/
```
Lista todos los dispositivos/cámaras registrados.

### 5. **API REST - Vehículos**
```
http://localhost:8000/api/vehicles/
```
Lista todos los vehículos registrados.

### 6. **API REST - Infracciones**
```
http://localhost:8000/api/infractions/
```
Lista todas las infracciones detectadas.

### 7. **Documentación Interactiva de la API**
```
http://localhost:8000/api/docs/
```
Interfaz Swagger UI para probar todos los endpoints.

```
http://localhost:8000/api/redoc/
```
Documentación alternativa con ReDoc.

---

## 🚀 Script para Ver Datos Rápidamente

Ejecuta este comando en WSL:

```bash
cd ~/github.com/sistema_in/backend-django
python3 show_data.py
```

Esto te mostrará:
- ✅ Cantidad de registros en cada tabla
- ✅ Listado de zonas, dispositivos, usuarios
- ✅ Todas las URLs para acceder a los datos
- ✅ Ejemplos de comandos curl

---

## 📊 Verificar Datos en la Base de Datos

### Desde Python:

```bash
cd ~/github.com/sistema_in/backend-django
python3 manage.py shell
```

Luego ejecuta:
```python
from devices.models import Zone, Device
from django.contrib.auth.models import User

# Ver zonas
print(f"Zonas: {Zone.objects.count()}")
for z in Zone.objects.all():
    print(f"  - {z.code}: {z.name}")

# Ver dispositivos
print(f"Dispositivos: {Device.objects.count()}")
for d in Device.objects.all():
    print(f"  - {d.code}: {d.name}")

# Ver usuarios
print(f"Usuarios: {User.objects.count()}")
for u in User.objects.all():
    print(f"  - {u.username}")

# Salir
exit()
```

### Desde curl:

```bash
# Ver estadísticas
curl http://localhost:8000/api/

# Ver zonas
curl http://localhost:8000/api/devices/zones/

# Ver dispositivos
curl http://localhost:8000/api/devices/

# Ver infracciones
curl http://localhost:8000/api/infractions/
```

---

## 🎯 Interfaz Visual (Panel Admin)

1. **Accede a:** http://localhost:8000/admin/

2. **Login:**
   - Usuario: `admin`
   - Contraseña: `admin123`

3. **Explora:**
   - **DEVICES** → Zones, Devices
   - **VEHICLES** → Vehicles, Drivers
   - **INFRACTIONS** → Infractions, Appeals
   - **AUTHENTICATION** → Users, Groups

4. **Aquí puedes:**
   - ✅ Ver todos los registros
   - ✅ Crear nuevos registros
   - ✅ Editar registros existentes
   - ✅ Eliminar registros
   - ✅ Filtrar y buscar

---

## 🔍 Ejemplo Completo

### 1. Verificar que el servidor está corriendo:

```bash
curl http://localhost:8000/health/
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "service": "django-admin",
  "version": "1.0.0"
}
```

### 2. Ver estadísticas del sistema:

```bash
curl http://localhost:8000/api/
```

**Respuesta esperada:**
```json
{
  "message": "Traffic Infraction Detection System API",
  "version": "1.0.0",
  "database_stats": {
    "users": 1,
    "zones": 1,
    "devices": 1,
    "vehicles": 0,
    "infractions": 0
  },
  "endpoints": {
    "admin": "/admin/",
    "api_docs": "/api/docs/",
    "devices": "/api/devices/",
    "zones": "/api/devices/zones/",
    "infractions": "/api/infractions/",
    "vehicles": "/api/vehicles/",
    "notifications": "/api/notifications/"
  }
}
```

### 3. Ver zonas registradas:

```bash
curl http://localhost:8000/api/devices/zones/
```

**Respuesta esperada:**
```json
[
  {
    "id": "abc123...",
    "code": "ZONE-001",
    "name": "Centro de Lima",
    "description": "Zona central de monitoreo",
    "speed_limit": 60,
    "is_active": true,
    "created_at": "2025-11-04T...",
    ...
  }
]
```

---

## 🐛 Si No Ves Datos

### Opción 1: Verificar con el script
```bash
cd ~/github.com/sistema_in/backend-django
python3 show_data.py
```

### Opción 2: Re-inicializar la base de datos
```bash
cd ~/github.com/sistema_in/backend-django
python3 init_database.py
```

### Opción 3: Verificar en el shell de Django
```bash
python3 manage.py shell -c "from devices.models import Zone; print(f'Zonas: {Zone.objects.count()}')"
```

### Opción 4: Acceder al Panel Admin
1. Ir a: http://localhost:8000/admin/
2. Login: admin / admin123
3. Click en "Zones" o "Devices"
4. Ver los registros

---

## 💡 Resumen Rápido

| Lo que quieres ver | URL |
|-------------------|-----|
| Estadísticas generales | http://localhost:8000/api/ |
| Panel visual (admin) | http://localhost:8000/admin/ |
| Zonas | http://localhost:8000/api/devices/zones/ |
| Dispositivos | http://localhost:8000/api/devices/ |
| Vehículos | http://localhost:8000/api/vehicles/ |
| Infracciones | http://localhost:8000/api/infractions/ |
| Documentación API | http://localhost:8000/api/docs/ |

**Recuerda:** `localhost:8000` solo (sin ruta) te redirige a `/api/`, que muestra las estadísticas y endpoints.

---

## 🆘 Comandos Útiles

```bash
# Ver datos con el script
python3 show_data.py

# Reinicializar base de datos
python3 init_database.py

# Verificar servidor corriendo
curl http://localhost:8000/health/

# Ver zonas desde terminal
curl http://localhost:8000/api/devices/zones/ | python3 -m json.tool

# Abrir shell de Django
python3 manage.py shell
```

---

**¿Sigues sin ver datos?** Comparte qué URL estás usando y qué ves en pantalla! 🚀
