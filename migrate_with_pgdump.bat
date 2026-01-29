@echo off
REM Script para migrar datos usando pg_dump
REM Ajusta estos valores según tu configuración local
set LOCAL_DB_NAME=sistema_labs
set LOCAL_DB_USER=postgres
set LOCAL_DB_HOST=localhost
set LOCAL_DB_PORT=5432

REM Configuración de Supabase
set SUPABASE_DB_NAME=postgres
set SUPABASE_DB_USER=postgres.zrtbnovaxukwsyomasfx
set SUPABASE_DB_PASSWORD=Damian27052001
set SUPABASE_DB_HOST=aws-1-us-east-1.pooler.supabase.com
set SUPABASE_DB_PORT=5432

echo Exportando datos desde base de datos local...
pg_dump -h %LOCAL_DB_HOST% -p %LOCAL_DB_PORT% -U %LOCAL_DB_USER% -d %LOCAL_DB_NAME% -F c -f backup_local.dump

echo.
echo Restaurando datos en Supabase...
echo NOTA: Necesitaras ingresar la contraseña de Supabase cuando se solicite
pg_restore -h %SUPABASE_DB_HOST% -p %SUPABASE_DB_PORT% -U %SUPABASE_DB_USER% -d %SUPABASE_DB_NAME% --no-owner --no-acl backup_local.dump

echo.
echo Migracion completada!
pause





