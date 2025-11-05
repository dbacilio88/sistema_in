# 🚀 Guía Rápida: Inicializar Base de Datos

## ❌ Problema Identificado

La base de datos está **vacía** y no tiene:
- ❌ Tablas creadas (migraciones no ejecutadas)
- ❌ Usuarios del sistema
- ❌ Zonas y dispositivos
- ❌ Tipos de infracciones configurados

Por eso las infracciones detectadas **no se guardan**.

---

## ✅ Solución en 3 Pasos

### Paso 1: Verificar PostgreSQL

```bash
# Verificar que PostgreSQL está corriendo
docker ps | grep postgres

# Si no está corriendo:
docker-compose up -d postgres

# O iniciar todo el stack:
docker-compose up -d
```

### Paso 2: Ejecutar Script de Inicialización

#### Opción A - Script Python (Recomendado):

```bash
cd backend-django
python init_database.py
```

#### Opción B - Comandos manuales:

```bash
cd backend-django

# 1. Ejecutar migraciones
python manage.py migrate

# 2. Crear superusuario
python manage.py createsuperuser
# Username: admin
# Email: admin@traffic.pe
# Password: admin123

# 3. Cargar datos semilla (opcional)
python seed_data.py
```

#### Opción C - Script Bash:

```bash
chmod +x setup-database.sh
./setup-database.sh
```

### Paso 3: Verificar Base de Datos

```bash
cd backend-django

# Verificar con Django shell
python manage.py shell

>>> from infractions.models import Infraction
>>> from devices.models import Device, Zone
>>> from django.contrib.auth import get_user_model
>>> 
>>> User = get_user_model()
>>> print(f"Usuarios: {User.objects.count()}")
>>> print(f"Zonas: {Zone.objects.count()}")
>>> print(f"Dispositivos: {Device.objects.count()}")
>>> print(f"Infracciones: {Infraction.objects.count()}")
>>> 
>>> exit()
```

---

## 🎯 Verificación Rápida

### Test 1: Crear infracción desde API

```bash
curl -X POST http://localhost:8000/api/infractions/ \
  -H "Content-Type: application/json" \
  -d '{
    "infraction_type": "speed",
    "detected_at": "2025-11-04T10:00:00Z",
    "severity": "high",
    "status": "pending",
    "license_plate_detected": "ABC-123",
    "detected_speed": 95.0,
    "speed_limit": 60
  }'
```

**Resultado esperado:**
```json
{
  "id": 1,
  "infraction_code": "INF-20251104-0001",
  "infraction_type": "speed",
  "severity": "high",
  ...
}
```

### Test 2: Listar infracciones

```bash
curl http://localhost:8000/api/infractions/
```

---

## 📋 Tipos de Infracciones Disponibles

Una vez inicializada la BD, estos son los tipos de infracciones que el sistema acepta:

| Código | Descripción | Severidad Recomendada |
|--------|-------------|----------------------|
| `speed` | Exceso de velocidad | `medium` / `high` |
| `red_light` | Cruce de semáforo en rojo | `high` / `critical` |
| `wrong_lane` | Invasión de carril | `medium` / `high` |
| `no_helmet` | Sin casco (motocicletas) | `medium` |
| `parking` | Estacionamiento indebido | `low` / `medium` |
| `phone_use` | Uso de teléfono al conducir | `medium` |
| `seatbelt` | Sin cinturón de seguridad | `medium` |
| `other` | Otras infracciones | `low` |

---

## 🔧 Comandos Útiles

### Resetear Base de Datos (⚠️ CUIDADO)

```bash
cd backend-django

# Eliminar todas las tablas
python manage.py flush --noinput

# Re-ejecutar migraciones
python manage.py migrate

# Re-cargar datos
python init_database.py
```

### Ver Esquema de Base de Datos

```bash
cd backend-django
python manage.py dbshell

# Dentro de psql:
\dt                           # Listar tablas
\d infractions_infraction     # Describir tabla de infracciones
SELECT COUNT(*) FROM infractions_infraction;  # Contar infracciones
\q                           # Salir
```

### Crear Migraciones (después de modificar models.py)

```bash
cd backend-django
python manage.py makemigrations
python manage.py migrate
```

---

## 📊 Estructura de la Base de Datos

Después de la inicialización, tendrás estas tablas:

```
infractions_infraction        # Infracciones detectadas
devices_device               # Cámaras y dispositivos
devices_zone                 # Zonas de monitoreo
vehicles_vehicle             # Vehículos registrados
authentication_customuser    # Usuarios del sistema
```

---

## 🐛 Troubleshooting

### Error: "No such table"

```
django.db.utils.OperationalError: no such table: infractions_infraction
```

**Solución**: Ejecutar migraciones
```bash
python manage.py migrate
```

### Error: "Could not connect to server"

```
django.db.utils.OperationalError: could not connect to server
```

**Solución**: Iniciar PostgreSQL
```bash
docker-compose up -d postgres
```

### Error: "DETAIL: Key (infraction_type)=(...) is not present"

```
IntegrityError: DETAIL: Key (infraction_type)=('speed') is not present in table "infractions_infractiontype"
```

**Causa**: Modelo antiguo con FK a tabla de tipos

**Solución**: Verificar que `infraction_type` sea un CharField en el modelo:
```python
# infractions/models.py
infraction_type = models.CharField(
    max_length=50,
    choices=[
        ('speed', 'Exceso de velocidad'),
        ('red_light', 'Semáforo en rojo'),
        ...
    ]
)
```

---

## ✅ Checklist Post-Inicialización

Después de ejecutar la inicialización, verifica:

- [ ] Migraciones ejecutadas: `python manage.py showmigrations`
- [ ] Superusuario creado: Login en http://localhost:8000/admin/
- [ ] Tablas creadas: Al menos 10+ tablas en la BD
- [ ] Tipos de infracciones disponibles (ver lista arriba)
- [ ] API responde: `curl http://localhost:8000/api/infractions/`
- [ ] Se pueden crear infracciones desde la API
- [ ] Las infracciones se muestran en el admin panel

---

## 🎓 Próximos Pasos

1. ✅ Inicializar base de datos (este documento)
2. 🔄 Reiniciar inference service (leerá nueva configuración)
3. 🎬 Probar detección con video o webcam
4. 📊 Ver infracciones en http://localhost:8000/admin/

---

## 📞 Comandos de Referencia Rápida

```bash
# Inicializar base de datos
cd backend-django && python init_database.py

# Verificar estado
python manage.py showmigrations

# Ver en admin panel
# URL: http://localhost:8000/admin/
# User: admin
# Pass: admin123

# Ver infracciones por API
curl http://localhost:8000/api/infractions/

# Contar infracciones
curl http://localhost:8000/api/infractions/ | grep -o '"id"' | wc -l
```

---

**Autor**: Sistema BAC - Traffic Infraction Detection System  
**Fecha**: Noviembre 4, 2025  
**Versión**: 1.0.0
