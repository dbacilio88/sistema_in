#!/bin/bash

# Script para arreglar el error de permisos de entrypoint.sh

echo "🔧 Arreglando permisos de entrypoint.sh..."

# Navegar al directorio correcto
cd /opt/sistema-in

# Parar contenedores si están ejecutándose
echo "⏹️ Deteniendo contenedores..."
docker-compose down || true

# Dar permisos de ejecución al entrypoint.sh local
echo "🔐 Configurando permisos locales..."
chmod +x backend-django/entrypoint.sh
ls -la backend-django/entrypoint.sh

# Limpiar imágenes y contenedores
echo "🧹 Limpiando imágenes anteriores..."
docker system prune -f
docker image prune -f

# Reconstruir y ejecutar
echo "🔨 Reconstruyendo contenedores..."
docker-compose build --no-cache backend

echo "🚀 Iniciando contenedores..."
docker-compose up -d

echo "✅ Corrección completada!"
echo ""
echo "📊 Estado de contenedores:"
docker-compose ps

echo ""
echo "📋 Si el problema persiste, ejecuta:"
echo "   docker-compose logs backend"