#!/bin/bash
# ==============================================================================
# SCRIPT DE RESTAURACIÓN COMPLETA DEL SISTEMA
# ==============================================================================
# Este script restaura un backup completo del sistema en un nuevo ordenador
# ==============================================================================

set -e  # Salir si hay error

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Validar argumentos
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: Debe especificar el directorio del backup${NC}"
    echo -e "${YELLOW}Uso: $0 <directorio_backup>${NC}"
    echo -e "${YELLOW}Ejemplo: $0 ../backup_20251105_123456${NC}"
    exit 1
fi

BACKUP_DIR="$1"

if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}❌ Error: Directorio de backup no encontrado: $BACKUP_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🔄 RESTAURACIÓN COMPLETA - Sistema de Tránsito              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Mostrar información del backup
if [ -f "$BACKUP_DIR/BACKUP_INFO.txt" ]; then
    echo -e "${YELLOW}📋 Información del backup:${NC}"
    cat "$BACKUP_DIR/BACKUP_INFO.txt"
    echo ""
    
    echo -e "${YELLOW}⚠️  ¿Desea continuar con la restauración? (s/n)${NC}"
    read -r CONFIRM
    if [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "S" ]; then
        echo -e "${YELLOW}Restauración cancelada${NC}"
        exit 0
    fi
fi

# 1. RESTAURAR CONFIGURACIÓN
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}⚙️  PASO 1: Restaurando Configuración${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -f "$BACKUP_DIR/config/.env" ]; then
    cp "$BACKUP_DIR/config/.env" .env
    echo -e "${GREEN}   ✓ Archivo .env restaurado${NC}"
else
    echo -e "${YELLOW}   ⚠ Archivo .env no encontrado en backup${NC}"
fi

if [ -f "$BACKUP_DIR/config/docker-compose.yml" ]; then
    cp "$BACKUP_DIR/config/docker-compose.yml" docker-compose.yml
    echo -e "${GREEN}   ✓ Archivo docker-compose.yml restaurado${NC}"
else
    echo -e "${YELLOW}   ⚠ Archivo docker-compose.yml no encontrado en backup${NC}"
fi
echo ""

