# 🚀 Instalación Manual - Backend Django

## El error que tienes:

```
ModuleNotFoundError: No module named 'environ'
```

**Causa**: No están instaladas las dependencias de Python.

---

## ✅ Solución Rápida (Copia y pega estos comandos)

### En terminal de WSL/Linux:

```bash
# 1. Ir al directorio backend
cd ~/github.com/sistema_in/backend-django

# 2. Instalar dependencias
pip3 install -r requirements.txt

# 3. Ejecutar migraciones
python3 manage.py migrate

# 4. Inicializar base de datos
python3 init_database.py

# 5. Iniciar servidor
python3 manage.py runserver
```

---

## 📦 Instalación Completa (Recomendada)

### Opción 1: Script Automático

```bash
# En la raíz del proyecto
chmod +x install-backend.sh
./install-backend.sh
```

### Opción 2: Paso a Paso

```bash
# 1. Ir a backend-django
cd backend-django

# 2. Crear entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate

# 3. Actualizar pip
pip install --upgrade pip

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Verificar instalación
python -c "import django; import environ; print('✅ Paquetes instalados')"

# 6. Iniciar PostgreSQL (si no está corriendo)
cd ..
docker-compose up -d postgres
cd backend-django

# 7. Ejecutar migraciones
python manage.py migrate

# 8. Crear superusuario
python manage.py createsuperuser
# Username: admin
# Email: admin@traffic.pe  
# Password: admin123

# 9. Inicializar datos
python init_database.py

# 10. Iniciar servidor
python manage.py runserver
```

---

## 🐛 Si hay errores

### Error: `pip3: command not found`

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip

# Verificar
pip3 --version
```

### Error: `python3: command not found`

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Verificar
python3 --version
```

### Error: `psycopg2` no compila

```bash
# Instalar dependencias del sistema
sudo apt install libpq-dev python3-dev

# Reinstalar
pip3 install psycopg2-binary
```

### Error: Conexión a PostgreSQL

```bash
# Verificar que PostgreSQL está corriendo
docker ps | grep postgres

# Si no está corriendo
docker-compose up -d postgres

# Esperar 10 segundos
sleep 10

# Verificar conexión
python3 manage.py dbshell
# Si conecta, escribe \q para salir
```

---

## 📋 Dependencias Clave

Estas son las dependencias principales que se instalarán:

```
Django==4.2.11                 # Framework web
djangorestframework==3.14.0     # REST API
django-environ==0.11.2          # Variables de entorno
psycopg2-binary==2.9.9          # Conector PostgreSQL
django-cors-headers==4.3.1      # CORS para frontend
redis==5.0.3                    # Cache
celery==5.3.6                   # Tareas asíncronas
drf-spectacular==0.27.2         # Documentación API
```

**Total**: ~50 paquetes (~500MB)

**Tiempo**: 3-5 minutos

---

## ✅ Verificar que Todo Funciona

```bash
cd backend-django

# Test 1: Verificar Django
python3 manage.py check
# Debe decir: System check identified no issues (0 silenced).

# Test 2: Listar migraciones
python3 manage.py showmigrations
# Debe mostrar lista de migraciones con [X]

# Test 3: Conectar a BD
python3 manage.py dbshell
# Si conecta, escribe \q para salir

# Test 4: Iniciar servidor
python3 manage.py runserver
# Debe iniciar en http://127.0.0.1:8000/

# Test 5: Probar API (en otra terminal)
curl http://localhost:8000/api/
```

---

## 🎯 Resultado Final

Después de la instalación exitosa verás:

```
System check identified no issues (0 silenced).
November 04, 2025 - 23:30:00
Django version 4.2.11, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Y en el navegador:
- http://localhost:8000/admin/ → Panel de administración
- http://localhost:8000/api/ → API REST

---

## 💡 Tips

### Usar entorno virtual (recomendado)

```bash
# Crear
python3 -m venv venv

# Activar (Linux/Mac)
source venv/bin/activate

# Activar (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Desactivar
deactivate
```

### Sin entorno virtual (más simple pero no recomendado)

```bash
# Instalar globalmente
pip3 install -r requirements.txt
```

### Verificar paquete específico

```bash
# Ver si está instalado
pip3 show django-environ

# Ver versión
python3 -c "import environ; print(environ.__version__)"
```

---

## 🆘 Ayuda Rápida

### Todos los comandos en uno:

```bash
cd ~/github.com/sistema_in/backend-django && \
pip3 install -r requirements.txt && \
python3 manage.py migrate && \
python3 init_database.py && \
python3 manage.py runserver
```

### Reinstalar todo desde cero:

```bash
cd backend-django
pip3 uninstall -r requirements.txt -y
pip3 install -r requirements.txt
python3 manage.py migrate
python3 init_database.py
```

---

**¿Sigue sin funcionar?**

Comparte el error completo y te ayudaré específicamente! 🚀
