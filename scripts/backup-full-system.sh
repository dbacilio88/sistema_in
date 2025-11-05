#!/bin/bash
# ==============================================================================
# SCRIPT DE BACKUP COMPLETO DEL SISTEMA
# ==============================================================================
# Este script crea un backup completo de:
# - Base de datos PostgreSQL
# - Archivos media de Django
# - Configuración (.env)
# - Logs importantes
# ==============================================================================

set -e  # Salir si hay error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sin color

# Configuración
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_ROOT="./backups"
BACKUP_DIR="$BACKUP_ROOT/backup_$TIMESTAMP"
CONTAINER_DB="traffic-postgres"
CONTAINER_DJANGO="traffic-django"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     🔄 BACKUP COMPLETO DEL SISTEMA - Sistema de Tránsito      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Crear directorio de backup
echo -e "${YELLOW}📁 Creando directorio de backup...${NC}"
mkdir -p "$BACKUP_DIR"
echo -e "${GREEN}   ✓ Directorio creado: $BACKUP_DIR${NC}"
echo ""

# 1. BACKUP DE POSTGRESQL
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🗄️  PASO 1: Respaldando Base de Datos PostgreSQL${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Verificar que el contenedor existe
if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_DB}$"; then
    echo -e "${RED}❌ Error: Contenedor PostgreSQL '${CONTAINER_DB}' no encontrado${NC}"
    exit 1
fi

# Verificar que está corriendo
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_DB}$"; then
    echo -e "${RED}❌ Error: Contenedor PostgreSQL no está corriendo${NC}"
    exit 1
fi

# Backup de PostgreSQL
echo -e "${BLUE}   📦 Generando dump de PostgreSQL...${NC}"
docker exec $CONTAINER_DB pg_dump -U postgres -d traffic_system \
    --no-owner --no-acl --clean --if-exists \
    > "$BACKUP_DIR/database.sql"

if [ $? -eq 0 ]; then
    DB_SIZE=$(du -h "$BACKUP_DIR/database.sql" | cut -f1)
    echo -e "${GREEN}   ✓ Base de datos respaldada: $DB_SIZE${NC}"
    
    # Contar registros importantes
    echo -e "${BLUE}   📊 Estadísticas de la base de datos:${NC}"
    docker exec $CONTAINER_DB psql -U postgres -d traffic_system -t -c "
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
    echo -e "${RED}   ❌ Error al respaldar base de datos${NC}"
    exit 1
fi
echo ""

# 2. BACKUP DE ARCHIVOS MEDIA
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📁 PASO 2: Respaldando Archivos Media${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Verificar contenedor Django
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_DJANGO}$"; then
    echo -e "${BLUE}   📦 Copiando archivos media...${NC}"
    mkdir -p "$BACKUP_DIR/media"
    
    # Copiar media files (evidencias, snapshots)
    if docker exec $CONTAINER_DJANGO test -d /app/media; then
        docker cp ${CONTAINER_DJANGO}:/app/media "$BACKUP_DIR/" 2>/dev/null || true
        if [ -d "$BACKUP_DIR/media" ]; then
            MEDIA_SIZE=$(du -sh "$BACKUP_DIR/media" | cut -f1)
            MEDIA_COUNT=$(find "$BACKUP_DIR/media" -type f | wc -l)
            echo -e "${GREEN}   ✓ Archivos media respaldados: $MEDIA_SIZE ($MEDIA_COUNT archivos)${NC}"
        else
            echo -e "${YELLOW}   ⚠ No hay archivos media para respaldar${NC}"
        fi
    else
        echo -e "${YELLOW}   ⚠ Directorio media no existe en el contenedor${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠ Contenedor Django no está corriendo, saltando archivos media${NC}"
fi
echo ""