# 2. LEVANTAR SERVICIOS BASE
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🐳 PASO 2: Levantando Servicios Base${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${BLUE}   � Iniciando PostgreSQL, Redis, RabbitMQ...${NC}"
docker-compose up -d postgres redis rabbitmq minio

echo -e "${BLUE}   ⏳ Esperando a que los servicios estén listos (15 segundos)...${NC}"
sleep 15

# Verificar PostgreSQL
echo -e "${BLUE}   🔍 Verificando PostgreSQL...${NC}"
for i in {1..30}; do
    if docker exec traffic-postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo -e "${GREEN}   ✓ PostgreSQL está listo${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}   ❌ Timeout esperando PostgreSQL${NC}"
        exit 1
    fi
    sleep 1
done
echo ""

# 3. RESTAURAR BASE DE DATOS
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🗄️  PASO 3: Restaurando Base de Datos${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ ! -f "$BACKUP_DIR/database.sql" ]; then
    echo -e "${RED}   ❌ Error: Archivo database.sql no encontrado${NC}"
    exit 1
fi

echo -e "${BLUE}   📦 Restaurando base de datos desde backup...${NC}"
cat "$BACKUP_DIR/database.sql" | docker exec -i traffic-postgres psql -U postgres -d traffic_system

if [ $? -eq 0 ]; then
    echo -e "${GREEN}   ✓ Base de datos restaurada exitosamente${NC}"
    
    # Verificar datos restaurados
    echo -e "${BLUE}   📊 Verificando datos restaurados:${NC}"
    docker exec traffic-postgres psql -U postgres -d traffic_system -t -c "
        SELECT 
            '   Infracciones: ' || COUNT(*) FROM infractions_infraction
        UNION ALL
        SELECT 
            '   Vehículos: ' || COUNT(*) FROM vehicles_vehicle
        UNION ALL
        SELECT 
            '   Conductores: ' || COUNT(*) FROM vehicles_driver
        UNION ALL
        SELECT 
            '   Predicciones ML: ' || COUNT(*) FROM ml_models_mlprediction
        UNION ALL
        SELECT 
            '   Dispositivos: ' || COUNT(*) FROM devices_device;
    " | grep -v "^$"
else
    echo -e "${RED}   ❌ Error al restaurar base de datos${NC}"
    exit 1
fi
echo ""

# 4. LEVANTAR DJANGO Y COPIAR ARCHIVOS MEDIA
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📁 PASO 4: Restaurando Archivos Media${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${BLUE}   🚀 Iniciando Django...${NC}"
docker-compose up -d django

echo -e "${BLUE}   ⏳ Esperando a que Django esté listo (10 segundos)...${NC}"
sleep 10

if [ -d "$BACKUP_DIR/media" ]; then
    echo -e "${BLUE}   📦 Copiando archivos media...${NC}"
    docker cp "$BACKUP_DIR/media/." traffic-django:/app/media/
    
    if [ $? -eq 0 ]; then
        MEDIA_COUNT=$(find "$BACKUP_DIR/media" -type f | wc -l)
        echo -e "${GREEN}   ✓ Archivos media restaurados ($MEDIA_COUNT archivos)${NC}"
    else
        echo -e "${YELLOW}   ⚠ Error al copiar archivos media${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠ No hay archivos media en el backup${NC}"
fi
echo ""

# 5. LEVANTAR RESTO DE SERVICIOS
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🚀 PASO 5: Levantando Todos los Servicios${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${BLUE}   🐳 Iniciando inference-service, frontend, etc...${NC}"
docker-compose up -d

echo -e "${BLUE}   ⏳ Esperando a que todos los servicios estén listos (10 segundos)...${NC}"
sleep 10

echo -e "${GREEN}   ✓ Todos los servicios iniciados${NC}"
echo ""

# 6. VERIFICACIÓN FINAL
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🔍 PASO 6: Verificación Final${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${BLUE}   🐳 Estado de los contenedores:${NC}"
docker-compose ps

echo ""
echo -e "${BLUE}   🌐 Verificando endpoints:${NC}"

# Verificar Django
if curl -s http://localhost:8000/api/health/ > /dev/null 2>&1; then
    echo -e "${GREEN}   ✓ Django API: http://localhost:8000 (OK)${NC}"
else
    echo -e "${YELLOW}   ⚠ Django API: http://localhost:8000 (No responde aún)${NC}"
fi

# Verificar Inference
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}   ✓ Inference Service: http://localhost:8001 (OK)${NC}"
else
    echo -e "${YELLOW}   ⚠ Inference Service: http://localhost:8001 (No responde aún)${NC}"
fi

# Verificar Frontend
if curl -s http://localhost:3002 > /dev/null 2>&1; then
    echo -e "${GREEN}   ✓ Frontend: http://localhost:3002 (OK)${NC}"
else
    echo -e "${YELLOW}   ⚠ Frontend: http://localhost:3002 (No responde aún)${NC}"
fi

echo ""

# RESUMEN FINAL
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            ✅ RESTAURACIÓN COMPLETADA EXITOSAMENTE             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}🎉 El sistema ha sido restaurado completamente!${NC}"
echo ""
echo -e "${YELLOW}📋 Servicios disponibles:${NC}"
echo -e "   🌐 Frontend Dashboard: ${GREEN}http://localhost:3002${NC}"
echo -e "   🔧 Django Admin: ${GREEN}http://localhost:8000/admin/${NC}"
echo -e "   🤖 Inference Service: ${GREEN}http://localhost:8001${NC}"
echo -e "   📊 API Docs: ${GREEN}http://localhost:8000/api/docs/${NC}"
echo ""
echo -e "${YELLOW}📝 Comandos útiles:${NC}"
echo -e "   Ver logs: ${BLUE}docker-compose logs -f${NC}"
echo -e "   Detener: ${BLUE}docker-compose stop${NC}"
echo -e "   Reiniciar: ${BLUE}docker-compose restart${NC}"
echo ""
echo -e "${GREEN}✨ ¡Sistema listo para usar!${NC}"
echo ""
