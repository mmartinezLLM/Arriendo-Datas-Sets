@echo off
REM Script maestro para ejecutar todos los lotes secuencialmente
REM Procesa 277,953 URLs divididas en 10 lotes

echo ================================================================================
echo PROCESAMIENTO MASIVO DE 277,953 INMUEBLES EN 10 LOTES
echo ================================================================================
echo.
echo Este script procesara todos los lotes secuencialmente.
echo Cada lote contiene ~27,795 URLs.
echo.
echo IMPORTANTE:
echo - El proceso puede tardar VARIOS DIAS
echo - Puedes interrumpir con Ctrl+C y retomar despues
echo - El progreso se guarda automaticamente cada 100 URLs
echo.
pause

cd /d "%~dp0"

FOR /L %%i IN (1,1,10) DO (
    echo.
    echo ================================================================================
    echo INICIANDO LOTE %%i/10
    echo ================================================================================
    echo.
    
    python procesar_lote.py %%i
    
    if errorlevel 1 (
        echo.
        echo ERROR: El lote %%i fallo. Revisa los logs.
        echo.
        pause
        exit /b 1
    )
    
    echo.
    echo ================================================================================
    echo LOTE %%i/10 COMPLETADO
    echo ================================================================================
    echo.
    
    REM Pausa de 1 minuto entre lotes
    echo Esperando 1 minuto antes del siguiente lote...
    timeout /t 60 /nobreak
)

echo.
echo ================================================================================
echo TODOS LOS LOTES COMPLETADOS
echo ================================================================================
echo.
echo Revisa los resultados en: resultados/lotes/lote_XX/
echo.
pause
