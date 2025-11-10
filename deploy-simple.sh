#!/bin/bash

# Script de deployment simplificado para AWS usando solo .env

set -e

echo "🚀 Desplegando Sistema IN en AWS (usando .env)..."

# Obtener IP pública de la instancia EC2
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "")

if [ -z "$PUBLIC_IP" ]; then
    echo "❌ No se pudo obtener la IP pública. ¿Estás ejecutando esto en EC2?"
    echo "💡 Configura manualmente: export PUBLIC_IP=tu-ip-publica"
    PUBLIC_IP=${PUBLIC_IP:-"localhost"}
fi

echo "🌐 IP Pública detectada: $PUBLIC_IP"

# Actualizar .env con la IP actual
echo "⚙️ Actualizando .env con IP pública: $PUBLIC_IP"

# Actualizar las URLs del frontend en .env
sed -i "s|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=http://$PUBLIC_IP:8000|g" .env
sed -i "s|NEXT_PUBLIC_ML_SERVICE_URL=.*|NEXT_PUBLIC_ML_SERVICE_URL=http://$PUBLIC_IP:8001|g" .env
sed -i "s|NEXT_PUBLIC_WS_URL=.*|NEXT_PUBLIC_WS_URL=ws://$PUBLIC_IP:8000|g" .env

# Asegurar que ALLOWED_HOSTS incluya la IP pública
sed -i "s|ALLOWED_HOSTS=.*|ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,django,$PUBLIC_IP,*|g" .env

echo "📝 Archivo .env actualizado con IP $PUBLIC_IP"

# Exportar variables de entorno
export PUBLIC_IP=$PUBLIC_IP
export COMPOSE_PROJECT_NAME=sistema-in

# Parar servicios existentes
echo "⏹️ Parando servicios existentes..."
docker-compose down || true

echo "🔧 Construyendo servicios..."
docker-compose build --no-cache

echo "🚀 Iniciando servicios..."
docker-compose up -d

echo "⏳ Esperando que los servicios estén listos..."
sleep 30

echo "🔍 Verificando estado de los servicios..."
docker-compose ps

echo "✅ Deployment completado!"
echo "🌐 Accede a la aplicación en: http://$PUBLIC_IP:3000"
echo "🔧 API disponible en: http://$PUBLIC_IP:8000"