# 3. BACKUP DE CONFIGURACIÓN
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}⚙️  PASO 3: Respaldando Configuración${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

mkdir -p "$BACKUP_DIR/config"

# Copiar .env
if [ -f ".env" ]; then
    cp .env "$BACKUP_DIR/config/"
    echo -e "${GREEN}   ✓ Archivo .env respaldado${NC}"
else
    echo -e "${YELLOW}   ⚠ Archivo .env no encontrado${NC}"
fi

# Copiar docker-compose.yml
if [ -f "docker-compose.yml" ]; then
    cp docker-compose.yml "$BACKUP_DIR/config/"
    echo -e "${GREEN}   ✓ Archivo docker-compose.yml respaldado${NC}"
else
    echo -e "${YELLOW}   ⚠ Archivo docker-compose.yml no encontrado${NC}"
fi

# Información del sistema
echo -e "${BLUE}   📝 Generando información del sistema...${NC}"
cat > "$BACKUP_DIR/BACKUP_INFO.txt" << EOF
╔════════════════════════════════════════════════════════════════╗
║           INFORMACIÓN DEL BACKUP - Sistema de Tránsito        ║
╚════════════════════════════════════════════════════════════════╝

📅 Fecha del backup: $(date '+%Y-%m-%d %H:%M:%S %Z')
💻 Hostname: $(hostname)
👤 Usuario: $(whoami)
📂 Directorio: $(pwd)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐳 CONTENEDORES DOCKER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}" | grep -E "django|postgres|redis|rabbitmq|minio|inference")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 CONTENIDO DEL BACKUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF

# Listar contenido del backup
find "$BACKUP_DIR" -type f -o -type d | sed "s|$BACKUP_DIR||" | grep -v "^$" >> "$BACKUP_DIR/BACKUP_INFO.txt"

echo -e "${GREEN}   ✓ Información del sistema generada${NC}"
echo ""

# 4. COMPRIMIR BACKUP
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🗜️  PASO 4: Comprimiendo Backup${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

BACKUP_FILE="$BACKUP_ROOT/sistema_trafico_backup_$TIMESTAMP.tar.gz"

echo -e "${BLUE}   🗜️  Comprimiendo archivos...${NC}"
tar -czf "$BACKUP_FILE" -C "$BACKUP_ROOT" "backup_$TIMESTAMP"

if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}   ✓ Backup comprimido exitosamente: $BACKUP_SIZE${NC}"
    
    # Limpiar directorio temporal
    rm -rf "$BACKUP_DIR"
    echo -e "${GREEN}   ✓ Archivos temporales limpiados${NC}"
else
    echo -e "${RED}   ❌ Error al comprimir backup${NC}"
    exit 1
fi
echo ""

# 5. RESUMEN FINAL
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  ✅ BACKUP COMPLETADO EXITOSAMENTE             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📦 Archivo de backup:${NC}"
echo -e "   ${GREEN}$BACKUP_FILE${NC}"
echo ""
echo -e "${BLUE}📊 Tamaño total:${NC}"
echo -e "   ${GREEN}$BACKUP_SIZE${NC}"
echo ""
echo -e "${BLUE}📝 Contenido incluido:${NC}"
echo -e "   ✓ Base de datos PostgreSQL (traffic_system)"
echo -e "   ✓ Archivos media (evidencias, snapshots)"
echo -e "   ✓ Configuración (.env, docker-compose.yml)"
echo -e "   ✓ Información del sistema"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📋 INSTRUCCIONES PARA RESTAURAR EN OTRO ORDENADOR:${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}1. Copiar el archivo:${NC}"
echo -e "   scp $BACKUP_FILE usuario@otro-pc:/home/usuario/"
echo ""
echo -e "${BLUE}2. En el nuevo ordenador, extraer:${NC}"
echo -e "   tar -xzf sistema_trafico_backup_$TIMESTAMP.tar.gz"
echo ""
echo -e "${BLUE}3. Ejecutar el script de restauración:${NC}"
echo -e "   cd sistema_in"
echo -e "   ./scripts/restore-full-system.sh ../backup_$TIMESTAMP"
echo ""
echo -e "${GREEN}🎉 ¡Backup completado! Guarda este archivo en un lugar seguro.${NC}"
echo ""
