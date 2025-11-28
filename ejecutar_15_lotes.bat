@echo off
setlocal enabledelayedexpansion

set "PYTHON=C:\Users\Miguel Martinez SSD\OneDrive - BROWSER TRAVEL SOLUTIONS S.A.S VIAJEMOS\Documentos\PROYECTOS\ARRIENDO DATA SETS\.venv\Scripts\python.exe"
set "WORK=c:\Users\Miguel Martinez SSD\OneDrive - BROWSER TRAVEL SOLUTIONS S.A.S VIAJEMOS\Documentos\PROYECTOS\ARRIENDO DATA SETS\scraper_inmobiliarios"

cd /d "%WORK%"

echo ================================================
echo EJECUTANDO 15 LOTES EN PARALELO
echo ================================================

for /L %%i in (1,1,15) do (
    start "Lote %%i" "%PYTHON%" procesar_lote_limpio.py %%i
    timeout /t 1 /nobreak > nul
)

echo 15 lotes iniciados en paralelo
echo ================================================
