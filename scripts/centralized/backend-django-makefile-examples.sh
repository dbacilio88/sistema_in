#!/bin/bash
# =================================================================
# EJEMPLOS DE USO DEL MAKEFILE - Django Backend
# =================================================================
# Este script contiene ejemplos de flujos de trabajo comunes
# No ejecutar directamente, usar como referencia
# =================================================================

# =================================================================
# 🆕 SETUP INICIAL - PRIMERA VEZ
# =================================================================

# Opción 1: Todo automático (Recomendado)
make quick-start
# Esto ejecuta: install + migrate + admin + run

# Opción 2: Paso a paso (Mayor control)
make venv               # Crear entorno virtual
source venv/bin/activate # Activar venv
make install            # Instalar dependencias
cp ../.env.example ../.env # Configurar variables
# Editar .env con tus valores
make migrate            # Crear tablas
make admin              # Crear superusuario
make run                # Iniciar servidor

# =================================================================
# 💼 FLUJO DE TRABAJO DIARIO
# =================================================================

# Inicio del día
cd /home/bacsystem/github.com/sistema_in/backend-django
source venv/bin/activate  # Si no está activado

# Actualizar código
git pull origin main
make install              # Por si hay nuevas dependencias
make migrate              # Por si hay nuevas migraciones

# Iniciar desarrollo
make dev                  # migrate + run

# En otra terminal: Tests en watch mode
make test-watch

# En otra terminal: Celery worker (si es necesario)
make celery-worker

# =================================================================
# 🔨 DESARROLLO DE FEATURES
# =================================================================

# 1. Crear nueva rama
git checkout -b feature/nueva-funcionalidad

# 2. Hacer cambios en modelos
# ... editar models.py ...

# 3. Crear y aplicar migraciones
make mm                   # makemigrations
make m                    # migrate

# 4. Ejecutar tests mientras desarrollas
make test-watch           # O en otra terminal

# 5. Escribir tests
# ... editar tests/test_nueva_feature.py ...

# 6. Verificar tests
make test-cov             # Con coverage
make coverage-html        # Ver en navegador

# 7. Antes de commit: Code quality
make format               # Formatear código
make lint                 # Verificar linting
make check                # Verificar todo

# 8. Commit y push
git add .
git commit -m "feat: nueva funcionalidad"
git push origin feature/nueva-funcionalidad

# =================================================================
# 🧪 TESTING EXHAUSTIVO
# =================================================================

# Tests básicos
make test                 # Todos los tests
make test-fast            # Sin coverage (rápido)
make test-cov             # Con coverage completo

# Tests específicos
make test-auth            # Solo authentication
make test-app APP=devices # App específica

# Ver resultados
make coverage-html        # Abrir reporte HTML

# Tests en CI (como en GitHub Actions)
make ci                   # check + test

# =================================================================
# 🔍 DEBUGGING
# =================================================================

# Shell interactivo para probar código
make shell
# >>> from authentication.models import User
# >>> User.objects.all()
# >>> exit()

# Shell de base de datos
make dbshell
# postgres=# \dt
# postgres=# SELECT * FROM users;
# postgres=# \q

# Ver todas las URLs
make urls

# Verificar configuración
make check-django
make check-deploy

# =================================================================
# 📊 BASE DE DATOS
# =================================================================

# Crear migraciones
make makemigrations
make mm                   # Alias corto

# Aplicar migraciones
make migrate
make m                    # Alias corto

# Migración de app específica
make migrate-app APP=authentication

# Ver estado de migraciones
make showmigrations

# Cargar datos de prueba
make seed

# Backup antes de cambios importantes
make backup               # Crea SQL dump

# Si algo sale mal, restaurar
make restore              # Interactivo

# Export/Import en JSON
make dump                 # Exporta todo a JSON
# ... editar backup JSON si es necesario ...
# Luego importar manualmente

# =================================================================
# 🐳 DESARROLLO CON DOCKER
# =================================================================

# Primera vez con Docker
cd ..  # Ir a raíz del proyecto
make docker-up            # Levantar todos los servicios
make docker-migrate       # Crear tablas

# Ver logs
make docker-logs          # Logs de Django

# Entrar al container
make docker-shell         # Bash
make docker-django-shell  # Django shell

# Ejecutar comandos en container
make docker-migrate       # Migraciones
make docker-test          # Tests

# Reiniciar servicio
make docker-restart

# Detener todo
make docker-down

# Limpieza completa (⚠️ borra datos)
make docker-clean

# =================================================================
# 🚀 PREPARACIÓN PARA PRODUCCIÓN
# =================================================================

# 1. Verificar que todo funciona
make check-deploy         # Verificaciones de seguridad
make test-cov             # Tests completos

# 2. Actualizar dependencias
make deps-outdated        # Ver qué está desactualizado
# Actualizar requirements.txt manualmente si es necesario

# 3. Limpiar código
make format
make lint
make check

# 4. Recopilar estáticos
make collectstatic

