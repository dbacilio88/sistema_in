# 🚦 Sistema de Detección de Infracciones de Tráfico - Guía de Inicio Local

Este documento proporciona instrucciones para ejecutar el sistema completo en tu máquina local para pruebas antes de desplegar en producción.

## 📋 Requisitos Previos

### Software Requerido

- **Docker Desktop** (versión 20.10 o superior)
  - Windows: [Descargar Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - Debe tener WSL 2 habilitado en Windows
- **Docker Compose** (incluido en Docker Desktop)
- **Git** para clonar el repositorio
- **Mínimo 8GB RAM** disponible para Docker
- **Mínimo 20GB** de espacio en disco

### Verificar Instalación

```bash
# Verificar Docker
docker --version
# Debería mostrar: Docker version 20.10+

# Verificar Docker Compose
docker compose version
# Debería mostrar: Docker Compose version v2.0+

# Verificar que Docker está ejecutándose
docker info
```

## 🚀 Inicio Rápido

### 1. Clonar el Repositorio (si aún no lo has hecho)

```bash
git clone <repository-url>
cd sistema_in
```

### 2. Configurar Variables de Entorno

El archivo `.env` ya está configurado con valores por defecto para desarrollo local. Puedes modificarlo si es necesario:

```bash
# Ver configuración actual
cat .env

# Editar si necesitas cambiar algo
nano .env  # o usa tu editor preferido
```

### 3. Iniciar el Sistema Completo

Usa el script automatizado que se encarga de todo:

```bash
# Desde WSL o terminal Linux
./start-local.sh

# Desde PowerShell (Windows)
wsl bash -c "cd /home/bacsystem/github.com/sistema_in && ./start-local.sh"
```

El script realizará:
- ✅ Verificación de Docker y Docker Compose
- ✅ Verificación del archivo .env
- ✅ Construcción de imágenes Docker
- ✅ Inicio de servicios de infraestructura (PostgreSQL, Redis, RabbitMQ, MinIO)
- ✅ Inicialización de buckets de almacenamiento
- ✅ Inicio de servicios de aplicación (Django, ML Service, Celery)
- ✅ Inicio de servicios de monitoreo (Prometheus, Grafana)

**Tiempo estimado de primera ejecución:** 10-15 minutos

### 4. Verificar que Todo Está Funcionando

```bash
# Usando el script de verificación
./health-check.sh

# Manualmente
docker compose ps
```

## 🌐 URLs de Acceso

Una vez que el sistema esté ejecutándose, puedes acceder a:

### Aplicaciones Principales

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Django Admin** | http://localhost:8000/admin | Crear con: `docker compose exec django python manage.py createsuperuser` |
| **API Backend** | http://localhost:8000/api/v1/ | Token JWT requerido |
| **API Documentation** | http://localhost:8000/api/v1/docs/ | Documentación interactiva |
| **ML Service API** | http://localhost:8001 | - |
| **ML Service Docs** | http://localhost:8001/docs | Documentación FastAPI |

### Herramientas de Gestión

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Grafana** | http://localhost:3000 | admin / admin123 |
| **Prometheus** | http://localhost:9090 | Sin autenticación |
| **RabbitMQ Management** | http://localhost:15672 | admin / SecurePassword123! |
| **MinIO Console** | http://localhost:9001 | admin / SecurePassword123! |

## 🧪 Ejecutar Pruebas

### Pruebas Automatizadas de API

```bash
./test-api.sh
```

### Pruebas Unitarias Backend

```bash
# Ejecutar todos los tests
docker compose exec django python manage.py test

# Ejecutar tests específicos
docker compose exec django python manage.py test authentication
docker compose exec django python manage.py test infractions

# Con coverage
docker compose exec django coverage run --source='.' manage.py test
docker compose exec django coverage report
```

### Pruebas del ML Service

```bash
# Ejecutar tests con pytest
docker compose exec inference pytest

# Con coverage
docker compose exec inference pytest --cov=app
```

## 📝 Comandos Útiles

### Gestión de Contenedores

```bash
# Ver logs en tiempo real
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f django
docker compose logs -f inference
docker compose logs -f celery-worker

# Ver logs de los últimos 100 líneas
docker compose logs --tail=100 django

# Detener todos los servicios
docker compose stop

# Reiniciar un servicio específico
docker compose restart django

# Reiniciar todo el sistema
docker compose restart

# Ver estado de los servicios
docker compose ps

# Ver uso de recursos
docker stats
```

### Acceso a Shells

```bash
# Shell de Django
docker compose exec django bash
docker compose exec django python manage.py shell

# Shell del ML Service
docker compose exec inference bash

# Shell de PostgreSQL
docker compose exec postgres psql -U postgres -d traffic_system

# Shell de Redis
docker compose exec redis redis-cli
```

### Gestión de Base de Datos

```bash
# Ejecutar migraciones
docker compose exec django python manage.py migrate

# Crear migración nueva
docker compose exec django python manage.py makemigrations

# Ver estado de migraciones
docker compose exec django python manage.py showmigrations

# Crear superusuario
docker compose exec django python manage.py createsuperuser

# Cargar datos de prueba
docker compose exec django python manage.py loaddata seed_data.json

# Limpiar base de datos (¡CUIDADO!)
docker compose exec django python manage.py flush
```

### Debugging

```bash
# Ver variables de entorno
docker compose exec django env

# Verificar conectividad entre servicios
docker compose exec django curl http://inference:8001/health
docker compose exec django curl http://redis:6379

# Ver procesos en ejecución
docker compose exec django ps aux
docker compose exec inference ps aux

# Verificar uso de memoria
docker compose exec django free -h

# Verificar espacio en disco
docker compose exec django df -h
```

## 🛑 Detener el Sistema

### Opción 1: Usar el Script

```bash
./stop-local.sh
```

El script te dará tres opciones:
1. **Detener contenedores** (mantener datos)
2. **Detener y eliminar contenedores** (mantener volúmenes/datos)
3. **Detener y eliminar TODO** (incluyendo datos - ⚠️ DESTRUCTIVO)

### Opción 2: Comandos Manuales

```bash
# Solo detener (mantener todo)
docker compose stop

# Detener y eliminar contenedores (mantener volúmenes)
docker compose down

# Eliminar TODO incluyendo volúmenes (⚠️ CUIDADO)
docker compose down -v

# Eliminar también imágenes
docker compose down --rmi all
```

## 🔧 Troubleshooting

### Problema: Puerto ya en uso

```bash
# Ver qué proceso está usando el puerto
# Windows PowerShell
netsh interface ipv4 show excludedportrange protocol=tcp

# Linux/WSL
sudo lsof -i :8000
sudo netstat -tulpn | grep 8000

# Cambiar puerto en docker-compose.yml
# Ejemplo para Django: cambiar "8000:8000" a "8080:8000"
```

### Problema: Sin espacio en disco

```bash
# Limpiar imágenes no usadas
docker system prune -a

# Limpiar volúmenes no usados
docker volume prune

# Ver uso de espacio
docker system df
```

### Problema: Contenedor no arranca

```bash
# Ver logs detallados
docker compose logs <servicio>

# Ver eventos
docker compose events

# Reiniciar servicio específico
docker compose restart <servicio>

# Reconstruir imagen
docker compose build --no-cache <servicio>
docker compose up -d <servicio>
```

### Problema: Base de datos corrupta

```bash
# Detener todo
docker compose down

# Eliminar volumen de PostgreSQL
docker volume rm sistema_in_postgres_data

# Reiniciar (se recreará vacío)
docker compose up -d postgres

# Esperar que inicie y ejecutar migraciones
docker compose exec django python manage.py migrate
```

### Problema: Memoria insuficiente

```bash
# Aumentar memoria de Docker Desktop
# Docker Desktop > Settings > Resources > Memory: 8GB mínimo

# Reducir workers en docker-compose.yml
# django: cambiar --workers 4 a --workers 2
# inference: cambiar --workers 4 a --workers 2
```

## 📊 Monitoreo

### Métricas en Grafana

1. Acceder a http://localhost:3000
2. Login: admin / admin123
3. Ir a Dashboards
4. Explorar dashboards pre-configurados:
   - Traffic System Overview
   - Database Performance
   - API Performance
   - ML Service Metrics

### Métricas en Prometheus

1. Acceder a http://localhost:9090
2. Query examples:
   ```promql
   # Request rate
   rate(http_requests_total[5m])
   
   # 95th percentile response time
   histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
   
   # Error rate
   rate(http_requests_total{status=~"5.."}[5m])
   
   # ML processing time
   ml_inference_duration_seconds
   ```

## 🔐 Seguridad en Desarrollo Local

⚠️ **IMPORTANTE**: Este entorno está configurado para desarrollo/pruebas locales.

### Diferencias con Producción

| Aspecto | Local | Producción |
|---------|-------|------------|
| DEBUG | Activado | Desactivado |
| Secretos | Valores simples | Generados seguros |
| HTTPS | No | Sí (requerido) |
| Exposición de puertos | Todos | Solo necesarios |
| Recursos | Limitados | Escalables |

### Antes de Producción

- [ ] Cambiar todos los secretos y contraseñas
- [ ] Desactivar DEBUG en Django
- [ ] Configurar HTTPS/TLS
- [ ] Configurar firewall
- [ ] Configurar backups automáticos
- [ ] Configurar alertas de monitoreo
- [ ] Revisar logs de seguridad
- [ ] Actualizar documentación

## 📚 Recursos Adicionales

### Documentación

- [Documentación Completa](./docs/)
- [API Backend](./docs/api/backend-api.md)
- [ML Service API](./docs/api/ml-service-api.md)
- [Guía de Troubleshooting](./docs/operations/troubleshooting-guide.md)
- [Runbooks Operacionales](./docs/training/runbooks.md)

### Soporte

- **Issues**: [GitHub Issues](link-to-issues)
- **Email**: support@example.com
- **Documentación**: `./docs/`

## 📝 Notas Adicionales

### Datos de Prueba

El sistema carga automáticamente datos de prueba en el primer inicio. Estos incluyen:

- Usuarios de ejemplo (admin, operator, technician)
- Vehículos de ejemplo
- Infracciones de muestra
- Configuraciones iniciales

### Desarrollo

Si estás desarrollando y modificando código:

```bash
# Los cambios en Python se aplicarán automáticamente (hot reload)
# Para forzar recarga:
docker compose restart django

# Para cambios en dependencias (requirements.txt):
docker compose build django
docker compose up -d django

# Para cambios en modelos de base de datos:
docker compose exec django python manage.py makemigrations
docker compose exec django python manage.py migrate
```

### Performance

Para mejor performance en desarrollo local:

1. Asignar más memoria a Docker (8GB recomendado)
2. Usar SSD para volúmenes de Docker
3. Reducir workers si la máquina es lenta
4. Desactivar servicios no necesarios en docker-compose.yml

---

**¿Problemas?** Consulta la [Guía de Troubleshooting](./docs/operations/troubleshooting-guide.md) o ejecuta `./health-check.sh` para diagnósticos automáticos.
