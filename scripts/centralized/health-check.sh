#!/bin/bash

# ==================================
# Script de Verificación del Sistema
# ==================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Verificación de Salud del Sistema                       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check service health
check_service() {
    local service_name=$1
    local url=$2
    local expected_code=${3:-200}
    
    echo -n "Verificando $service_name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$response" == "$expected_code" ]; then
        echo -e "${GREEN}✓ OK ($response)${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED ($response)${NC}"
        return 1
    fi
}

# Check Docker status
echo -e "${YELLOW}[1/10]${NC} Docker Status"
if docker compose ps > /dev/null 2>&1; then
    docker compose ps
    echo -e "${GREEN}✓ Docker Compose está ejecutándose${NC}"
else
    echo -e "${RED}✗ Docker Compose no está disponible${NC}"
    exit 1
fi
echo ""

# Check individual services
echo -e "${YELLOW}[2/10]${NC} Servicios de Infraestructura"
echo ""

# PostgreSQL
echo -n "PostgreSQL... "
if docker compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

# Redis
echo -n "Redis... "
if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

# RabbitMQ
echo -n "RabbitMQ... "
if docker compose exec -T rabbitmq rabbitmq-diagnostics ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

echo ""
echo -e "${YELLOW}[3/10]${NC} Servicios de Aplicación"
echo ""

# Django API
check_service "Django API" "http://localhost:8000/api/v1/health/" 200 || true

# Inference Service
check_service "ML Inference Service" "http://localhost:8001/health" 200 || true

echo ""
echo -e "${YELLOW}[4/10]${NC} Servicios de Monitoreo"
echo ""

# Prometheus
check_service "Prometheus" "http://localhost:9090/-/healthy" 200 || true

# Grafana
check_service "Grafana" "http://localhost:3000/api/health" 200 || true

echo ""
echo -e "${YELLOW}[5/10]${NC} Almacenamiento y Colas"
echo ""

# MinIO
check_service "MinIO API" "http://localhost:9000/minio/health/live" 200 || true

# RabbitMQ Management
check_service "RabbitMQ Management" "http://localhost:15672" 200 || true

echo ""
echo -e "${YELLOW}[6/10]${NC} Base de Datos"
echo ""

# Check database connection from Django
echo -n "Conexión Django → PostgreSQL... "
if docker compose exec -T django python manage.py check --database > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

echo ""
echo -e "${YELLOW}[7/10]${NC} Logs Recientes (últimas 10 líneas por servicio)"
echo ""

services=("django" "inference" "celery-worker")
for service in "${services[@]}"; do
    echo -e "${BLUE}=== $service ===${NC}"
    docker compose logs --tail=5 "$service" 2>/dev/null || echo "No logs available"
    echo ""
done

echo -e "${YELLOW}[8/10]${NC} Uso de Recursos"
echo ""

# Docker stats
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" \
    $(docker compose ps -q) 2>/dev/null || echo "No se pudo obtener estadísticas"

echo ""
echo -e "${YELLOW}[9/10]${NC} Volúmenes de Datos"
echo ""

docker volume ls | grep "sistema_in" || echo "No volumes found"

echo ""
echo -e "${YELLOW}[10/10]${NC} Resumen de Conectividad"
echo ""

# Test inter-service communication
echo -n "Django → ML Service... "
if docker compose exec -T django curl -s http://inference:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

echo -n "Django → Redis... "
if docker compose exec -T django python -c "import redis; r=redis.Redis(host='redis', port=6379); r.ping()" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Verificación de salud completada${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
