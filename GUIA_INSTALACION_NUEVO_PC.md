# 🚀 Guía Completa: Instalación del Sistema en Nuevo Ordenador

Esta guía te llevará paso a paso para instalar y ejecutar el **Sistema de Monitoreo de Tráfico con IA** en un ordenador nuevo, partiendo desde cero hasta tener todo funcionando.

---

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación de Dependencias](#instalación-de-dependencias)
3. [Transferencia del Backup](#transferencia-del-backup)
4. [Clonación del Repositorio](#clonación-del-repositorio)
5. [Restauración del Sistema](#restauración-del-sistema)
6. [Verificación del Sistema](#verificación-del-sistema)
7. [Acceso a los Servicios](#acceso-a-los-servicios)
8. [Solución de Problemas](#solución-de-problemas)

---

## 1️⃣ Requisitos Previos

### Hardware Mínimo
- **CPU**: 4 cores (8 recomendado para ML)
- **RAM**: 8 GB (16 GB recomendado)
- **Disco**: 50 GB libres
- **GPU**: Opcional (acelera detección YOLO)

### Sistema Operativo
- ✅ **Ubuntu 20.04/22.04** (recomendado)
- ✅ **Windows 10/11** con WSL2
- ✅ **macOS** con Docker Desktop

---

## 2️⃣ Instalación de Dependencias

### Opción A: Ubuntu/Debian

```bash
# 1. Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar Git
sudo apt install -y git

# 3. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 4. Agregar usuario al grupo docker (evita usar sudo)
sudo usermod -aG docker $USER

# 5. Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 6. Reiniciar sesión para aplicar permisos
# Cierra la terminal y vuelve a abrirla

# 7. Verificar instalación
docker --version
docker-compose --version
git --version
```

### Opción B: Windows 10/11

```powershell
# 1. Instalar WSL2
wsl --install

# 2. Reiniciar el PC

# 3. Descargar e instalar Docker Desktop
# https://www.docker.com/products/docker-desktop

# 4. Instalar Git for Windows
# https://git-scm.com/download/win

# 5. Abrir PowerShell y verificar
wsl --version
docker --version
git --version

# 6. Abrir terminal Ubuntu en WSL2
wsl
```

### Opción C: macOS

```bash
# 1. Instalar Homebrew (si no lo tienes)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Instalar Git
brew install git

# 3. Descargar e instalar Docker Desktop
# https://www.docker.com/products/docker-desktop

# 4. Verificar instalación
docker --version
docker-compose --version
git --version
```

---

## 3️⃣ Transferencia del Backup

### Opción 1: Transferencia por Red (SCP)

**Desde el PC antiguo:**
```bash
# Obtener IP del nuevo PC
# En el nuevo PC: ip addr show | grep inet

# Transferir backup
scp ./backups/sistema_trafico_backup_20251105_174340.tar.gz usuario@<IP-NUEVO-PC>:/home/usuario/
```

**Desde el PC nuevo (alternativa):**
```bash
# Crear directorio
mkdir -p ~/sistema-trafico

# Descargar desde PC antiguo
scp usuario@<IP-PC-ANTIGUO>:/ruta/al/backup/sistema_trafico_backup_20251105_174340.tar.gz ~/sistema-trafico/
```

### Opción 2: Transferencia por USB

**En el PC antiguo:**
```bash
# Montar USB
sudo mount /dev/sdb1 /mnt/usb

# Copiar backup
cp ./backups/sistema_trafico_backup_20251105_174340.tar.gz /mnt/usb/

# Desmontar USB
sudo umount /mnt/usb
```

**En el PC nuevo:**
```bash
# Montar USB
sudo mount /dev/sdb1 /mnt/usb

# Crear directorio y copiar
mkdir -p ~/sistema-trafico
cp /mnt/usb/sistema_trafico_backup_20251105_174340.tar.gz ~/sistema-trafico/

# Desmontar USB
sudo umount /mnt/usb
```

### Opción 3: Transferencia por AWS S3

**En el PC antiguo:**
```bash
# Instalar AWS CLI
sudo apt install -y awscli

# Configurar credenciales
aws configure

# Subir a S3
aws s3 cp ./backups/sistema_trafico_backup_20251105_174340.tar.gz s3://mi-bucket-trafico/
```

**En el PC nuevo:**
```bash
# Instalar AWS CLI
sudo apt install -y awscli

# Configurar credenciales (mismas del PC antiguo)
aws configure

# Descargar de S3
mkdir -p ~/sistema-trafico
cd ~/sistema-trafico
aws s3 cp s3://mi-bucket-trafico/sistema_trafico_backup_20251105_174340.tar.gz .
```

---

## 4️⃣ Clonación del Repositorio

```bash
# 1. Ir al directorio home
cd ~

# 2. Clonar el repositorio
git clone https://github.com/dbacilio88/sistema_in.git

# 3. Entrar al directorio
cd sistema_in

# 4. Verificar estructura
ls -la
```

**Salida esperada:**
```
backend-django/
inference-service/
frontend-dashboard/
docker-compose.yml
scripts/
backups/
docs/
...
```

---

## 5️⃣ Restauración del Sistema

### Paso 1: Extraer el Backup

```bash
# 1. Ir al directorio donde está el backup
cd ~/sistema-trafico

# 2. Extraer el archivo
tar -xzf sistema_trafico_backup_20251105_174340.tar.gz

# 3. Verificar contenido extraído
ls -la backup_20251105_174340/
```

**Contenido esperado:**
```
backup_20251105_174340/
├── BACKUP_INFO.txt          # Información del backup
├── database.sql             # Base de datos (898 infracciones)
├── config/
│   ├── .env                 # Variables de entorno
│   └── docker-compose.yml   # Configuración Docker
└── media/                   # Archivos multimedia (si existen)
```

### Paso 2: Ejecutar Script de Restauración

```bash
# 1. Ir al directorio del proyecto
cd ~/sistema_in

# 2. Dar permisos de ejecución al script
chmod +x scripts/restore-full-system.sh

# 3. Ejecutar restauración (apuntando al directorio del backup extraído)
./scripts/restore-full-system.sh ~/sistema-trafico/backup_20251105_174340
```

**Proceso automático que ejecutará:**
```
✓ Copiando configuración...
✓ Iniciando servicios base (PostgreSQL, Redis, RabbitMQ, MinIO)...
✓ Esperando PostgreSQL (30 segundos máximo)...
✓ Restaurando base de datos...
✓ Iniciando servicios completos...
✓ Copiando archivos media...
✓ Verificando servicios...
```

**Tiempo estimado:** 5-10 minutos

### Paso 3: Esperar Inicialización

```bash
# Monitorear logs de Django (en otra terminal)
docker logs -f traffic-django

# Esperar mensaje:
# "Performing system checks..."
# "Django version 4.2.x"
# "Starting development server at http://0.0.0.0:8000/"
```

---

## 6️⃣ Verificación del Sistema

### Verificar Contenedores Activos

```bash
# Listar todos los contenedores
docker-compose ps
```

**Salida esperada (12 contenedores):**
```
NAME                      STATUS
traffic-django            Up (healthy)
traffic-postgres          Up (healthy)
traffic-inference         Up (healthy)
traffic-frontend          Up
traffic-redis             Up
traffic-rabbitmq          Up
traffic-minio             Up
traffic-grafana           Up
traffic-prometheus        Up
traffic-celery-worker     Up
traffic-celery-beat       Up
traffic-config-mgmt       Up
```

### Verificar Base de Datos

```bash
# Conectar a PostgreSQL y verificar datos
docker exec -it traffic-postgres psql -U postgres -d traffic_system -c "
SELECT 
    'Infracciones' as tipo, COUNT(*) as total FROM infractions_infraction
UNION ALL
SELECT 'Vehículos', COUNT(*) FROM vehicles_vehicle
UNION ALL
SELECT 'Conductores', COUNT(*) FROM vehicles_driver
UNION ALL
SELECT 'Predicciones ML', COUNT(*) FROM ml_models_mlprediction
UNION ALL
SELECT 'Dispositivos', COUNT(*) FROM devices_device;
"
```

**Salida esperada:**
```
      tipo       | total
-----------------+-------
 Infracciones    |   898
 Vehículos       |     2
 Conductores     |     1
 Predicciones ML |     2
 Dispositivos    |     4
```

### Verificar Servicios Web

```bash
# Django Backend
curl -s http://localhost:8000/health/ | jq

# Inference Service
curl -s http://localhost:8001/health | jq

# Frontend Dashboard
curl -s http://localhost:3002 | grep -o "<title>.*</title>"
```

---

## 7️⃣ Acceso a los Servicios

### 🌐 URLs de Acceso

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Frontend Dashboard** | http://localhost:3002 | N/A |
| **Backend API** | http://localhost:8000 | N/A |
| **Django Admin** | http://localhost:8000/admin | admin / admin123 |
| **Inference Service** | http://localhost:8001 | N/A |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin |
| **Grafana** | http://localhost:3000 | admin / admin |
| **RabbitMQ** | http://localhost:15672 | guest / guest |

### 🔐 Cambiar Credenciales de Producción

**⚠️ IMPORTANTE:** Antes de usar en producción, cambiar todas las contraseñas:

```bash
# Editar .env
nano .env

# Cambiar estas variables:
DJANGO_SECRET_KEY=<nuevo-secreto-generado>
DB_PASSWORD=<nuevo-password-fuerte>
RABBITMQ_PASSWORD=<nuevo-password>
MINIO_SECRET_KEY=<nuevo-secreto>
GRAFANA_ADMIN_PASSWORD=<nuevo-password>

# Generar nuevo Django secret key
docker exec traffic-django python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Reiniciar servicios
docker-compose down
docker-compose up -d
```

---

## 8️⃣ Solución de Problemas

### Problema: Contenedores no inician

```bash
# Ver logs específicos
docker logs traffic-django --tail 50
docker logs traffic-postgres --tail 50

# Verificar puertos en uso
sudo netstat -tulpn | grep -E '3002|8000|8001|5432'

# Si hay conflicto de puertos, editar docker-compose.yml
nano docker-compose.yml
# Cambiar puertos según necesidad
```

### Problema: Base de datos no se restaura

```bash
# Verificar que PostgreSQL está listo
docker exec traffic-postgres pg_isready -U postgres

# Intentar restauración manual
docker exec -i traffic-postgres psql -U postgres -d traffic_system < ~/sistema-trafico/backup_20251105_174340/database.sql

# Ver errores específicos
docker logs traffic-postgres --tail 100
```

### Problema: Falta de memoria

```bash
# Ver uso de recursos
docker stats

# Detener servicios no esenciales
docker stop traffic-grafana traffic-prometheus

# Aumentar memoria de Docker (Docker Desktop)
# Settings > Resources > Memory: 8 GB mínimo
```

### Problema: Frontend no carga

```bash
# Verificar logs
docker logs traffic-frontend --tail 50

# Reconstruir frontend
cd frontend-dashboard
docker-compose up -d --build frontend

# Verificar variable NEXT_PUBLIC_API_URL en .env
grep NEXT_PUBLIC_API_URL .env
```

### Problema: Inference service no responde

```bash
# Verificar logs
docker logs traffic-inference --tail 50

# Verificar que los modelos ML están descargados
docker exec traffic-inference ls -lh /app/models/

# Si faltan modelos, ejecutar script de descarga
docker exec traffic-inference python download_models.py
```

---

## 🎯 Comandos Útiles de Mantenimiento

### Ver logs en tiempo real
```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker logs -f traffic-django
docker logs -f traffic-inference
docker logs -f traffic-frontend
```

### Reiniciar servicios
```bash
# Todos los servicios
docker-compose restart

# Servicio específico
docker-compose restart django
docker-compose restart inference
```

### Detener sistema
```bash
# Detener todos los contenedores
docker-compose down

# Detener y eliminar volúmenes (⚠️ borra datos no respaldados)
docker-compose down -v
```

### Crear nuevo backup
```bash
# Ejecutar script de backup
./scripts/backup-full-system.sh

# Ver backups creados
ls -lh backups/
```

### Actualizar código
```bash
# Obtener últimos cambios
git pull origin master

# Reconstruir contenedores si hay cambios en Dockerfile
docker-compose up -d --build
```

---

## 📊 Verificación Final del Sistema

### Script de Verificación Completa

```bash
#!/bin/bash
echo "🔍 Verificando Sistema de Tráfico..."
echo ""

# 1. Contenedores
echo "📦 Contenedores activos:"
docker-compose ps | grep Up | wc -l
echo ""

# 2. Base de datos
echo "💾 Datos en base de datos:"
docker exec traffic-postgres psql -U postgres -d traffic_system -c "
SELECT 'Infracciones: ' || COUNT(*) FROM infractions_infraction;
" -t

# 3. APIs
echo "🌐 Estado de APIs:"
curl -s http://localhost:8000/health/ > /dev/null && echo "✅ Django: OK" || echo "❌ Django: Error"
curl -s http://localhost:8001/health > /dev/null && echo "✅ Inference: OK" || echo "❌ Inference: Error"
curl -s http://localhost:3002 > /dev/null && echo "✅ Frontend: OK" || echo "❌ Frontend: Error"
echo ""

# 4. Disco
echo "💿 Uso de disco:"
du -sh .
echo ""

echo "✅ Verificación completada"
```

**Guardar como `verify-system.sh` y ejecutar:**
```bash
chmod +x verify-system.sh
./verify-system.sh
```

---

## 🚀 ¡Sistema Listo!

Si todos los checks anteriores están en verde, tu sistema está completamente funcional con:

- ✅ **898 infracciones** restauradas
- ✅ **2 vehículos** (incluido ABC123)
- ✅ **1 conductor** (Juan Pérez)
- ✅ **2 predicciones ML** con 88% de precisión
- ✅ **4 dispositivos** de monitoreo
- ✅ **12 servicios** corriendo en Docker
- ✅ **Dashboard web** accesible
- ✅ **API REST** funcionando
- ✅ **Servicio ML** para inferencia

### Próximos Pasos Recomendados

1. **Cambiar credenciales** de producción (ver sección 7)
2. **Configurar backup automático** con cron
3. **Configurar monitoreo** con Grafana
4. **Configurar SSL/HTTPS** si es producción
5. **Conectar cámaras RTSP** reales
6. **Configurar notificaciones** por email/webhook

---

## 📞 Soporte

Si encuentras problemas no documentados aquí:

1. Revisar logs: `docker-compose logs`
2. Consultar documentación en `docs/`
3. Verificar issues en GitHub
4. Crear nuevo issue con logs completos

---

**Versión:** 1.0.0  
**Fecha:** Noviembre 2025  
**Sistema:** Traffic Monitoring System with AI  
**Backup:** 898 infracciones + 2 vehículos + ML models
