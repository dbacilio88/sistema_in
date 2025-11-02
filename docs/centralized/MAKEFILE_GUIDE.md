# 🚀 Guía Rápida - Makefile Django Backend

## 📋 Comandos Más Usados

### 🆕 Primer Setup (Primera vez)

```bash
# Opción 1: Setup completo automático
make quick-start

# Opción 2: Paso a paso
make setup          # Crear venv + instalar dependencias
make migrate        # Aplicar migraciones
make admin          # Crear superusuario
make run            # Iniciar servidor
```

---

## 🏃 Desarrollo Diario

### Iniciar Desarrollo
```bash
make dev            # migrate + run (lo más común)
make run            # Solo servidor (alias: make r)
```

### Shell Interactivo
```bash
make shell          # Django shell (alias: make s)
make dbshell        # PostgreSQL shell
```

### Migraciones
```bash
make mm             # makemigrations (crear)
make m              # migrate (aplicar)
make showmigrations # Ver estado
```

---

## 🧪 Testing

```bash
make test           # Todos los tests (alias: make t)
make test-cov       # Con coverage (alias: make tc)
make test-auth      # Solo authentication
make test-fast      # Rápido sin coverage

# Tests de una app específica
make test-app APP=devices
```

### Ver Coverage
```bash
make coverage-html  # Abre reporte en navegador
```

---

## 🎨 Calidad de Código

```bash
make format         # Formatear código (black + isort) (alias: make f)
make lint           # Verificar con flake8 (alias: make l)
make check          # Todo: lint + format + types (alias: make c)
make check-django   # Verificar proyecto Django
```

---

## 🐳 Docker

### Comandos Básicos
```bash
make docker-up      # Levantar todos los servicios
make docker-down    # Detener servicios
make docker-logs    # Ver logs de Django
make docker-restart # Reiniciar Django
```

### En Container
```bash
make docker-shell         # Bash en container
make docker-django-shell  # Django shell en container
make docker-migrate       # Migraciones en container
make docker-test          # Tests en container
```

### Build
```bash
make docker-build   # Construir imagen
make docker-clean   # Limpiar todo (⚠️ cuidado)
```

---

## 💾 Base de Datos

### Migraciones
```bash
make migrate              # Aplicar todas
make migrate-app APP=auth # App específica
make showmigrations       # Ver estado
```

### Backup & Restore
```bash
make backup     # Backup PostgreSQL
make restore    # Restaurar backup
make dump       # Exportar a JSON
make seed       # Cargar fixtures
```

### Reset (⚠️ Peligroso)
```bash
make reset-db   # Borrar todos los datos
```

---

## 🔧 Utilidades

### Información
```bash
make info       # Info del proyecto
make deps       # Listar dependencias
make urls       # Ver todas las URLs
make validate   # Validar estructura
```

### Limpieza
```bash
make clean      # Limpiar __pycache__, .pyc
make clean-logs # Limpiar logs
```

### Dependencias
```bash
make install          # Instalar deps
make deps-outdated    # Ver desactualizadas
make deps-update      # Actualizar requirements.txt
```

---

## 📚 Documentación

```bash
make docs       # Ver docs (Swagger + ReDoc)
make schema     # Generar schema OpenAPI
```

Endpoints:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

---

## 🔄 Celery

```bash
make celery-worker  # Iniciar worker
make celery-beat    # Iniciar beat scheduler
make celery-flower  # Monitor (Flower)
make celery-purge   # Limpiar cola
```

---

## 🚀 Comandos Rápidos Combinados

### Desarrollo
```bash
make dev            # migrate + run
make quick-start    # install + migrate + admin + run
make fresh-start    # clean + install + migrate + seed + admin
```

### CI/CD
```bash
make ci             # check + test (para CI)
make all            # clean + install + migrate + collectstatic + test
```

---

## 📝 Alias Cortos

| Alias | Comando Completo |
|-------|------------------|
| `make m` | `make migrate` |
| `make mm` | `make makemigrations` |
| `make r` | `make run` |
| `make s` | `make shell` |
| `make t` | `make test` |
| `make tc` | `make test-cov` |
| `make l` | `make lint` |
| `make f` | `make format` |
| `make c` | `make check` |

---

## 🎯 Casos de Uso Comunes

### 1️⃣ Primera vez en el proyecto
```bash
make quick-start
# Responder preguntas del superusuario
```

### 2️⃣ Día de trabajo normal
```bash
# Mañana
make dev

# Antes de commit
make format
make test
```

### 3️⃣ Después de pull
```bash
make install    # Por si hay nuevas deps
make migrate    # Nuevas migraciones
make run
```

### 4️⃣ Crear nueva app
```bash
python manage.py startapp mi_app
make mm         # Crear migraciones
make m          # Aplicar migraciones
make test       # Verificar
```

### 5️⃣ Testing
```bash
# Durante desarrollo
make test-watch

# Antes de PR
make test-cov
make coverage-html
```

### 6️⃣ Con Docker
```bash
# Setup inicial
make docker-up
make docker-migrate

# Trabajo diario
make docker-logs     # En una terminal
make docker-shell    # Para comandos
```

### 7️⃣ Producción local (simular)
```bash
make collectstatic
make run-prod
```

---

## ⚠️ Comandos Peligrosos

Estos comandos **borran datos**, úsalos con cuidado:

```bash
make reset-db       # Borra todos los datos de DB
make docker-clean   # Elimina containers y volúmenes
make fresh-start    # Limpia todo y empieza de cero
```

---

## 💡 Tips

### Ver ayuda completa
```bash
make help
# o simplemente
make
```

### Ejecutar múltiples comandos
```bash
make clean install migrate test
```

### Variables personalizadas
```bash
# Migrar app específica
make migrate-app APP=authentication

# Test app específica
make test-app APP=devices
```

### En WSL/Windows
```bash
# Desde PowerShell
wsl make dev

# Desde WSL
cd /home/bacsystem/github.com/sistema_in/backend-django
make dev
```

---

## 🔍 Troubleshooting

### No encuentra make
```bash
# En WSL/Linux
sudo apt-get install make

# Verificar
make --version
```

### Permisos en scripts
```bash
chmod +x validate.sh
chmod +x verify_setup.sh
```

### Python no encontrado
```bash
# Editar Makefile, cambiar línea 9:
PYTHON := python    # En lugar de python3
```

### Virtual env no funciona
```bash
make clean
make setup
source venv/bin/activate
```

---

## 📖 Más Información

- **README.md**: Documentación completa del proyecto
- **VALIDATION_REPORT.md**: Reporte de validación
- **validate.sh**: Script de validación completo

---

## 🎉 Atajos Recomendados

Añade estos alias a tu `.bashrc` o `.zshrc`:

```bash
alias m='make'
alias mr='make run'
alias mt='make test'
alias mm='make migrate'

# Ahora puedes usar:
# m r    → make run
# m t    → make test
# m mm   → make migrate
```

---

**Última actualización**: 2025-11-01  
**Versión Makefile**: 1.0.0
