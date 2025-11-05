@echo off
REM Script de Windows para inicializar la base de datos
REM Ejecutar desde la raíz del proyecto: .\setup-database-windows.bat

echo ==========================================
echo INICIALIZACION DE BASE DE DATOS
echo ==========================================
echo.

REM Verificar Docker
echo [1/4] Verificando Docker...
docker ps >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Docker no esta corriendo
    echo Inicia Docker Desktop primero
    pause
    exit /b 1
)
echo OK: Docker esta corriendo
echo.

REM Verificar PostgreSQL
echo [2/4] Verificando PostgreSQL...
docker ps | findstr postgres >nul
if %ERRORLEVEL% NEQ 0 (
    echo Iniciando PostgreSQL...
    docker-compose up -d postgres
    timeout /t 5 >nul
)
echo OK: PostgreSQL corriendo
echo.

REM Cambiar al directorio backend-django
cd backend-django
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se encontro el directorio backend-django
    pause
    exit /b 1
)

REM Ejecutar script de inicializacion
echo [3/4] Inicializando base de datos...
python init_database.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Fallo la inicializacion
    echo Verifica que Python este instalado: python --version
    pause
    exit /b 1
)
echo.

REM Verificar
echo [4/4] Verificando instalacion...
curl -s http://localhost:8000/api/health/ >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo OK: Backend respondiendo
) else (
    echo NOTA: Backend no esta corriendo
    echo Inicia con: python manage.py runserver
)

echo.
echo ==========================================
echo INICIALIZACION COMPLETA
echo ==========================================
echo.
echo Credenciales:
echo   Usuario: admin
echo   Password: admin123
echo.
echo URLs:
echo   Admin: http://localhost:8000/admin/
echo   API:   http://localhost:8000/api/
echo.
echo Proximo paso:
echo   cd backend-django
echo   python manage.py runserver
echo.
pause
