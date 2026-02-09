@echo off
REM Script para restaurar datos desde un archivo SQL a Supabase
REM 
REM INSTRUCCIONES:
REM 1. Coloca tu archivo SQL de backup en esta carpeta
REM 2. Renómbralo a "backup.sql" o ajusta el nombre en la línea siguiente
REM 3. Ejecuta este script

set SQL_FILE=backup.sql

REM Configuración de Supabase
REM IMPORTANTE: Las credenciales se leen del archivo .env
REM No incluyas credenciales directamente en este archivo

REM Leer credenciales del archivo .env
for /f "tokens=1,2 delims==" %%a in ('type .env ^| findstr /v "^#"') do (
    if "%%a"=="DB_NAME" set SUPABASE_DB_NAME=%%b
    if "%%a"=="DB_USER" set SUPABASE_DB_USER=%%b
    if "%%a"=="DB_PASSWORD" set SUPABASE_DB_PASSWORD=%%b
    if "%%a"=="DB_HOST" set SUPABASE_DB_HOST=%%b
    if "%%a"=="DB_PORT" set SUPABASE_DB_PORT=%%b
)

if not exist "%SQL_FILE%" (
    echo ERROR: No se encontro el archivo %SQL_FILE%
    echo.
    echo Por favor:
    echo 1. Coloca tu archivo SQL de backup en esta carpeta
    echo 2. Renombralo a "backup.sql" o ajusta el nombre en este script
    pause
    exit /b 1
)

echo Restaurando datos desde %SQL_FILE% a Supabase...
echo NOTA: Se te pedira la contraseña de Supabase configurada en .env
echo.

psql -h %SUPABASE_DB_HOST% -p %SUPABASE_DB_PORT% -U %SUPABASE_DB_USER% -d %SUPABASE_DB_NAME% -f %SQL_FILE%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Restauracion completada exitosamente!
) else (
    echo.
    echo ✗ Error durante la restauracion
)

pause





