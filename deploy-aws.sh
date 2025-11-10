#!/bin/bash

# Script de deployment para AWS con IP pública automática

set -e

echo "🚀 Desplegando Sistema IN en AWS..."

# Obtener IP pública de la instancia EC2
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "")

if [ -z "$PUBLIC_IP" ]; then
    echo "❌ No se pudo obtener la IP pública. ¿Estás ejecutando esto en EC2?"
    echo "💡 Configura manualmente: export PUBLIC_IP=tu-ip-publica"
    PUBLIC_IP=${PUBLIC_IP:-"localhost"}
fi

echo "🌐 IP Pública detectada: $PUBLIC_IP"

# Exportar variables de entorno
export PUBLIC_IP=$PUBLIC_IP
export COMPOSE_PROJECT_NAME=sistema-in

# Ir al directorio correcto
cd /opt/sistema-in || { echo "❌ Directorio /opt/sistema-in no encontrado"; exit 1; }

# Actualizar código si es un repositorio git
if [ -d ".git" ]; then
    echo "📥 Actualizando código..."
    git pull origin master || git pull origin main || echo "⚠️ No se pudo actualizar desde git"
fi

# Detener servicios existentes
echo "⏹️ Deteniendo servicios existentes..."
docker-compose -f docker-compose.yml -f docker-compose.aws.yml down || true

# Limpiar contenedores e imágenes no utilizadas
echo "🧹 Limpiando recursos Docker..."
docker system prune -f

# Construir imágenes
echo "🔨 Construyendo imágenes..."
docker-compose -f docker-compose.yml -f docker-compose.aws.yml build --no-cache

# Iniciar servicios de forma escalonada
echo "🚀 Iniciando servicios de base de datos..."
docker-compose -f docker-compose.yml -f docker-compose.aws.yml up -d postgres redis minio

echo "⏳ Esperando que las bases de datos estén listas..."
sleep 20

echo "🚀 Iniciando servicios de aplicación..."
docker-compose -f docker-compose.yml -f docker-compose.aws.yml up -d django inference

echo "⏳ Esperando que los servicios backend estén listos..."
sleep 30

echo "🚀 Iniciando frontend y servicios adicionales..."
docker-compose -f docker-compose.yml -f docker-compose.aws.yml up -d

echo "📊 Verificando estado de los servicios..."
docker-compose -f docker-compose.yml -f docker-compose.aws.yml ps

# Verificar conectividad
echo ""
echo "🧪 Verificando conectividad..."
echo "Testing backend..."
curl -f "http://localhost:8000/api/health/" > /dev/null 2>&1 && echo "✅ Backend OK" || echo "❌ Backend failed"

echo "Testing frontend..."
curl -f "http://localhost:3002" > /dev/null 2>&1 && echo "✅ Frontend OK" || echo "❌ Frontend failed"

echo ""
echo "✅ ¡Deployment completado!"
echo ""
echo "🌐 Tu aplicación está disponible en:"
echo "  🖥️  Frontend:     http://$PUBLIC_IP:3002"
echo "  🔧 Backend API:   http://$PUBLIC_IP:8000"
echo "  🤖 ML Service:    http://$PUBLIC_IP:8001"
echo "  📊 Grafana:       http://$PUBLIC_IP:3001"
echo "  📈 Prometheus:    http://$PUBLIC_IP:9090"
echo "  🗃️  MinIO:         http://$PUBLIC_IP:9001"
echo "  ⚙️  Config Mgmt:   http://$PUBLIC_IP:8080"
echo ""
echo "📋 Comandos útiles:"
echo "  Ver logs:     docker-compose -f docker-compose.yml -f docker-compose.aws.yml logs [servicio]"
echo "  Reiniciar:    docker-compose -f docker-compose.yml -f docker-compose.aws.yml restart [servicio]"
echo "  Estado:       docker-compose -f docker-compose.yml -f docker-compose.aws.yml ps"
echo ""
echo "🔍 Para troubleshooting:"
echo "  docker-compose -f docker-compose.yml -f docker-compose.aws.yml logs frontend"
echo "  docker-compose -f docker-compose.yml -f docker-compose.aws.yml logs django"