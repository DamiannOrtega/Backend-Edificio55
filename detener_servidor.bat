@echo off
REM Script para detener el servidor Django
REM Mata todos los procesos de Python que estan ejecutando manage.py runserver

echo ========================================
echo   Deteniendo Servidor Django
echo ========================================
echo.

REM Buscar y matar procesos de Python ejecutando runserver
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| findstr /C:"PID:"') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM Tambien buscar procesos de pythonw.exe
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq pythonw.exe" /FO LIST ^| findstr /C:"PID:"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo Servidor Django detenido.
echo.
pause







