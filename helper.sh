#!/bin/bash
################################################################################
# Helper Script - Comandos Útiles para Desarrollo Local
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

show_menu() {
    clear
    print_header "Sistema de Detección de Infracciones - Helper"
    echo ""
    echo "1)  📊 Ver estado de todos los servicios"
    echo "2)  📝 Ver logs de Django"
    echo "3)  📝 Ver logs de Celery Worker"
    echo "4)  📝 Ver logs de Celery Beat"
    echo "5)  📝 Ver logs de Inference Service"
    echo "6)  📝 Ver logs de Frontend Dashboard"
    echo "7)  📝 Ver logs de Config Management"
    echo "8)  📝 Ver logs de todos los servicios"
    echo ""
    echo "9)  🔄 Reiniciar Django"
    echo "10) 🔄 Reiniciar Celery"
    echo "11) 🔄 Reiniciar Frontend"
    echo "12) 🔄 Reiniciar Config Management"
    echo "13) 🔄 Reiniciar todos los servicios"
    echo ""
    echo "14) 🗄️  Crear migraciones"
    echo "15) 🗄️  Ejecutar migraciones"
    echo "16) 🗄️  Ver estado de migraciones"
    echo "17) 🗄️  Crear superusuario"
    echo ""
    echo "18) 🧪 Ejecutar tests de Django"
    echo "19) 🧪 Verificar salud del sistema"
    echo "20) 🧪 Test de API"
    echo ""
    echo "21) 🔍 Shell de Django"
    echo "22) 🔍 Shell de PostgreSQL"
    echo "23) 🔍 Monitor de Redis"
    echo ""
    echo "24) 🌐 Abrir URLs de servicios"
    echo "25) 📊 Ver uso de recursos"
    echo "26) 🧹 Limpiar sistema (con confirmación)"
    echo ""
    echo "0)  🚪 Salir"
    echo ""
    echo -n "Selecciona una opción: "
}

# 1. Ver estado de servicios
show_status() {
    print_header "Estado de Servicios"
    docker compose ps
    echo ""
    print_info "Presiona Enter para continuar..."
    read
}

# 2-6. Ver logs
show_logs() {
    local service=$1
    local service_name=$2
    print_header "Logs de $service_name"
    echo "Mostrando últimas 50 líneas. Presiona Ctrl+C para salir del seguimiento."
    echo ""
    sleep 2
    if [ "$service" == "all" ]; then
        docker compose logs -f --tail=50
    else
        docker compose logs -f --tail=50 "$service"
    fi
}

# 7-9. Reiniciar servicios
restart_service() {
    local service=$1
    local service_name=$2
    print_header "Reiniciando $service_name"
    if [ "$service" == "all" ]; then
        docker compose restart
        print_success "Todos los servicios reiniciados"
    elif [ "$service" == "celery" ]; then
        docker compose restart celery-worker celery-beat
        print_success "Servicios Celery reiniciados"
    else
        docker compose restart "$service"
        print_success "$service_name reiniciado"
    fi
    echo ""
    print_info "Presiona Enter para continuar..."
    read
}

# 10. Crear migraciones
make_migrations() {
    print_header "Crear Migraciones"
    echo "Creando migraciones para cambios en modelos..."
    docker compose exec django python manage.py makemigrations
    echo ""
    print_success "Migraciones creadas"
    print_info "Presiona Enter para continuar..."
    read
}

# 11. Ejecutar migraciones
run_migrations() {
    print_header "Ejecutar Migraciones"
    echo "Aplicando migraciones a la base de datos..."
    docker compose exec django python manage.py migrate
    echo ""
    print_success "Migraciones aplicadas"
    print_info "Presiona Enter para continuar..."
    read
}

# 12. Ver estado de migraciones
show_migrations() {
    print_header "Estado de Migraciones"
    docker compose exec django python manage.py showmigrations
    echo ""
    print_info "Presiona Enter para continuar..."
    read
}

# 13. Crear superusuario
create_superuser() {
    print_header "Crear Superusuario"
    echo "Sigue las instrucciones para crear un usuario administrador..."
    echo ""
    docker compose exec django python manage.py createsuperuser
    echo ""
    print_success "Superusuario creado"
    print_info "Presiona Enter para continuar..."
    read
}

# 14. Ejecutar tests
run_tests() {
    print_header "Ejecutar Tests de Django"
    echo "Ejecutando suite de tests..."
    echo ""
    docker compose exec django python manage.py test
    echo ""
    print_info "Presiona Enter para continuar..."
    read
}

# 15. Health check
health_check() {
    print_header "Verificación de Salud del Sistema"
    if [ -f "./health-check.sh" ]; then
        ./health-check.sh
    else
        print_error "Script health-check.sh no encontrado"
        echo ""
        echo "Verificación básica:"
        docker compose ps
    fi
    echo ""
    print_info "Presiona Enter para continuar..."
    read
}

# 16. Test API
test_api() {
    print_header "Test de API"
    if [ -f "./test-api.sh" ]; then
        ./test-api.sh
    else
        print_error "Script test-api.sh no encontrado"
        echo ""
        echo "Tests manuales:"
        echo "Django Health: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health/)"
        echo "ML Service: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8001/docs)"
    fi
    echo ""
    print_info "Presiona Enter para continuar..."
    read
}

