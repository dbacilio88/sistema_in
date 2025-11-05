# 📦 Guía de Backup y Restauración del Sistema

## 🎯 Resumen del Backup Creado

**Archivo**: `sistema_trafico_backup_20251105_174340.tar.gz`  
**Tamaño**: 120 KB  
**Ubicación**: `./backups/`

### 📊 Datos Incluidos

✅ **Base de Datos PostgreSQL** (600 KB)
- 898 Infracciones
- 2 Vehículos (incluyendo ABC123)
- 1 Conductor (Juan Pérez - DNI: 12345678)
- 2 Predicciones ML
- 4 Dispositivos

✅ **Configuración**
- [`.env`](.env ) con todas las variables de entorno
- [`docker-compose.yml`](docker-compose.yml )

✅ **Información del Sistema**
- Fecha y hora del backup
- Estado de los contenedores
- Estructura completa

---

## 🚀 Cómo Restaurar en Otro Ordenador

### Opción 1: Transferencia por Red (LAN)

```bash
# En el ordenador ACTUAL (donde está el backup)
scp ./backups/sistema_trafico_backup_20251105_174340.tar.gz usuario@otro-pc:/home/usuario/

# En el NUEVO ordenador
cd /home/usuario
tar -xzf sistema_trafico_backup_20251105_174340.tar.gz
```

### Opción 2: USB / Disco Externo

```bash
# 1. Copiar el archivo .tar.gz al USB
cp ./backups/sistema_trafico_backup_20251105_174340.tar.gz /media/usb/

# 2. En el nuevo ordenador, montar USB y extraer
tar -xzf /media/usb/sistema_trafico_backup_20251105_174340.tar.gz -C ~/
```

### Opción 3: Subir a AWS S3 (para despliegue en la nube)

```bash
# Subir backup a S3
aws s3 cp ./backups/sistema_trafico_backup_20251105_174340.tar.gz \
  s3://mi-bucket-backups/sistema-trafico/

# En AWS EC2, descargar
aws s3 cp s3://mi-bucket-backups/sistema-trafico/sistema_trafico_backup_20251105_174340.tar.gz ./
tar -xzf sistema_trafico_backup_20251105_174340.tar.gz
```

---

## 🔧 Instalación en el Nuevo Ordenador

### Prerrequisitos

```bash
# 1. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. Agregar usuario a grupo docker
sudo usermod -aG docker $USER
newgrp docker

# 4. Verificar instalación
docker --version
docker-compose --version
```

### Pasos de Restauración

```bash
# 1. Clonar repositorio (o extraer código)
git clone <tu-repositorio>
cd sistema_in

# 2. Extraer backup en el directorio padre
cd ..
tar -xzf sistema_trafico_backup_20251105_174340.tar.gz

# 3. Ejecutar script de restauración
cd sistema_in
./scripts/restore-full-system.sh ../backup_20251105_174340
```

El script automáticamente:
1. ✅ Restaura configuración ([`.env`](.env ), [`docker-compose.yml`](docker-compose.yml ))
2. ✅ Levanta servicios base (PostgreSQL, Redis, RabbitMQ)
3. ✅ Restaura base de datos completa
4. ✅ Copia archivos media
5. ✅ Inicia todos los servicios
6. ✅ Verifica que todo funcione

---

## 🌐 Acceso al Sistema Restaurado

Después de la restauración exitosa:

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| 🖥️ **Frontend Dashboard** | http://localhost:3002 | N/A |
| 🔧 **Django Admin** | http://localhost:8000/admin/ | admin / admin123 |
| 🤖 **Inference API** | http://localhost:8001 | N/A |
| 📊 **API Docs** | http://localhost:8000/api/docs/ | N/A |
| 📈 **Grafana** | http://localhost:3000 | admin / admin123 |

---

## 📋 Verificación Post-Restauración

```bash
# 1. Verificar todos los contenedores
docker-compose ps

# 2. Ver logs en tiempo real
docker-compose logs -f

# 3. Verificar base de datos
docker exec traffic-postgres psql -U postgres -d traffic_system -c "
SELECT COUNT(*) as infracciones FROM infractions_infraction;
"

# 4. Verificar infracción con ML
docker exec traffic-django python manage.py shell -c "
from infractions.models import Infraction
inf = Infraction.objects.filter(license_plate_detected='ABC123').first()
if inf:
    print(f'Código: {inf.infraction_code}')
    print(f'Placa: {inf.license_plate_detected}')
    print(f'Conductor: {inf.driver.full_name if inf.driver else None}')
    print(f'Riesgo ML: {inf.recidivism_risk*100:.1f}%')
"
```

