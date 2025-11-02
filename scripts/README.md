# 🚀 Scripts Centralizados - Sistema de Detección de Infracciones de Tráfico

## 🎯 Nueva Estructura Centralizada de Scripts

Todos los scripts shell (`.sh`) del proyecto han sido reorganizados en una estructura centralizada para mayor organización y mantenimiento.

### 📁 Estructura Actual

```
scripts/
└── centralized/           # 🚀 Todos los scripts en un solo lugar
    ├── README.md                             # 📋 Este archivo de documentación
    │
    ├── 🔧 SCRIPTS PRINCIPALES DEL PROYECTO:
    ├── health-check.sh                       # 🏥 Verificación de salud del sistema
    ├── check_inference.sh                    # 🔍 Verificar servicio de inferencia
    ├── start-local.sh                        # 🚀 Iniciar entorno local
    ├── stop-local.sh                         # 🛑 Detener entorno local
    ├── quick_check.sh                        # ⚡ Verificación rápida del sistema
    ├── diagnose_ml.sh                        # 🤖 Diagnóstico de ML
    ├── start_ml_detection.sh                 # 🤖 Iniciar detección ML
    ├── verify_ml.sh                          # ✅ Verificar servicios ML
    ├── test-api.sh                           # 🧪 Pruebas de API
    ├── test_login.sh                         # 🔐 Pruebas de login
    ├── helper.sh                             # 🛠️ Funciones auxiliares
    │
    ├── 📦 SCRIPTS DE BACKEND (Django):
    ├── backend-django-entrypoint.sh          # 🚪 Punto de entrada del contenedor
    ├── backend-django-makefile-examples.sh   # 📘 Ejemplos de Makefile
    ├── backend-django-migrate.sh             # 📊 Migración de base de datos
    ├── backend-django-validate.sh            # ✅ Validación del backend
    ├── backend-django-verify_setup.sh        # 🔧 Verificar configuración
    │
    ├── 🤖 SCRIPTS DE ML SERVICE:
    ├── ml-service-validate_speed.sh          # 🏎️ Validar velocidad de ML
    │
    ├── 🏗️ SCRIPTS DE INFRAESTRUCTURA:
    ├── infrastructure-postgres-01-init.sh    # 🗄️ Inicialización de PostgreSQL
    │
    ├── 🎨 SCRIPTS DE FRONTEND:
    ├── frontend-dashboard-start-dashboard.sh # 🖥️ Iniciar dashboard
    │
    └── 🧪 SCRIPTS DE TESTING:
        └── tests-setup-testing.sh            # 🧪 Configurar entorno de pruebas
```

## 🔧 Categorías de Scripts

### 🚀 **Scripts de Sistema Principal**
Scripts para el manejo general del sistema:

| Script | Descripción | Uso |
|--------|-------------|-----|
| `health-check.sh` | Verificación de salud general | `./health-check.sh` |
| `start-local.sh` | Iniciar todos los servicios localmente | `./start-local.sh` |
| `stop-local.sh` | Detener todos los servicios | `./stop-local.sh` |
| `quick_check.sh` | Verificación rápida del estado | `./quick_check.sh` |
| `helper.sh` | Funciones auxiliares compartidas | `source ./helper.sh` |

### 🤖 **Scripts de Machine Learning**
Scripts específicos para servicios de ML:

| Script | Descripción | Uso |
|--------|-------------|-----|
| `start_ml_detection.sh` | Iniciar servicio de detección ML | `./start_ml_detection.sh` |
| `diagnose_ml.sh` | Diagnóstico de problemas ML | `./diagnose_ml.sh` |
| `verify_ml.sh` | Verificar que ML funciona | `./verify_ml.sh` |
| `check_inference.sh` | Verificar servicio de inferencia | `./check_inference.sh` |
| `ml-service-validate_speed.sh` | Validar velocidad de ML | `./ml-service-validate_speed.sh` |

### 🧪 **Scripts de Testing**
Scripts para pruebas y validación:

| Script | Descripción | Uso |
|--------|-------------|-----|
| `test-api.sh` | Pruebas de API REST | `./test-api.sh` |
| `test_login.sh` | Pruebas de autenticación | `./test_login.sh` |
| `tests-setup-testing.sh` | Configurar entorno de testing | `./tests-setup-testing.sh` |

### 📦 **Scripts de Backend (Django)**
Scripts específicos del backend Django:

