#!/bin/bash

# Script para verificar conectividad entre servicios

echo "🔍 Verificando conectividad entre servicios..."

# Función para verificar conectividad
check_service() {
    local service=$1
    local url=$2
    local description=$3
    
    echo -n "  $description: "
    if docker-compose exec $service curl -s -f "$url" > /dev/null 2>&1; then
        echo "✅ OK"
    else
        echo "❌ FAILED"
        return 1
    fi
}

# Verificar que los contenedores estén ejecutándose
echo "📊 Estado de contenedores:"
docker-compose -f docker-compose.yml -f docker-compose.aws.yml ps

echo ""
echo "🌐 Verificando conectividad externa (desde el host):"

PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")
echo "IP Pública: $PUBLIC_IP"

# Verificar acceso externo
check_external() {
    local port=$1
    local service=$2
    echo -n "  $service (puerto $port): "
    if curl -s -f "http://localhost:$port" > /dev/null 2>&1; then
        echo "✅ Accesible externamente"
    else
        echo "❌ No accesible externamente"
    fi
}

check_external 8000 "Django Backend"
check_external 8001 "ML Service" 
check_external 3002 "Frontend"
check_external 3001 "Grafana"

echo ""
echo "🔗 Verificando conectividad interna (entre contenedores):"

# Verificar conectividad desde frontend a backend
echo "Frontend → Backend:"
if docker-compose exec frontend curl -s -f "http://django:8000/api/health/" > /dev/null 2>&1; then
    echo "  ✅ Frontend puede conectar a Django"
else
    echo "  ❌ Frontend no puede conectar a Django"
fi

# Verificar conectividad desde frontend a ML service
echo "Frontend → ML Service:"
if docker-compose exec frontend curl -s -f "http://inference:8001/api/v1/health" > /dev/null 2>&1; then
    echo "  ✅ Frontend puede conectar a ML Service"
else
    echo "  ❌ Frontend no puede conectar a ML Service"
fi

# Verificar conectividad desde backend a base de datos
echo "Backend → PostgreSQL:"
if docker-compose exec django python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(
        host='postgres',
        database=os.environ.get('POSTGRES_DB', 'traffic_system'),
        user=os.environ.get('POSTGRES_USER', 'postgres'),
        password=os.environ.get('POSTGRES_PASSWORD', 'postgres123!')
    )
    conn.close()
    print('  ✅ Django puede conectar a PostgreSQL')
except Exception as e:
    print(f'  ❌ Django no puede conectar a PostgreSQL: {e}')
" 2>/dev/null; then
    echo ""
else
    echo "  ❌ Error verificando conexión Django → PostgreSQL"
fi

# Verificar conectividad desde backend a Redis
echo "Backend → Redis:"
if docker-compose exec django python -c "
import redis
try:
    r = redis.Redis(host='redis', port=6379, db=0)
    r.ping()
    print('  ✅ Django puede conectar a Redis')
except Exception as e:
    print(f'  ❌ Django no puede conectar a Redis: {e}')
" 2>/dev/null; then
    echo ""
else
    echo "  ❌ Error verificando conexión Django → Redis"
fi

echo ""
echo "📱 URLs finales para acceso externo:"
echo "  🖥️  Frontend:     http://$PUBLIC_IP:3002"
echo "  🔧 Backend API:   http://$PUBLIC_IP:8000"
echo "  🤖 ML Service:    http://$PUBLIC_IP:8001"
echo "  📊 Grafana:       http://$PUBLIC_IP:3001"
echo "  📈 Prometheus:    http://$PUBLIC_IP:9090"
echo "  🗃️  MinIO:         http://$PUBLIC_IP:9001"

echo ""
echo "🔍 Comandos de troubleshooting:"
echo "  docker-compose -f docker-compose.yml -f docker-compose.aws.yml logs frontend"
echo "  docker-compose -f docker-compose.yml -f docker-compose.aws.yml logs django"
echo "  docker-compose -f docker-compose.yml -f docker-compose.aws.yml exec frontend env | grep API"