# 17. Django shell
django_shell() {
    print_header "Django Shell"
    echo "Iniciando shell interactivo de Django..."
    echo "Escribe 'exit()' para salir"
    echo ""
    docker compose exec django python manage.py shell
}

# 18. PostgreSQL shell
postgres_shell() {
    print_header "PostgreSQL Shell"
    echo "Iniciando psql..."
    echo "Escribe '\\q' para salir"
    echo ""
    docker compose exec postgres psql -U postgres -d traffic_system
}

# 19. Redis monitor
redis_monitor() {
    print_header "Redis Monitor"
    echo "Mostrando comandos en tiempo real. Presiona Ctrl+C para salir."
    echo ""
    sleep 2
    docker compose exec redis redis-cli monitor
}

# 20. Abrir URLs
open_urls() {
    print_header "URLs de Servicios"
    echo ""
    echo -e "${GREEN}Aplicaciones Principales:${NC}"
    echo "  📱 Dashboard Frontend:      http://localhost:3002/"
    echo "  🔐 Django Admin:            http://localhost:8000/admin/"
    echo "  📚 API Documentation:       http://localhost:8000/api/docs/"
    echo "  🤖 ML Service Docs:         http://localhost:8001/docs"
    echo "  ⚙️  Config Management:      http://localhost:8080/docs"
    echo ""
    echo -e "${GREEN}Herramientas de Gestión:${NC}"
    echo "  🐰 RabbitMQ Management:     http://localhost:15672/ (admin/SecurePassword123!)"
    echo "  📦 MinIO Console:           http://localhost:9001/ (admin/SecurePassword123!)"
    echo "  📊 Prometheus:              http://localhost:9090/"
    echo "  📈 Grafana:                 http://localhost:3001/ (admin/admin)"
    echo ""
    print_info "En Windows, puedes copiar y pegar estas URLs en tu navegador"
    print_info "Presiona Enter para continuar..."
    read
}

# 21. Ver recursos
show_resources() {
    print_header "Uso de Recursos"
    echo "Mostrando uso de CPU y memoria. Presiona Ctrl+C para salir."
    echo ""
    sleep 2
    docker compose stats
}

# 22. Limpiar sistema
cleanup_system() {
    print_header "Limpiar Sistema"
    echo ""
    print_warning "Esta operación puede eliminar datos. ¿Qué deseas hacer?"
    echo ""
    echo "1) Detener contenedores (mantiene datos)"
    echo "2) Eliminar contenedores (mantiene volúmenes/datos)"
    echo "3) Eliminar TODO (contenedores, volúmenes, datos)"
    echo "4) Cancelar"
    echo ""
    echo -n "Selecciona una opción: "
    read cleanup_option
    
    case $cleanup_option in
        1)
            print_info "Deteniendo contenedores..."
            docker compose stop
            print_success "Contenedores detenidos"
            ;;
        2)
            echo ""
            print_warning "¿Estás seguro? Esto eliminará los contenedores pero mantendrá los datos (s/n): "
            read confirm
            if [ "$confirm" == "s" ] || [ "$confirm" == "S" ]; then
                docker compose down
                print_success "Contenedores eliminados, datos preservados"
            else
                print_info "Operación cancelada"
            fi
            ;;
        3)
            echo ""
            print_error "¡ADVERTENCIA! Esto eliminará TODOS los datos"
            print_warning "¿Estás ABSOLUTAMENTE seguro? (escribe 'DELETE' para confirmar): "
            read confirm
            if [ "$confirm" == "DELETE" ]; then
                docker compose down -v
                print_success "Sistema completamente limpiado"
            else
                print_info "Operación cancelada"
            fi
            ;;
        4)
            print_info "Operación cancelada"
            ;;
        *)
            print_error "Opción inválida"
            ;;
    esac
    echo ""
    print_info "Presiona Enter para continuar..."
    read
}

# Main loop
main() {
    while true; do
        show_menu
        read option
        
        case $option in
            1)  show_status ;;
            2)  show_logs "django" "Django" ;;
            3)  show_logs "celery-worker" "Celery Worker" ;;
            4)  show_logs "celery-beat" "Celery Beat" ;;
            5)  show_logs "inference" "Inference Service" ;;
            6)  show_logs "frontend" "Frontend Dashboard" ;;
            7)  show_logs "config-management" "Config Management" ;;
            8)  show_logs "all" "Todos los Servicios" ;;
            9)  restart_service "django" "Django" ;;
            10) restart_service "celery" "Celery" ;;
            11) restart_service "frontend" "Frontend" ;;
            12) restart_service "config-management" "Config Management" ;;
            13) restart_service "all" "Todos los Servicios" ;;
            14) make_migrations ;;
            15) run_migrations ;;
            16) show_migrations ;;
            17) create_superuser ;;
            18) run_tests ;;
            19) health_check ;;
            20) test_api ;;
            21) django_shell ;;
            22) postgres_shell ;;
            23) redis_monitor ;;
            24) open_urls ;;
            25) show_resources ;;
            26) cleanup_system ;;
            0)  
                print_info "¡Hasta luego!"
                exit 0
                ;;
            *)  
                print_error "Opción inválida"
                sleep 1
                ;;
        esac
    done
}

# Check if docker compose is available
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado o no está en el PATH"
    exit 1
fi

# Run main
main