| Script | Descripción | Uso |
|--------|-------------|-----|
| `backend-django-entrypoint.sh` | Punto de entrada del contenedor | `./backend-django-entrypoint.sh` |
| `backend-django-migrate.sh` | Ejecutar migraciones | `./backend-django-migrate.sh` |
| `backend-django-validate.sh` | Validar configuración | `./backend-django-validate.sh` |
| `backend-django-verify_setup.sh` | Verificar setup | `./backend-django-verify_setup.sh` |
| `backend-django-makefile-examples.sh` | Ejemplos Makefile | `./backend-django-makefile-examples.sh` |

### 🏗️ **Scripts de Infraestructura**
Scripts para configuración de infraestructura:

| Script | Descripción | Uso |
|--------|-------------|-----|
| `infrastructure-postgres-01-init.sh` | Inicializar PostgreSQL | `./infrastructure-postgres-01-init.sh` |

### 🎨 **Scripts de Frontend**
Scripts del frontend dashboard:

| Script | Descripción | Uso |
|--------|-------------|-----|
| `frontend-dashboard-start-dashboard.sh` | Iniciar dashboard | `./frontend-dashboard-start-dashboard.sh` |

## 🚀 Uso Rápido

### 🎬 Scripts de Inicio Rápido
```bash
# Navegar a scripts centralizados
cd scripts/centralized

# Iniciar sistema completo
./start-local.sh

# Verificar que todo funciona
./health-check.sh

# Iniciar solo ML
./start_ml_detection.sh

# Verificar ML específicamente
./verify_ml.sh
```

### 🔧 Scripts de Desarrollo
```bash
# Verificación rápida durante desarrollo
./quick_check.sh

# Ejecutar migraciones
./backend-django-migrate.sh

# Validar configuración
./backend-django-validate.sh
```

### 🧪 Scripts de Testing
```bash
# Configurar entorno de pruebas
./tests-setup-testing.sh

# Probar API
./test-api.sh

# Probar login
./test_login.sh
```

## 📱 Acceso desde VS Code

```bash
# Navegar a scripts
cd scripts/centralized

# Ver todos los scripts
ls -la

# Hacer ejecutable (si es necesario)
chmod +x *.sh

# Ejecutar script específico
./health-check.sh
```

## 🎯 Beneficios de la Centralización

### ✅ Ventajas
1. **📁 Organización Clara**: Todos los scripts en un solo directorio
2. **🔍 Búsqueda Eficiente**: No hay que buscar en múltiples carpetas
3. **📝 Mantenimiento Fácil**: Un solo lugar para actualizar scripts
4. **🏷️ Nomenclatura Consistente**: Prefijos claros por servicio
5. **🚀 Ejecución Centralizada**: Punto único para todos los scripts
6. **📚 Documentación Unificada**: Este README como referencia

### 🎨 Código Más Limpio
- ❌ **Antes**: Scripts dispersos en 7+ carpetas diferentes
- ✅ **Ahora**: 1 carpeta centralizada con 20 scripts organizados

## 🔄 Migración Completada

- ✅ **20 scripts shell** movidos exitosamente desde:
  - ✅ Raíz del proyecto (12 scripts)
  - ✅ Carpeta `backend-django/` (5 scripts)
  - ✅ Carpeta `ml-service/scripts/` (1 script)
  - ✅ Carpeta `infrastructure/postgres/init/` (1 script)
  - ✅ Carpeta `tests/` (1 script)
  - ✅ Carpeta `frontend-dashboard/` (1 script)
- ✅ **Estructura limpia** implementada
- ✅ **Nomenclatura consistente** aplicada
- ✅ **Documentación completa** creada

## 🔗 Referencias Útiles

### 📋 Scripts Más Utilizados
```bash
# Top 5 scripts para desarrollo diario:
./start-local.sh           # Iniciar todo
./health-check.sh          # Verificar estado
./start_ml_detection.sh    # Iniciar ML
./quick_check.sh           # Check rápido
./stop-local.sh           # Detener todo
```

### 🚨 Scripts de Emergencia
```bash
# Para troubleshooting:
./diagnose_ml.sh          # Diagnosticar ML
./verify_ml.sh            # Verificar ML
./backend-django-verify_setup.sh  # Verificar backend
```

---

**Última actualización:** 2 de Noviembre, 2025  
**Mantenido por:** Sistema de Detección de Infracciones de Tráfico  
**Ubicación:** `scripts/centralized/`