# Makefile for Django Backend - Traffic Infraction Detection System
# =================================================================

.PHONY: help install setup test clean run migrate shell admin docs lint format check docker-build docker-up docker-down backup restore

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
VENV := venv
VENV_BIN := $(VENV)/bin
MANAGE := $(PYTHON) manage.py
PYTEST := pytest
BLACK := black
FLAKE8 := flake8
ISORT := isort
MYPY := mypy

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

# =================================================================
# HELP
# =================================================================

help: ## Mostrar esta ayuda
	@echo "$(BLUE)════════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Traffic Infraction Detection - Django Backend$(NC)"
	@echo "$(BLUE)════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(GREEN)Comandos disponibles:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BLUE)════════════════════════════════════════════════════════════$(NC)"

# =================================================================
# SETUP & INSTALLATION
# =================================================================

install: ## Instalar todas las dependencias
	@echo "$(BLUE)→ Instalando dependencias...$(NC)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencias instaladas$(NC)"

venv: ## Crear entorno virtual
	@echo "$(BLUE)→ Creando entorno virtual...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)✓ Entorno virtual creado en ./$(VENV)$(NC)"
	@echo "$(YELLOW)  Activar con: source $(VENV_BIN)/activate$(NC)"

setup: venv install ## Setup completo (venv + dependencias)
	@echo "$(GREEN)✓ Setup completado$(NC)"

install-dev: install ## Instalar dependencias de desarrollo
	@echo "$(BLUE)→ Instalando dependencias de desarrollo...$(NC)"
	$(PIP) install -r requirements-dev.txt 2>/dev/null || echo "No requirements-dev.txt found"
	@echo "$(GREEN)✓ Dependencias de desarrollo instaladas$(NC)"

# =================================================================
# DATABASE
# =================================================================

migrate: ## Ejecutar migraciones de base de datos
	@echo "$(BLUE)→ Ejecutando migraciones...$(NC)"
	$(MANAGE) migrate
	@echo "$(GREEN)✓ Migraciones aplicadas$(NC)"

makemigrations: ## Crear nuevas migraciones
	@echo "$(BLUE)→ Creando migraciones...$(NC)"
	$(MANAGE) makemigrations
	@echo "$(GREEN)✓ Migraciones creadas$(NC)"

showmigrations: ## Mostrar estado de migraciones
	@echo "$(BLUE)→ Estado de migraciones:$(NC)"
	$(MANAGE) showmigrations

migrate-app: ## Migrar una app específica (usar: make migrate-app APP=authentication)
	@echo "$(BLUE)→ Migrando app $(APP)...$(NC)"
	$(MANAGE) migrate $(APP)
	@echo "$(GREEN)✓ Migraciones de $(APP) aplicadas$(NC)"

reset-db: ## Resetear base de datos (CUIDADO: Borra todos los datos)
	@echo "$(RED)⚠ ADVERTENCIA: Esto borrará TODOS los datos$(NC)"
	@echo -n "¿Estás seguro? [y/N] "; \
	read respuesta; \
	if [ "$$respuesta" = "y" ] || [ "$$respuesta" = "Y" ]; then \
		echo "$(BLUE)→ Reseteando base de datos...$(NC)"; \
		python3 reset_db.py || exit 1; \
		echo "$(GREEN)✓ Base de datos reseteada$(NC)"; \
	else \
		echo "$(YELLOW)  Operación cancelada$(NC)"; \
	fi

# =================================================================
# DEVELOPMENT
# =================================================================

run: ## Iniciar servidor de desarrollo
	@echo "$(BLUE)→ Iniciando servidor en http://localhost:8000$(NC)"
	$(MANAGE) runserver

run-prod: ## Iniciar servidor con Gunicorn (producción)
	@echo "$(BLUE)→ Iniciando Gunicorn...$(NC)"
	gunicorn config.wsgi:application \
		--bind 0.0.0.0:8000 \
		--workers 4 \
		--threads 2 \
		--worker-class gthread \
		--access-logfile - \
		--error-logfile - \
		--log-level info

shell: ## Abrir shell interactivo de Django
	@echo "$(BLUE)→ Abriendo Django shell...$(NC)"
	$(MANAGE) shell

shell-plus: ## Abrir shell plus (si django-extensions está instalado)
	@echo "$(BLUE)→ Abriendo Django shell plus...$(NC)"
	$(MANAGE) shell_plus 2>/dev/null || $(MANAGE) shell

dbshell: ## Abrir shell de base de datos
	@echo "$(BLUE)→ Abriendo database shell...$(NC)"
	$(MANAGE) dbshell

