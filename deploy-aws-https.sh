#!/bin/bash

# Script completo para desplegar en AWS con HTTPS
echo "🚀 Desplegando sistema con HTTPS en AWS..."

# Variables
DOMAIN=${1:-54.86.67.166}
MODE=${2:-development}  # development o production

echo "📋 Configuración:"
echo "   🌐 Dominio: $DOMAIN"
echo "   🔧 Modo: $MODE"
echo ""

# Paso 1: Detener servicios existentes
echo "🛑 Deteniendo servicios existentes..."
docker-compose -f docker-compose.yml -f docker-compose.aws.yml down

# Paso 2: Configurar SSL
echo "🔒 Configurando certificados SSL..."
./setup-ssl-aws.sh $DOMAIN $MODE

if [ $? -ne 0 ]; then
    echo "❌ Error configurando SSL"
    exit 1
fi

# Paso 3: Construir imágenes
echo "🔨 Construyendo imágenes..."
docker-compose -f docker-compose.yml -f docker-compose.aws.yml --env-file .env.aws build

if [ $? -ne 0 ]; then
    echo "❌ Error construyendo imágenes"
    exit 1
fi

# Paso 4: Iniciar servicios
echo "🚀 Iniciando servicios con HTTPS..."
docker-compose -f docker-compose.yml -f docker-compose.aws.yml --env-file .env.aws up -d

if [ $? -ne 0 ]; then
    echo "❌ Error iniciando servicios"
    exit 1
fi

# Paso 5: Esperar que los servicios estén listos
echo "⏳ Esperando que los servicios estén listos..."
sleep 10

# Paso 6: Verificar servicios
echo "🔍 Verificando servicios..."

services=("nginx" "frontend" "django" "inference" "postgres" "redis")
all_healthy=true

for service in "${services[@]}"; do
    if docker-compose -f docker-compose.yml -f docker-compose.aws.yml ps | grep -q "$service.*Up"; then
        echo "   ✅ $service: Corriendo"
    else
        echo "   ❌ $service: Error"
        all_healthy=false
    fi
done

if [ "$all_healthy" = true ]; then
    echo ""
    echo "🎉 Despliegue completado exitosamente!"
    echo ""
    echo "🌐 URLs disponibles:"
    echo "   • Frontend: https://$DOMAIN"
    echo "   • API:      https://$DOMAIN/api/"
    echo "   • ML:       https://$DOMAIN/ml/"
    echo "   • Admin:    https://$DOMAIN/api/admin/"
    echo ""
    echo "📱 Para acceder a la cámara:"
    echo "   1. Accede a: https://$DOMAIN"
    echo "   2. Acepta el certificado SSL"
    echo "   3. Permite el acceso a la cámara"
    echo ""
    if [ "$MODE" = "development" ]; then
        echo "⚠️  Certificado autofirmado - el navegador mostrará advertencia de seguridad"
        echo "    Haz clic en 'Avanzado' -> 'Continuar'"
    fi
else
    echo ""
    echo "❌ Algunos servicios fallaron. Revisa los logs:"
    echo "   docker-compose -f docker-compose.yml -f docker-compose.aws.yml logs"
fi