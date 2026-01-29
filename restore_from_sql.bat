@echo off
REM Script para restaurar datos desde un archivo SQL a Supabase
REM 
REM INSTRUCCIONES:
REM 1. Coloca tu archivo SQL de backup en esta carpeta
REM 2. Renómbralo a "backup.sql" o ajusta el nombre en la línea siguiente
REM 3. Ejecuta este script

set SQL_FILE=backup.sql
set SUPABASE_DB_NAME=postgres
set SUPABASE_DB_USER=postgres.zrtbnovaxukwsyomasfx
set SUPABASE_DB_HOST=aws-1-us-east-1.pooler.supabase.com
set SUPABASE_DB_PORT=5432

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
echo NOTA: Se te pedira la contraseña de Supabase: Damian27052001
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