admin: ## Crear superusuario
	@echo "$(BLUE)→ Creando superusuario...$(NC)"
	$(MANAGE) createsuperuser

collectstatic: ## Recopilar archivos estáticos
	@echo "$(BLUE)→ Recopilando archivos estáticos...$(NC)"
	$(MANAGE) collectstatic --noinput
	@echo "$(GREEN)✓ Archivos estáticos recopilados$(NC)"

# =================================================================
# TESTING
# =================================================================

test: ## Ejecutar todos los tests
	@echo "$(BLUE)→ Ejecutando tests...$(NC)"
	$(PYTEST) -v

test-fast: ## Ejecutar tests rápidos (sin coverage)
	@echo "$(BLUE)→ Ejecutando tests rápidos...$(NC)"
	$(PYTEST) -v -x --ff

test-cov: ## Ejecutar tests con coverage
	@echo "$(BLUE)→ Ejecutando tests con coverage...$(NC)"
	$(PYTEST) --cov=. --cov-report=term-missing --cov-report=html --cov-report=xml
	@echo "$(GREEN)✓ Coverage report generado en htmlcov/index.html$(NC)"

test-auth: ## Ejecutar tests de authentication
	@echo "$(BLUE)→ Ejecutando tests de authentication...$(NC)"
	$(PYTEST) authentication/tests/ -v

test-app: ## Ejecutar tests de una app específica (usar: make test-app APP=authentication)
	@echo "$(BLUE)→ Ejecutando tests de $(APP)...$(NC)"
	$(PYTEST) $(APP)/tests/ -v

test-watch: ## Ejecutar tests en modo watch
	@echo "$(BLUE)→ Modo watch activado (Ctrl+C para salir)...$(NC)"
	$(PYTEST) -f -v

coverage-html: test-cov ## Abrir reporte de coverage en navegador
	@echo "$(BLUE)→ Abriendo reporte de coverage...$(NC)"
	@which xdg-open > /dev/null 2>&1 && xdg-open htmlcov/index.html || \
	 which open > /dev/null 2>&1 && open htmlcov/index.html || \
	 which start > /dev/null 2>&1 && start htmlcov/index.html || \
	 echo "$(YELLOW)  Abrir manualmente: htmlcov/index.html$(NC)"

# =================================================================
# CODE QUALITY
# =================================================================

lint: ## Ejecutar linting (flake8)
	@echo "$(BLUE)→ Ejecutando flake8...$(NC)"
	$(FLAKE8) .
	@echo "$(GREEN)✓ Linting completado$(NC)"

format: ## Formatear código (black + isort)
	@echo "$(BLUE)→ Formateando código con black...$(NC)"
	$(BLACK) .
	@echo "$(BLUE)→ Ordenando imports con isort...$(NC)"
	$(ISORT) .
	@echo "$(GREEN)✓ Código formateado$(NC)"

format-check: ## Verificar formato sin cambios
	@echo "$(BLUE)→ Verificando formato...$(NC)"
	$(BLACK) --check .
	$(ISORT) --check-only .
	@echo "$(GREEN)✓ Formato verificado$(NC)"

type-check: ## Verificar tipos con mypy
	@echo "$(BLUE)→ Verificando tipos con mypy...$(NC)"
	$(MYPY) . 2>/dev/null || echo "$(YELLOW)  mypy no configurado o no instalado$(NC)"

check: lint format-check type-check ## Ejecutar todas las verificaciones
	@echo "$(GREEN)✓ Todas las verificaciones completadas$(NC)"

check-django: ## Verificar proyecto Django
	@echo "$(BLUE)→ Verificando proyecto Django...$(NC)"
	$(MANAGE) check
	@echo "$(GREEN)✓ Proyecto Django verificado$(NC)"

check-deploy: ## Verificar configuración para deploy
	@echo "$(BLUE)→ Verificando configuración de deploy...$(NC)"
	$(MANAGE) check --deploy
	@echo "$(GREEN)✓ Configuración de deploy verificada$(NC)"

# =================================================================
# DOCUMENTATION
# =================================================================

docs: ## Abrir documentación API
	@echo "$(BLUE)→ Iniciando servidor para ver docs...$(NC)"
	@echo "$(GREEN)  Swagger UI: http://localhost:8000/api/docs/$(NC)"
	@echo "$(GREEN)  ReDoc: http://localhost:8000/api/redoc/$(NC)"
	@$(MANAGE) runserver

schema: ## Generar schema OpenAPI
	@echo "$(BLUE)→ Generando schema OpenAPI...$(NC)"
	$(MANAGE) spectacular --file schema.yml
	@echo "$(GREEN)✓ Schema generado en schema.yml$(NC)"

