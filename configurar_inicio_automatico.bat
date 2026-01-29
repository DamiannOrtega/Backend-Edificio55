@echo off
REM Script para configurar el inicio automatico del sistema
REM Crea una tarea programada en Windows para iniciar el sistema al arrancar

echo ========================================
echo   Configuracion de Inicio Automatico
echo ========================================
echo.
echo Este script configurara el sistema para que se inicie
echo automaticamente cuando Windows arranque.
echo.
echo IMPORTANTE: Este script debe ejecutarse como Administrador
echo.
pause

REM Verificar que se ejecuta como administrador
net session >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Este script debe ejecutarse como Administrador
    echo.
    echo Por favor:
    echo   1. Cierra este script
    echo   2. Haz clic derecho en este archivo
    echo   3. Selecciona "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

REM Obtener la ruta del script maestro
set "SCRIPT_PATH=%~dp0iniciar_sistema_completo.bat"

REM Verificar que el script existe
if not exist "%SCRIPT_PATH%" (
    echo ERROR: No se encontro el script iniciar_sistema_completo.bat
    echo Asegurate de que este archivo esta en el directorio raiz del proyecto
    pause
    exit /b 1
)

echo.
echo Configurando tarea programada...
echo.

REM Eliminar tarea existente si existe (ignorar errores)
schtasks /Delete /TN "SistemaLaboratorios_Inicio" /F >nul 2>&1

REM Crear nueva tarea programada
schtasks /Create /TN "SistemaLaboratorios_Inicio" /TR "\"%SCRIPT_PATH%\"" /SC ONLOGON /RL HIGHEST /F

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo crear la tarea programada
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Configuracion completada exitosamente
echo ========================================
echo.
echo El sistema se iniciara automaticamente cuando:
echo   - Windows arranque
echo   - Un usuario inicie sesion
echo.
echo La tarea se llama: SistemaLaboratorios_Inicio
echo.
echo Para desactivar el inicio automatico:
echo   1. Abre "Programador de tareas" (Task Scheduler)
echo   2. Busca "SistemaLaboratorios_Inicio"
echo   3. Haz clic derecho y selecciona "Deshabilitar" o "Eliminar"
echo.
pause







