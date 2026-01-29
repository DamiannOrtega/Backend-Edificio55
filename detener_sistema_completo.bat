@echo off
REM Script para detener todo el sistema
REM Detiene tanto el backend Django como el frontend React

echo ========================================
echo   Deteniendo Sistema Completo
echo ========================================
echo.

echo Deteniendo servidor Django...
call "%~dp0Backend-Edificio55\detener_servidor.bat"

echo.
echo Deteniendo servidor React...
call "%~dp0Frontend-Edificio55\detener_frontend.bat"

echo.
echo ========================================
echo   Sistema detenido correctamente
echo ========================================
echo.
pause