# =================================================================
# DOCKER
# =================================================================

docker-build: ## Build imagen Docker
	@echo "$(BLUE)→ Building Docker image...$(NC)"
	docker build -t traffic-django:latest .
	@echo "$(GREEN)✓ Imagen Docker creada$(NC)"

docker-up: ## Levantar servicios con docker-compose
	@echo "$(BLUE)→ Levantando servicios...$(NC)"
	cd .. && docker-compose up -d
	@echo "$(GREEN)✓ Servicios levantados$(NC)"

docker-down: ## Detener servicios docker-compose
	@echo "$(BLUE)→ Deteniendo servicios...$(NC)"
	cd .. && docker-compose down
	@echo "$(GREEN)✓ Servicios detenidos$(NC)"

docker-logs: ## Ver logs de Django en docker
	@echo "$(BLUE)→ Mostrando logs (Ctrl+C para salir)...$(NC)"
	cd .. && docker-compose logs -f django

docker-restart: ## Reiniciar servicio Django en docker
	@echo "$(BLUE)→ Reiniciando servicio Django...$(NC)"
	cd .. && docker-compose restart django
	@echo "$(GREEN)✓ Servicio reiniciado$(NC)"

docker-shell: ## Acceder a shell del container Django
	@echo "$(BLUE)→ Accediendo a container...$(NC)"
	cd .. && docker-compose exec django bash

docker-django-shell: ## Acceder a Django shell en container
	@echo "$(BLUE)→ Accediendo a Django shell en container...$(NC)"
	cd .. && docker-compose exec django python manage.py shell

docker-migrate: ## Ejecutar migraciones en container
	@echo "$(BLUE)→ Ejecutando migraciones en container...$(NC)"
	cd .. && docker-compose exec django python manage.py migrate
	@echo "$(GREEN)✓ Migraciones aplicadas$(NC)"

docker-test: ## Ejecutar tests en container
	@echo "$(BLUE)→ Ejecutando tests en container...$(NC)"
	cd .. && docker-compose exec django pytest -v

docker-clean: ## Limpiar containers, volúmenes e imágenes
	@echo "$(RED)⚠ ADVERTENCIA: Esto eliminará containers y volúmenes$(NC)"
	@read -p "¿Continuar? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo ""; \
		echo "$(BLUE)→ Limpiando Docker...$(NC)"; \
		cd .. && docker-compose down -v; \
		docker rmi traffic-django:latest 2>/dev/null || true; \
		echo "$(GREEN)✓ Limpieza completada$(NC)"; \
	else \
		echo ""; \
		echo "$(YELLOW)  Operación cancelada$(NC)"; \
	fi

# =================================================================
# DATA MANAGEMENT
# =================================================================