# 5. Build Docker image para producción
make docker-build

# 6. Test producción local
make run-prod             # Con Gunicorn

# =================================================================
# 🔄 CELERY TASKS
# =================================================================

# Terminal 1: Django
make run

# Terminal 2: Celery Worker
make celery-worker

# Terminal 3: Celery Beat (tareas programadas)
make celery-beat

# Terminal 4: Flower (monitor)
make celery-flower
# Abrir http://localhost:5555

# Limpiar cola si hay problemas
make celery-purge

# =================================================================
# 🧹 MANTENIMIENTO
# =================================================================

# Limpieza regular
make clean                # __pycache__, .pyc, etc.
make clean-logs           # Logs antiguos

# Actualizar dependencias
make deps-outdated        # Ver cuáles están viejas
# Editar requirements.txt
make install              # Reinstalar

# Validar estructura
make validate             # Ejecuta validate.sh

# Info del proyecto
make info                 # Versiones, paths, etc.

# =================================================================
# 🐛 TROUBLESHOOTING COMÚN
# =================================================================

# Error: ModuleNotFoundError
make clean
make install
# Verificar que venv esté activado

# Error: Database connection
# 1. Verificar que PostgreSQL esté corriendo
# 2. Verificar variables en .env
make check-django

# Error: Migrations conflict
make showmigrations       # Ver estado
# Si hay conflictos:
# python manage.py migrate --merge
make migrate

# Error: Tests failing
make clean                # Limpiar cache
make test-fast            # Ver primer error
# Corregir y volver a probar

# Error: Port already in use
# Encontrar proceso usando puerto 8000
# Linux: sudo lsof -i :8000
# Matar proceso o usar otro puerto
# python manage.py runserver 8001

# =================================================================
# 📝 COMBINACIONES ÚTILES
# =================================================================

# Reinicio completo
make clean install migrate seed admin run

# Preparar para PR
make format lint test-cov

# CI local (simular GitHub Actions)
make clean install check test

# Desarrollo rápido (después de cambios en models)
make mm m run             # makemigrations + migrate + run

# Update después de git pull
make install migrate run

# Fresh start completo
make fresh-start          # clean + install + migrate + seed + admin

# =================================================================
# 🎯 FLUJOS ESPECÍFICOS
# =================================================================

# === AÑADIR NUEVA APP ===
python manage.py startapp nueva_app
# Añadir a INSTALLED_APPS en settings.py
# Crear modelos
make mm m                 # Crear y aplicar migraciones
make test                 # Verificar

# === CAMBIAR MODELOS ===
# 1. Editar models.py
make mm                   # Crear migración
make m                    # Aplicar
make test                 # Verificar que tests pasen

# === CREAR ENDPOINT ===
# 1. Crear serializer
# 2. Crear view
# 3. Añadir URL
make test                 # Escribir y ejecutar tests
make run                  # Probar manualmente
# Abrir http://localhost:8000/api/docs/

# === DEBUGGING PRODUCCIÓN ===
DEBUG=False make run-prod # Simular producción
make check-deploy         # Verificaciones de seguridad

# === PERFORMANCE TESTING ===
make run-prod             # Gunicorn
# En otra terminal:
# ab -n 1000 -c 10 http://localhost:8000/health/

# =================================================================
# 💡 TIPS Y TRUCOS
# =================================================================

# Usar alias de shell
alias m='make'
alias mr='make run'
alias mt='make test'
# Ahora: m r, m t, etc.

# Multiple commands
make clean install migrate test

# Background processes
make run &                # Servidor en background
make celery-worker &      # Worker en background
# Matar con: jobs, fg, Ctrl+C

# Watch logs
make docker-logs          # Ctrl+C para salir

# Quick shell para queries
make shell <<EOF
from authentication.models import User
print(User.objects.count())
EOF

# Export variables from .env
export $(cat ../.env | grep -v '^#' | xargs)
echo $POSTGRES_HOST

# =================================================================
# 🔐 SEGURIDAD
# =================================================================

# Antes de deploy
make check-deploy         # Verificaciones Django
make test                 # Todos los tests

# Verificar secrets
cat ../.env | grep -i secret
# Asegurar que no están en git
cat ../.gitignore | grep .env

# Actualizar dependencias por seguridad
make deps-outdated
# Revisar CVEs en dependencias
# pip install safety
# safety check

# =================================================================
# 📊 MONITORING EN DESARROLLO
# =================================================================

# Terminal 1: Server
make run

# Terminal 2: Logs
tail -f logs/django.log

# Terminal 3: Tests watch
make test-watch

# Terminal 4: Celery
make celery-worker

# Terminal 5: Database
make dbshell

# =================================================================
# FIN DE EJEMPLOS
# =================================================================

echo "
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║  Para más información:                                ║
║  - make help          (lista completa de comandos)    ║
║  - MAKEFILE_GUIDE.md  (guía detallada)               ║
║  - README.md          (documentación del proyecto)    ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
"
