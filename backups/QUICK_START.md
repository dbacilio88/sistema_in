# ⚡ Quick Start - Restaurar Sistema en Nuevo Ordenador

## 📋 Prerrequisitos

```bash
# Verificar Docker instalado
docker --version
docker-compose --version

# Si NO está instalado:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

## 🚀 Restauración en 3 Comandos

```bash
# 1. Extraer backup
tar -xzf sistema_trafico_backup_20251105_174340.tar.gz

# 2. Clonar repositorio
git clone https://github.com/dbacilio88/sistema_in.git
cd sistema_in

# 3. Restaurar todo
./scripts/restore-full-system.sh ../backup_20251105_174340
```

## ✅ Verificación Rápida

```bash
# Ver servicios
docker-compose ps

# Debe mostrar:
# - traffic-django (UP)
# - traffic-postgres (UP)
# - traffic-inference (UP)
# - traffic-frontend (UP)
# - traffic-redis (UP)
# - traffic-rabbitmq (UP)
```

## 🌐 Accesos

| Servicio | URL | Usuario | Contraseña |
|----------|-----|---------|------------|
| Frontend | http://localhost:3002 | - | - |
| Admin | http://localhost:8000/admin/ | admin | admin123 |
| API Docs | http://localhost:8000/api/docs/ | - | - |

## 🔍 Verificar Datos Restaurados

```bash
# Contar infracciones
docker exec traffic-postgres psql -U postgres -d traffic_system -c \
  "SELECT COUNT(*) FROM infractions_infraction;"

# Ver infracción con ML (ABC123)
docker exec traffic-django python manage.py shell -c "
from infractions.models import Infraction
inf = Infraction.objects.filter(license_plate_detected='ABC123').first()
print(f'Código: {inf.infraction_code}')
print(f'Riesgo ML: {inf.recidivism_risk*100:.1f}%')
"
```

## 🆘 Problemas Comunes

### Puerto ocupado

```bash
# Cambiar puerto en .env
nano .env
# Modificar: DJANGO_PORT=8001 (en lugar de 8000)

# Reiniciar
docker-compose down
docker-compose up -d
```

### Contenedor no inicia

```bash
# Ver logs
docker logs traffic-django --tail 50

# Reiniciar servicio
docker-compose restart django
```

### Base de datos no responde

```bash
# Verificar PostgreSQL
docker exec traffic-postgres pg_isready -U postgres

# Reiniciar si es necesario
docker-compose restart postgres
sleep 5
docker-compose restart django
```

## 📚 Documentación Completa

Ver: [`./backups/README_BACKUP.md`](./backups/README_BACKUP.md)

## 🎉 ¡Listo!

Tu sistema debería estar funcionando en menos de 10 minutos.

---

**Última actualización**: 2025-11-05  
**Versión del backup**: 20251105_174340
