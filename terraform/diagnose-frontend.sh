#!/bin/bash

# Script de diagnóstico para problemas de frontend

echo "🔍 Diagnosticando problemas de conexión al frontend..."

# Verificar estado de contenedores
echo "📊 Estado actual de contenedores:"
docker-compose ps

echo ""
echo "🌐 Puertos expuestos:"
docker-compose ps | grep -E "frontend|3000|3001|3002"

echo ""
echo "📋 Verificando logs del frontend:"
docker-compose logs --tail=20 frontend

echo ""
echo "🔗 Verificando conectividad de red:"
echo "Contenedores en la red traffic-network:"
docker network inspect traffic-network | grep -A 5 -B 5 "Name"

echo ""
echo "🧪 Probando conectividad interna:"
# Probar si el frontend puede conectarse al backend
docker-compose exec frontend curl -s http://django:8000/health/ || echo "❌ Frontend no puede conectar al backend"

echo ""
echo "🌍 Puertos abiertos en el host:"
netstat -tlnp | grep -E ":3000|:3001|:3002" || echo "❌ No hay puertos 3000-3002 abiertos"

echo ""
echo "📱 URLs a probar:"
echo "  - Frontend: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3002"
echo "  - Backend: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
echo "  - ML Service: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8001"

echo ""
echo "🔧 Comandos de corrección recomendados:"
echo "1. Reiniciar frontend: docker-compose restart frontend"
echo "2. Reconstruir frontend: docker-compose build --no-cache frontend"
echo "3. Ver logs completos: docker-compose logs -f frontend"
echo "4. Verificar archivo Dockerfile: ls -la frontend-dashboard/Dockerfile*"