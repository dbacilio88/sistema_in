# ⚡ Inicio Rápido - Sistema de Detección de Infracciones

## 🎯 Objetivo

Tener el sistema completo ejecutándose en local en menos de 15 minutos.

## ✅ Pre-requisitos Mínimos

- Docker Desktop instalado y ejecutándose
- 8GB RAM disponible
- 20GB espacio en disco
- Conexión a Internet (para primera descarga)

## 🚀 Pasos Rápidos

### 1. Iniciar Sistema (Un Solo Comando)

```bash
# Desde WSL/Linux
./start-local.sh

# Desde Windows PowerShell
wsl bash -c "cd /home/bacsystem/github.com/sistema_in && ./start-local.sh"
```

Cuando pregunte si deseas limpiar contenedores anteriores:
- Primera vez: responde `n` (No)
- Si tuviste problemas antes: responde `s` (Sí)

⏰ **Tiempo esperado**: 
- Primera vez: 10-15 minutos
- Siguientes veces: 2-3 minutos

### 2. Verificar que Funciona

Cuando el script termine, deberías ver:

```
✓ Sistema Iniciado Exitosamente

URLs de Acceso:
🌐 Backend: http://localhost:8000
🤖 ML Service: http://localhost:8001
📊 Grafana: http://localhost:3000
```

### 3. Crear Usuario Admin

```bash
docker compose exec django python manage.py createsuperuser
```

Ingresa:
- Username: `admin`
- Email: `admin@example.com`
- Password: `admin123` (o lo que prefieras)

### 4. Acceder al Sistema

Abre tu navegador en:

- **Django Admin**: http://localhost:8000/admin
  - Login con el usuario que acabas de crear
  
- **API Docs**: http://localhost:8000/api/v1/docs/
  - Documentación interactiva de la API
  
- **ML Service**: http://localhost:8001/docs
  - API de Machine Learning

- **Grafana**: http://localhost:3000
  - Usuario: `admin`
  - Password: `admin123`

## 🧪 Probar que Funciona

### Test 1: API Health Check

```bash
curl http://localhost:8000/api/v1/health/
```

Debería responder: `{"status": "healthy"}`

### Test 2: ML Service Health

```bash
curl http://localhost:8001/health
```

Debería responder: `{"status": "healthy"}`

### Test 3: Suite Completa de Tests

```bash
./test-api.sh
```

Debería mostrar todos los tests en verde ✓

## 📊 Dashboards

### Grafana (Monitoreo)

1. Ir a http://localhost:3000
2. Login: admin / admin123
3. Explorar dashboards pre-configurados

### Prometheus (Métricas)

1. Ir a http://localhost:9090
2. Explorar métricas del sistema

### RabbitMQ (Colas)

1. Ir a http://localhost:15672
2. Login: admin / SecurePassword123!

### MinIO (Almacenamiento)

1. Ir a http://localhost:9001
2. Login: admin / SecurePassword123!

## 🔍 Ver Logs en Tiempo Real

```bash
# Todos los servicios
docker compose logs -f

# Solo backend
docker compose logs -f django

# Solo ML service
docker compose logs -f inference

# Backend + ML service
docker compose logs -f django inference
```

## 🛑 Detener el Sistema

```bash
# Detener pero mantener datos
docker compose stop

# Detener y eliminar contenedores (mantener datos)
docker compose down

# Eliminar TODO (⚠️ CUIDADO: borra todos los datos)
docker compose down -v
```

## 🆘 Problemas Comunes

### Puerto Ya en Uso

Si ves error como: `port is already allocated`

```bash
# Ver qué está usando el puerto
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac

# Detener contenedores anteriores
docker compose down
```

### Docker No Responde

```bash
# Reiniciar Docker Desktop
# Windows: Reiniciar desde la bandeja del sistema
# Linux: sudo systemctl restart docker
```

### Sin Espacio en Disco

```bash
# Limpiar Docker
docker system prune -a
docker volume prune

# Ver uso
docker system df
```

### Contenedor No Arranca

```bash
# Ver logs específicos
docker compose logs django

# Reiniciar servicio
docker compose restart django

# Reconstruir
docker compose build --no-cache django
docker compose up -d django
```

## 📱 Acceso Rápido a Comandos

### Crear Superusuario

```bash
docker compose exec django python manage.py createsuperuser
```

### Ejecutar Migraciones

```bash
docker compose exec django python manage.py migrate
```

### Abrir Shell de Django

```bash
docker compose exec django python manage.py shell
```

### Ejecutar Tests

```bash
docker compose exec django python manage.py test
```

### Ver Estado de Servicios

```bash
docker compose ps
```

### Verificar Salud del Sistema

```bash
./health-check.sh
```

## 🎓 Próximos Pasos

Una vez que el sistema esté funcionando:

1. **Explorar la API**: http://localhost:8000/api/v1/docs/
2. **Ver Ejemplos de Código**: `./docs/api/`
3. **Leer Documentación Completa**: `./docs/`
4. **Ejecutar Tests**: `./test-api.sh`
5. **Explorar Dashboards**: Grafana en http://localhost:3000

## 📚 Recursos

- [README Completo](./README-LOCAL.md)
- [Documentación de API](./docs/api/)
- [Guía de Troubleshooting](./docs/operations/troubleshooting-guide.md)
- [Runbooks](./docs/training/runbooks.md)

## 💡 Tips

### Para Desarrollo

```bash
# Hot reload está activado - los cambios en código Python
# se aplican automáticamente sin reiniciar

# Para cambios en requirements.txt:
docker compose build django
docker compose up -d django
```

### Para Pruebas

```bash
# Cargar datos de prueba
docker compose exec django python manage.py loaddata seed_data.json

# Limpiar base de datos
docker compose exec django python manage.py flush
```

### Para Debugging

```bash
# Abrir shell en contenedor
docker compose exec django bash

# Ver variables de entorno
docker compose exec django env | grep DATABASE

# Probar conectividad
docker compose exec django curl http://inference:8001/health
```

---

**¿Todo listo?** 🎉

Si llegaste hasta aquí y todo funciona, el sistema está listo para pruebas.

**¿Problemas?** Consulta el [README completo](./README-LOCAL.md) o ejecuta:

```bash
./health-check.sh  # Diagnóstico automático
./test-api.sh      # Pruebas de API
docker compose logs -f  # Ver todos los logs
```

---

**Tiempo total estimado desde cero: 15 minutos** ⏱️
