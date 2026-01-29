@echo off
REM Script para desactivar el inicio automatico del sistema

echo ========================================
echo   Desactivando Inicio Automatico
echo ========================================
echo.

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

echo Eliminando tarea programada...
schtasks /Delete /TN "SistemaLaboratorios_Inicio" /F

if errorlevel 1 (
    echo.
    echo La tarea no existe o ya fue eliminada.
) else (
    echo.
    echo ========================================
    echo   Inicio automatico desactivado
    echo ========================================
    echo.
    echo El sistema ya no se iniciara automaticamente.
    echo.
)

pause







