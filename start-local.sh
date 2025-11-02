#!/bin/bash

# ==================================
# Script de Inicio Local - Sistema de Detección de Infracciones
# ==================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Sistema de Detección de Infracciones de Tráfico        ║${NC}"
echo -e "${BLUE}║   Inicio de Entorno Local para Pruebas                    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if Docker is running
echo -e "${YELLOW}[1/8]${NC} Verificando Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Error: Docker no está ejecutándose${NC}"
    echo -e "Por favor, inicia Docker Desktop y vuelve a ejecutar este script."
    exit 1
fi
echo -e "${GREEN}✓ Docker está ejecutándose${NC}"

# Check if Docker Compose is available
echo -e "${YELLOW}[2/8]${NC} Verificando Docker Compose..."
if ! docker compose version > /dev/null 2>&1; then
    echo -e "${RED}✗ Error: Docker Compose no está disponible${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose está disponible${NC}"

# Check if .env file exists
echo -e "${YELLOW}[3/8]${NC} Verificando archivo .env..."
if [ ! -f .env ]; then
    echo -e "${RED}✗ Error: Archivo .env no encontrado${NC}"
    echo -e "Creando archivo .env con valores por defecto..."
    cat > .env << 'EOF'
DB_NAME=traffic_system
DB_USER=postgres
DB_PASSWORD=postgres123!
DJANGO_SECRET_KEY=django-insecure-local-dev-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,django
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=SecurePassword123!
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=SecurePassword123!
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin123
INFERENCE_DEVICE=cpu
EOF
    echo -e "${GREEN}✓ Archivo .env creado${NC}"
else
    echo -e "${GREEN}✓ Archivo .env encontrado${NC}"
fi

# Clean up old containers and volumes (optional)
echo -e "${YELLOW}[4/8]${NC} Limpiando contenedores anteriores..."
echo -e "¿Deseas limpiar contenedores y volúmenes anteriores? (s/N)"
read -r response
if [[ "$response" =~ ^([sS][iI]|[sS])$ ]]; then
    echo -e "Deteniendo y eliminando contenedores anteriores..."
    docker compose down -v
    echo -e "${GREEN}✓ Limpieza completada${NC}"
else
    echo -e "${GREEN}✓ Se omitió la limpieza${NC}"
fi

# Build Docker images
echo -e "${YELLOW}[5/8]${NC} Construyendo imágenes Docker..."
echo -e "Esto puede tomar varios minutos la primera vez..."
docker compose build --no-cache
echo -e "${GREEN}✓ Imágenes construidas exitosamente${NC}"

# Start infrastructure services first
echo -e "${YELLOW}[6/8]${NC} Iniciando servicios de infraestructura..."
docker compose up -d postgres redis rabbitmq minio
echo -e "Esperando a que los servicios estén listos (30 segundos)..."
sleep 30

# Initialize MinIO buckets
echo -e "${YELLOW}[7/8]${NC} Inicializando almacenamiento MinIO..."
docker compose up -d minio-init
sleep 10
echo -e "${GREEN}✓ Buckets de MinIO creados${NC}"

# Start application services
echo -e "${YELLOW}[8/8]${NC} Iniciando servicios de aplicación..."
docker compose up -d django inference celery-worker celery-beat prometheus grafana
echo -e "Esperando a que los servicios estén listos (40 segundos)..."
sleep 40

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✓ Sistema Iniciado Exitosamente                         ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   URLs de Acceso al Sistema${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}🌐 Backend Django API:${NC}"
echo -e "   http://localhost:8000"
echo -e "   http://localhost:8000/admin (Django Admin)"
echo -e "   http://localhost:8000/api/v1/docs/ (API Documentation)"
echo ""
echo -e "${GREEN}🤖 ML Inference Service:${NC}"
echo -e "   http://localhost:8001"
echo -e "   http://localhost:8001/docs (FastAPI Docs)"
echo ""
echo -e "${GREEN}📊 Monitoring & Management:${NC}"
echo -e "   http://localhost:3000 (Grafana - admin/admin123)"
echo -e "   http://localhost:9090 (Prometheus)"
echo -e "   http://localhost:15672 (RabbitMQ - admin/SecurePassword123!)"
echo -e "   http://localhost:9001 (MinIO Console - admin/SecurePassword123!)"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}📝 Comandos Útiles:${NC}"
echo -e "   ${GREEN}Ver logs:${NC}           docker compose logs -f [servicio]"
echo -e "   ${GREEN}Detener sistema:${NC}    docker compose stop"
echo -e "   ${GREEN}Reiniciar sistema:${NC}  docker compose restart"
echo -e "   ${GREEN}Ver estado:${NC}         docker compose ps"
echo -e "   ${GREEN}Acceder a shell:${NC}    docker compose exec django bash"
echo -e "   ${GREEN}Ejecutar migraciones:${NC} docker compose exec django python manage.py migrate"
echo -e "   ${GREEN}Crear superusuario:${NC} docker compose exec django python manage.py createsuperuser"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Show service status
echo -e "${YELLOW}Estado de los Servicios:${NC}"
docker compose ps

echo ""
echo -e "${GREEN}✓ El sistema está listo para pruebas locales${NC}"
echo -e "${YELLOW}⚠ Recuerda: Este es un entorno de desarrollo/pruebas${NC}"
echo ""
