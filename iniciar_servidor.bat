@echo off
REM Script para iniciar el servidor Django
REM Este script inicia el servidor de desarrollo de Django

echo ========================================
echo   Iniciando Servidor Django
echo ========================================
echo.

REM Cambiar al directorio del backend
cd /d "%~dp0"

REM Intentar activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
) else if exist "..\venv\Scripts\activate.bat" (
    echo Activando entorno virtual...
    call ..\venv\Scripts\activate.bat
) else (
    echo No se encontro entorno virtual, usando Python del sistema...
)

REM Verificar que Python esta disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    pause
    exit /b 1
)

REM Iniciar el servidor Django
echo.
echo Iniciando servidor Django en http://127.0.0.1:8000
echo Presiona Ctrl+C para detener el servidor
echo.
python manage.py runserver

pause



