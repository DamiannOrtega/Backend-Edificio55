@echo off
REM Script para verificar que todo este configurado correctamente

echo ========================================
echo   Verificacion de Configuracion
echo ========================================
echo.

set "ERRORES=0"

REM Verificar Python
echo [1/6] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo    [ERROR] Python no esta instalado o no esta en el PATH
    set /a ERRORES+=1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo    [OK] Python %%i instalado
)

REM Verificar Node.js
echo.
echo [2/6] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo    [ERROR] Node.js no esta instalado o no esta en el PATH
    set /a ERRORES+=1
) else (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do echo    [OK] Node.js %%i instalado
)

REM Verificar npm
echo.
echo [3/6] Verificando npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo    [ERROR] npm no esta instalado o no esta en el PATH
    set /a ERRORES+=1
) else (
    for /f "tokens=1" %%i in ('npm --version 2^>^&1') do echo    [OK] npm %%i instalado
)

REM Verificar estructura de directorios
echo.
echo [4/6] Verificando estructura de directorios...
if not exist "Backend-Edificio55" (
    echo    [ERROR] Directorio Backend-Edificio55 no encontrado
    set /a ERRORES+=1
) else (
    echo    [OK] Directorio Backend-Edificio55 existe
)

if not exist "Frontend-Edificio55" (
    echo    [ERROR] Directorio Frontend-Edificio55 no encontrado
    set /a ERRORES+=1
) else (
    echo    [OK] Directorio Frontend-Edificio55 existe
)

REM Verificar dependencias del Backend
echo.
echo [5/6] Verificando dependencias del Backend...
if exist "Backend-Edificio55\manage.py" (
    echo    [OK] manage.py encontrado
    cd Backend-Edificio55
    python manage.py check --deploy >nul 2>&1
    if errorlevel 1 (
        echo    [ADVERTENCIA] Django tiene algunos problemas de configuracion
    ) else (
        echo    [OK] Django configurado correctamente
    )
    cd ..
) else (
    echo    [ERROR] manage.py no encontrado
    set /a ERRORES+=1
)

REM Verificar dependencias del Frontend
echo.
echo [6/6] Verificando dependencias del Frontend...
if exist "Frontend-Edificio55\node_modules" (
    echo    [OK] node_modules encontrado
) else (
    echo    [ADVERTENCIA] node_modules no encontrado. Ejecuta 'npm install' en Frontend-Edificio55
)

if exist "Frontend-Edificio55\package.json" (
    echo    [OK] package.json encontrado
) else (
    echo    [ERROR] package.json no encontrado
    set /a ERRORES+=1
)

REM Verificar puertos
echo.
echo Verificando puertos...
netstat -an | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo    [ADVERTENCIA] Puerto 8000 esta en uso (Django)
)

netstat -an | findstr ":5173" >nul 2>&1
if not errorlevel 1 (
    echo    [ADVERTENCIA] Puerto 5173 esta en uso (Vite)
)

REM Resumen
echo.
echo ========================================
if %ERRORES% EQU 0 (
    echo   Verificacion completada: TODO OK
    echo ========================================
    echo.
    echo El sistema esta listo para iniciar.
    echo Puedes ejecutar 'iniciar_sistema_completo.bat'
) else (
    echo   Verificacion completada: SE ENCONTRARON ERRORES
    echo ========================================
    echo.
    echo Se encontraron %ERRORES% error(es).
    echo Por favor, corrige los errores antes de iniciar el sistema.
)
echo.
pause