---

## 🔄 Hacer Nuevos Backups

### Backup Manual

```bash
cd sistema_in
./scripts/backup-full-system.sh
```

### Backup Automático (Cron)

```bash
# Editar crontab
crontab -e

# Agregar backup diario a las 2:00 AM
0 2 * * * cd /home/usuario/sistema_in && ./scripts/backup-full-system.sh >> /var/log/backup-sistema.log 2>&1

# Agregar backup semanal los domingos
0 3 * * 0 cd /home/usuario/sistema_in && ./scripts/backup-full-system.sh >> /var/log/backup-sistema.log 2>&1
```

### Limpieza de Backups Antiguos

```bash
# Eliminar backups mayores a 30 días
find ./backups -name "sistema_trafico_backup_*.tar.gz" -mtime +30 -delete
```

---

## 🆘 Solución de Problemas

### Error: "Contenedor no encontrado"

```bash
# Verificar nombres de contenedores
docker ps -a

# Si los nombres son diferentes, editar scripts:
# - backup-full-system.sh
# - restore-full-system.sh
```

### Error: "Puerto ya en uso"

```bash
# Verificar puertos ocupados
sudo netstat -tulpn | grep -E "8000|8001|3002|5432"

# Detener servicios conflictivos o cambiar puertos en .env
```

### Error: "Base de datos no responde"

```bash
# Reiniciar PostgreSQL
docker-compose restart postgres

# Ver logs
docker logs traffic-postgres

# Verificar conectividad
docker exec traffic-postgres pg_isready -U postgres
```

### Error: "Sin espacio en disco"

```bash
# Verificar espacio
df -h

# Limpiar contenedores e imágenes no usadas
docker system prune -a --volumes
```

---

## 📚 Datos de Prueba Incluidos

El backup incluye estos datos de prueba:

### 🚗 Vehículos
- **ABC123**: Toyota Corolla 2020 (Azul)
  - Conductor: Juan Pérez (DNI: 12345678)
  - Con predicción ML de reincidencia

### 👤 Conductores
- **Juan Pérez** (DNI: 12345678)
  - Email: juan.perez@test.com
  - Teléfono: +51999999999
  - 1 vehículo asociado

### 🚨 Infracciones
- **INF-SPE-152103-23**: Exceso de velocidad
  - Placa: ABC123
  - Velocidad: 77.3 km/h (límite: 60 km/h)
  - Riesgo ML: 88% (CRÍTICO)
  - Processing time: 0.045s
  - ML prediction time: 24.826ms

### 🤖 Predicciones ML
- 2 predicciones guardadas con feature engineering completo

### 📍 Dispositivos
- **CAM-DEFAULT-001**: Cámara Web por Defecto
- Otros 3 dispositivos de prueba

---

## 🔐 Seguridad

### Cambiar Credenciales en Producción

```bash
# Editar .env antes de desplegar
nano .env

# Cambiar estas variables:
DJANGO_SECRET_KEY=<nueva-clave-secreta-fuerte>
DB_PASSWORD=<nueva-contraseña-bd>
RABBITMQ_PASSWORD=<nueva-contraseña>
MINIO_SECRET_KEY=<nueva-clave>
GRAFANA_ADMIN_PASSWORD=<nueva-contraseña>
```

### Generar Django Secret Key Segura

```python
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

---

## 📞 Soporte

Si encuentras problemas:

1. 📋 Revisar logs: `docker-compose logs -f`
2. 🔍 Verificar estado: `docker-compose ps`
3. 🔄 Reintentar: `docker-compose down && docker-compose up -d`
4. 📧 Contactar soporte: [soporte@ejemplo.com](soporte@ejemplo.com)

---

## 📝 Notas Importantes

⚠️ **El backup NO incluye**:
- Videos de MinIO (pueden ser muy grandes)
- Logs extensos
- Modelos ML customizados (usa los por defecto)

✅ **El backup SÍ incluye**:
- Toda la base de datos con registros
- Configuración completa
- Estructura y relaciones
- Datos de prueba funcionales

🎯 **Recomendación**: Hacer backups regulares y guardar en:
- AWS S3 (backup offsite)
- Disco externo (backup local)
- NAS o servidor de backups (backup en red)

---

## 🎉 ¡Listo para Desplegar!

Tu sistema está completamente respaldado y listo para ser restaurado en cualquier ordenador con Docker instalado.

**Tiempo estimado de restauración**: 5-10 minutos

**Último backup**: 2025-11-05 17:43:40
