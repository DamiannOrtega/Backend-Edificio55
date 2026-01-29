#!/usr/bin/env python
"""
Script para cambiar entre base de datos local y Supabase
"""
import os
import re

SETTINGS_FILE = 'sistema_labs/settings.py'

# Configuración de Supabase (actual)
SUPABASE_CONFIG = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',         
        'USER': 'postgres.zrtbnovaxukwsyomasfx',           
        'PASSWORD': 'Damian27052001',  
        'HOST': 'aws-1-us-east-1.pooler.supabase.com',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },               
    }
}"""

# Configuración local (necesitas completar estos valores)
LOCAL_CONFIG_TEMPLATE = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '{db_name}',         
        'USER': '{db_user}',           
        'PASSWORD': '{db_password}',  
        'HOST': '{db_host}',
        'PORT': '{db_port}',
    }
}"""

def read_settings():
    """Lee el archivo settings.py"""
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def write_settings(content):
    """Escribe el archivo settings.py"""
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def switch_to_local(db_name='sistema_labs', db_user='postgres', db_password='', db_host='localhost', db_port='5432'):
    """Cambia a base de datos local"""
    content = read_settings()
    
    # Reemplazar la configuración de DATABASES
    pattern = r'DATABASES\s*=\s*\{[^}]+\{[^}]+\}[^}]+\}'
    local_config = LOCAL_CONFIG_TEMPLATE.format(
        db_name=db_name,
        db_user=db_user,
        db_password=db_password,
        db_host=db_host,
        db_port=db_port
    )
    
    new_content = re.sub(pattern, local_config, content, flags=re.DOTALL)
    write_settings(new_content)
    print("✓ Cambiado a base de datos LOCAL")
    print(f"  Host: {db_host}:{db_port}")
    print(f"  Database: {db_name}")

def switch_to_supabase():
    """Cambia a base de datos Supabase"""
    content = read_settings()
    
    # Reemplazar la configuración de DATABASES
    pattern = r'DATABASES\s*=\s*\{[^}]+\{[^}]+\}[^}]+\}'
    new_content = re.sub(pattern, SUPABASE_CONFIG, content, flags=re.DOTALL)
    write_settings(new_content)
    print("✓ Cambiado a base de datos SUPABASE")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'local':
            # Valores por defecto o desde argumentos
            db_name = sys.argv[2] if len(sys.argv) > 2 else 'sistema_labs'
            db_user = sys.argv[3] if len(sys.argv) > 3 else 'postgres'
            db_password = sys.argv[4] if len(sys.argv) > 4 else ''
            db_host = sys.argv[5] if len(sys.argv) > 5 else 'localhost'
            db_port = sys.argv[6] if len(sys.argv) > 6 else '5432'
            switch_to_local(db_name, db_user, db_password, db_host, db_port)
        elif sys.argv[1] == 'supabase':
            switch_to_supabase()
        else:
            print("Uso:")
            print("  python switch_database.py local [db_name] [user] [password] [host] [port]")
            print("  python switch_database.py supabase")
    else:
        print("Uso:")
        print("  python switch_database.py local [db_name] [user] [password] [host] [port]")
        print("  python switch_database.py supabase")





