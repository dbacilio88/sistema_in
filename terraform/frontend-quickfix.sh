#!/bin/bash

echo "🚀 Solución rápida para frontend..."

# Comandos que debes ejecutar en la instancia EC2:

echo "1. Conectarse por SSH:"
echo "   ssh -i sistema-in-key.pem ec2-user@IP_PUBLICA"
echo ""

echo "2. Ir al directorio de la aplicación:"
echo "   cd /opt/sistema-in"
echo ""

echo "3. Clonar el repositorio actualizado:"
echo "   git clone https://github.com/dbacilio88/sistema_in.git ."
echo ""

echo "4. Verificar estado actual:"
echo "   docker-compose ps"
echo ""

echo "5. Detener contenedores:"
echo "   docker-compose down"
echo ""

echo "6. Limpiar y reconstruir:"
echo "   docker system prune -f"
echo "   docker-compose build --no-cache"
echo ""

echo "7. Iniciar servicios de forma escalonada:"
echo "   docker-compose up -d postgres redis"
echo "   sleep 10"
echo "   docker-compose up -d django"
echo "   sleep 15"
echo "   docker-compose up -d frontend"
echo ""

echo "8. Verificar logs:"
echo "   docker-compose logs frontend"
echo ""

echo "9. Probar conectividad:"
echo "   curl http://localhost:3002"
echo ""

echo "📱 URLs para acceder:"
echo "   Frontend: http://IP_PUBLICA:3002"
echo "   Backend:  http://IP_PUBLICA:8000"
echo ""

echo "🔍 Para diagnosticar problemas:"
echo "   docker-compose logs --tail=50 frontend"
echo "   docker-compose exec frontend curl http://django:8000"
echo "   netstat -tlnp | grep 3002"