seed: migrate ## Cargar datos de prueba
	@echo "$(BLUE)→ Cargando datos de prueba...$(NC)"
	$(MANAGE) loaddata fixtures/*.json 2>/dev/null || echo "$(YELLOW)  No hay fixtures para cargar$(NC)"
	@echo "$(GREEN)✓ Datos de prueba cargados$(NC)"

dump: ## Exportar datos a JSON
	@echo "$(BLUE)→ Exportando datos...$(NC)"
	mkdir -p backups
	$(MANAGE) dumpdata --indent 2 --natural-foreign --natural-primary \
		-e contenttypes -e auth.permission -e sessions \
		> backups/backup_$$(date +%Y%m%d_%H%M%S).json
	@echo "$(GREEN)✓ Datos exportados a backups/$(NC)"

backup: ## Crear backup de base de datos (PostgreSQL)
	@echo "$(BLUE)→ Creando backup de base de datos...$(NC)"
	mkdir -p backups
	@export $$(cat ../.env | grep -v '^#' | xargs) && \
	pg_dump -h $$POSTGRES_HOST -U $$POSTGRES_USER -d $$POSTGRES_DB \
		-f backups/db_backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Backup creado en backups/$(NC)"

restore: ## Restaurar backup de base de datos
	@echo "$(BLUE)→ Restaurando backup...$(NC)"
	@echo "$(YELLOW)  Archivos disponibles en backups/:$(NC)"
	@ls -1 backups/*.sql 2>/dev/null || echo "  No hay backups disponibles"
	@read -p "Nombre del archivo a restaurar: " backup_file; \
	if [ -f "backups/$$backup_file" ]; then \
		export $$(cat ../.env | grep -v '^#' | xargs) && \
		psql -h $$POSTGRES_HOST -U $$POSTGRES_USER -d $$POSTGRES_DB \
			-f "backups/$$backup_file"; \
		echo "$(GREEN)✓ Backup restaurado$(NC)"; \
	else \
		echo "$(RED)✗ Archivo no encontrado$(NC)"; \
	fi

# =================================================================
# CELERY
# =================================================================

celery-worker: ## Iniciar Celery worker
	@echo "$(BLUE)→ Iniciando Celery worker...$(NC)"
	celery -A config worker -l info

celery-beat: ## Iniciar Celery beat scheduler
	@echo "$(BLUE)→ Iniciando Celery beat...$(NC)"
	celery -A config beat -l info

celery-flower: ## Iniciar Flower (monitor de Celery)
	@echo "$(BLUE)→ Iniciando Flower en http://localhost:5555$(NC)"
	celery -A config flower

celery-purge: ## Limpiar cola de tareas
	@echo "$(BLUE)→ Limpiando cola de Celery...$(NC)"
	celery -A config purge
	@echo "$(GREEN)✓ Cola limpiada$(NC)"

# =================================================================
# UTILITIES
# =================================================================

clean: ## Limpiar archivos temporales y cache
	@echo "$(BLUE)→ Limpiando archivos temporales...$(NC)"
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '.coverage' -delete
	find . -type d -name 'htmlcov' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Limpieza completada$(NC)"

clean-logs: ## Limpiar logs
	@echo "$(BLUE)→ Limpiando logs...$(NC)"
	rm -rf logs/*.log
	@echo "$(GREEN)✓ Logs limpiados$(NC)"

deps: ## Listar dependencias instaladas
	@echo "$(BLUE)→ Dependencias instaladas:$(NC)"
	$(PIP) list

deps-outdated: ## Mostrar dependencias desactualizadas
	@echo "$(BLUE)→ Dependencias desactualizadas:$(NC)"
	$(PIP) list --outdated

deps-update: ## Actualizar requirements.txt
	@echo "$(BLUE)→ Actualizando requirements.txt...$(NC)"
	$(PIP) freeze > requirements.txt
	@echo "$(GREEN)✓ requirements.txt actualizado$(NC)"

urls: ## Mostrar todas las URLs del proyecto
	@echo "$(BLUE)→ URLs del proyecto:$(NC)"
	$(MANAGE) show_urls 2>/dev/null || \
	echo "$(YELLOW)  Instalar django-extensions para usar este comando$(NC)"

info: ## Mostrar información del proyecto
	@echo "$(BLUE)════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  PROJECT INFO$(NC)"
	@echo "$(BLUE)════════════════════════════════════════════════════════════$(NC)"
	@echo "$(YELLOW)Python version:$(NC) $$($(PYTHON) --version)"
	@echo "$(YELLOW)Django version:$(NC) $$($(PYTHON) -c 'import django; print(django.get_version())')"
	@echo "$(YELLOW)Working directory:$(NC) $$(pwd)"
	@echo "$(YELLOW)Virtual environment:$(NC) $$(if [ -d "$(VENV)" ]; then echo "Active ($(VENV))"; else echo "Not created"; fi)"
	@echo "$(BLUE)════════════════════════════════════════════════════════════$(NC)"

validate: ## Validar estructura del proyecto
	@echo "$(BLUE)→ Validando proyecto...$(NC)"
	@bash validate.sh || echo "$(YELLOW)  Ejecutar: bash validate.sh$(NC)"

# =================================================================
# QUICK COMMANDS
# =================================================================

dev: migrate run ## Setup rápido para desarrollo (migrate + run)

quick-start: install migrate admin run ## Inicio rápido completo

fresh-start: clean install migrate seed admin ## Inicio limpio con datos de prueba

ci: check test ## Comandos de CI (check + test)

all: clean install migrate collectstatic test ## Ejecutar todo el proceso

# =================================================================
# ALIASES
# =================================================================

m: migrate ## Alias para migrate
mm: makemigrations ## Alias para makemigrations
r: run ## Alias para run
s: shell ## Alias para shell
t: test ## Alias para test
tc: test-cov ## Alias para test-cov
l: lint ## Alias para lint
f: format ## Alias para format
c: check ## Alias para check

# =================================================================
# Pre-commit
# =================================================================

pre-commit-install: ## Instalar pre-commit hooks
	@echo "$(BLUE)→ Instalando pre-commit hooks...$(NC)"
	pre-commit install
	@echo "$(GREEN)✓ Pre-commit hooks instalados$(NC)"

pre-commit-run: ## Ejecutar pre-commit en todos los archivos
	@echo "$(BLUE)→ Ejecutando pre-commit...$(NC)"
	pre-commit run --all-files

# =================================================================
# END
# =================================================================
