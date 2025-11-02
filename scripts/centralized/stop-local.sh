#!/bin/bash

# ==================================
# Script de Detención - Sistema de Detección de Infracciones
# ==================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Deteniendo Sistema de Detección de Infracciones        ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Ask for cleanup option
echo -e "${YELLOW}¿Cómo deseas detener el sistema?${NC}"
echo -e "  1) Detener contenedores (mantener datos)"
echo -e "  2) Detener y eliminar contenedores (mantener volúmenes)"
echo -e "  3) Detener y eliminar TODO (incluyendo volúmenes de datos)"
echo -e ""
read -p "Selecciona una opción (1-3): " option

case $option in
    1)
        echo -e "${YELLOW}Deteniendo contenedores...${NC}"
        docker compose stop
        echo -e "${GREEN}✓ Contenedores detenidos${NC}"
        ;;
    2)
        echo -e "${YELLOW}Deteniendo y eliminando contenedores...${NC}"
        docker compose down
        echo -e "${GREEN}✓ Contenedores eliminados (datos preservados)${NC}"
        ;;
    3)
        echo -e "${RED}¡ADVERTENCIA! Esto eliminará TODOS los datos del sistema.${NC}"
        read -p "¿Estás seguro? (escribir 'SI' para confirmar): " confirm
        if [ "$confirm" == "SI" ]; then
            echo -e "${YELLOW}Deteniendo y eliminando TODO...${NC}"
            docker compose down -v --remove-orphans
            echo -e "${GREEN}✓ Sistema completamente eliminado${NC}"
        else
            echo -e "${YELLOW}Operación cancelada${NC}"
        fi
        ;;
    *)
        echo -e "${RED}Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✓ Operación completada${NC}"
