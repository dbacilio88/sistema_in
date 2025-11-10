#!/bin/bash

# Script de solución rápida para el error de ALLOWED_HOSTS

echo "🚨 Solucionando error de ALLOWED_HOSTS..."

# Obtener IP pública actual
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "unknown")
echo "🌐 IP Pública detectada: $PUBLIC_IP"

if [ "$PUBLIC_IP" = "unknown" ]; then
    echo "❌ No se pudo obtener la IP pública. ¿Estás en EC2?"
    exit 1
fi

# Ir al directorio correcto
cd /opt/sistema-in

# Parar el backend
echo "⏹️ Reiniciando backend con nueva configuración..."
docker-compose -f docker-compose.yml -f docker-compose.aws.yml stop django

# Exportar la IP pública
export PUBLIC_IP=$PUBLIC_IP

# Reiniciar el backend con la nueva configuración
echo "🚀 Iniciando Django con ALLOWED_HOSTS actualizado..."
docker-compose -f docker-compose.yml -f docker-compose.aws.yml up -d django

# Esperar un momento
sleep 10

# Verificar que funciona
echo "🧪 Probando conectividad..."
if curl -s -f "http://$PUBLIC_IP:8000/" > /dev/null; then
    echo "✅ ¡Problema solucionado! Backend accesible en http://$PUBLIC_IP:8000"
else
    echo "❌ Aún hay problemas. Verificando logs..."
    docker-compose -f docker-compose.yml -f docker-compose.aws.yml logs --tail=20 django
fi

echo ""
echo "📱 URLs actualizadas:"
echo "  Backend:  http://$PUBLIC_IP:8000"
echo "  Frontend: http://$PUBLIC_IP:3002"
echo ""
echo "🔧 Si persiste el problema, ejecuta:"
echo "  docker-compose -f docker-compose.yml -f docker-compose.aws.yml logs django"