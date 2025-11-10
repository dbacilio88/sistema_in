#!/bin/bash

# Script para corregir el problema de conexión del frontend en AWS

echo "🔧 Solucionando problema de conexión frontend → backend..."

# Obtener IP pública
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "unknown")
echo "🌐 IP Pública: $PUBLIC_IP"

if [ "$PUBLIC_IP" = "unknown" ]; then
    echo "❌ No se pudo obtener la IP pública"
    exit 1
fi

# Ir al directorio correcto
cd /opt/sistema-in

# Exportar variables
export PUBLIC_IP=$PUBLIC_IP

echo "⏹️ Deteniendo frontend..."
docker-compose -f docker-compose.yml -f docker-compose.aws.yml stop frontend

echo "🔨 Reconstruyendo frontend con nueva configuración..."
docker-compose -f docker-compose.yml -f docker-compose.aws.yml build --no-cache frontend

echo "🚀 Iniciando frontend con IP pública..."
docker-compose -f docker-compose.yml -f docker-compose.aws.yml up -d frontend

echo "⏳ Esperando que el frontend esté listo..."
sleep 15

echo "🧪 Verificando configuración..."
echo "Variables de entorno del frontend:"
docker-compose -f docker-compose.yml -f docker-compose.aws.yml exec frontend env | grep -E "NEXT_PUBLIC|API"

echo ""
echo "📱 URLs actualizadas:"
echo "  🖥️  Frontend: http://$PUBLIC_IP:3002"
echo "  🔧 Backend:  http://$PUBLIC_IP:8000"
echo ""
echo "🔍 Para ver logs del frontend:"
echo "  docker-compose -f docker-compose.yml -f docker-compose.aws.yml logs frontend"
echo ""
echo "💡 Abre las herramientas de desarrollador en tu navegador (F12)"
echo "   y busca los logs del API Service para ver la URL que está usando"