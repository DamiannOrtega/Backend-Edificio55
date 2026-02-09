@echo off
REM Script para migrar datos usando pg_dump
REM Ajusta estos valores según tu configuración local
set LOCAL_DB_NAME=sistema_labs
set LOCAL_DB_USER=postgres
set LOCAL_DB_HOST=localhost
set LOCAL_DB_PORT=5432

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

echo Exportando datos desde base de datos local...
pg_dump -h %LOCAL_DB_HOST% -p %LOCAL_DB_PORT% -U %LOCAL_DB_USER% -d %LOCAL_DB_NAME% -F c -f backup_local.dump

echo.
echo Restaurando datos en Supabase...
echo NOTA: Necesitaras ingresar la contraseña de Supabase cuando se solicite
pg_restore -h %SUPABASE_DB_HOST% -p %SUPABASE_DB_PORT% -U %SUPABASE_DB_USER% -d %SUPABASE_DB_NAME% --no-owner --no-acl backup_local.dump

echo.
echo Migracion completada!
pause





