#!/bin/bash

# Script para corregir problemas del frontend

set -e

echo "🔧 Corrigiendo problemas del frontend..."

# Ir al directorio correcto
cd /opt/sistema-in

# Parar todos los contenedores
echo "⏹️ Deteniendo contenedores..."
docker-compose down

# Limpiar contenedores e imágenes problemáticas
echo "🧹 Limpiando contenedores anteriores..."
docker container prune -f
docker image prune -f

# Verificar que los directorios existen
echo "📂 Verificando directorios..."
if [ ! -d "frontend-dashboard" ]; then
    echo "❌ Directorio frontend-dashboard no encontrado"
    exit 1
fi

if [ ! -f "frontend-dashboard/Dockerfile.dev" ]; then
    echo "❌ Dockerfile.dev no encontrado"
    ls -la frontend-dashboard/Dockerfile*
    exit 1
fi

# Corregir archivo docker-compose.yml si tiene errores
echo "📝 Verificando docker-compose.yml..."
docker-compose config || {
    echo "❌ Error en docker-compose.yml"
    exit 1
}

# Construir solo el frontend primero
echo "🔨 Construyendo frontend..."
docker-compose build frontend

# Iniciar solo los servicios esenciales primero
echo "🚀 Iniciando servicios base..."
docker-compose up -d postgres redis

# Esperar a que postgres esté listo
echo "⏳ Esperando a que PostgreSQL esté listo..."
sleep 10

# Iniciar backend
echo "🚀 Iniciando backend..."
docker-compose up -d django

# Esperar a que backend esté listo
echo "⏳ Esperando a que backend esté listo..."
sleep 15

# Iniciar frontend
echo "🚀 Iniciando frontend..."
docker-compose up -d frontend

# Mostrar estado
echo "📊 Estado final:"
docker-compose ps

echo ""
echo "📱 URLs disponibles:"
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")
echo "  - Frontend: http://$PUBLIC_IP:3002"
echo "  - Backend:  http://$PUBLIC_IP:8000"

echo ""
echo "📋 Para verificar logs:"
echo "  docker-compose logs frontend"

echo "✅ Corrección completada!"