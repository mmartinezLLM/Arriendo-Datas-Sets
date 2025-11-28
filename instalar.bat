@echo off
REM Script de instalación y ejecución para Windows
REM Este script configura todo el entorno necesario

setlocal enabledelayedexpansion

echo.
echo ======================================================================
echo    SCRAPER DE INMOBILIARIAS - FINCARAIZ.COM.CO
echo    Instalador para Windows
echo ======================================================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no está instalado o no está en el PATH
    echo.
    echo Por favor, instala Python desde: https://www.python.org
    echo Asegúrate de marcar "Add Python to PATH" durante la instalación
    echo.
    pause
    exit /b 1
)

echo ✓ Python encontrado
python --version

echo.
echo ======================================================================
echo PASO 1: Instalando dependencias...
echo ======================================================================
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ ERROR al instalar dependencias
    echo Intenta ejecutar: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ✓ Dependencias instaladas correctamente
echo.

echo ======================================================================
echo PASO 2: Selecciona qué deseas hacer
echo ======================================================================
echo.
echo 1. Inspeccionar estructura de la página
echo 2. Ejecutar scraper de inmobiliarias
echo 3. Ambas (primero inspecciona, luego scraped)
echo 4. Solo instalar (salir sin ejecutar)
echo.

set /p choice="Opción (1-4): "

if "%choice%"=="1" (
    echo.
    echo Ejecutando inspector de selectores...
    echo.
    python selector_inspector.py
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Ejecutando scraper...
    echo.
    python main_fincaraiz.py
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Ejecutando inspector...
    echo.
    python selector_inspector.py
    echo.
    echo Presiona cualquier tecla para continuar con el scraper...
    pause
    echo.
    echo Ejecutando scraper...
    echo.
    python main_fincaraiz.py
    goto end
)

if "%choice%"=="4" (
    echo.
    echo ✓ Instalación completada. Puedes ejecutar los scripts manualmente.
    echo.
    goto end
)

echo.
echo ❌ Opción no válida
echo.

:end
echo.
echo ======================================================================
echo Los datos se guardan en: resultados/
echo Los logs se encuentran en: resultados/scraper.log
echo ======================================================================
echo.
pause
