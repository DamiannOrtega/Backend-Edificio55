@echo off
REM Script maestro para iniciar todo el sistema
REM Inicia tanto el backend Django como el frontend React en ventanas separadas

echo ========================================
echo   Iniciando Sistema Completo
echo ========================================
echo.
echo Este script abrira dos ventanas:
echo   1. Servidor Django (Backend) - Puerto 8000
echo   2. Servidor React (Frontend) - Puerto 5173
echo.
echo Para detener los servidores, cierra las ventanas o presiona Ctrl+C en cada una
echo.

REM Obtener la ruta base (directorio donde esta este script)
set "BASE_DIR=%~dp0"

REM Iniciar servidor Django en una nueva ventana
echo Iniciando servidor Django...
start "Servidor Django - Backend" cmd /k "%BASE_DIR%Backend-Edificio55\iniciar_servidor.bat"

REM Esperar un poco para que Django inicie
timeout /t 3 /nobreak >nul

REM Iniciar servidor React en una nueva ventana
echo Iniciando servidor React...
start "Servidor React - Frontend" cmd /k "%BASE_DIR%Frontend-Edificio55\iniciar_frontend.bat"

echo.
echo ========================================
echo   Sistema iniciado correctamente
echo ========================================
echo.
echo Servidores iniciados en ventanas separadas.
echo Puedes cerrar esta ventana.
echo.
echo URLs:
echo   - Backend Admin: http://127.0.0.1:8000/admin/
echo   - Frontend: http://localhost:5173/
echo.
pause







