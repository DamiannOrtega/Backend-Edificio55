# 🔒 Guía de Seguridad - Variables de Entorno

## ⚠️ IMPORTANTE: Protección de Credenciales

Este proyecto utiliza **variables de entorno** para proteger información sensible como:
- Credenciales de base de datos (Supabase)
- Secret Key de Django
- Configuraciones sensibles

## 📋 Configuración Inicial

### 1. Crear archivo `.env`

Cuando clones este repositorio, **debes crear tu propio archivo `.env`** en la raíz del proyecto Backend:

```bash
cd Backend-Edificio55
cp .env.example .env
```

### 2. Completar tus credenciales

Edita el archivo `.env` y completa con tus credenciales reales:

```env
# Configuración de Base de Datos
DB_ENGINE=django.db.backends.postgresql
DB_NAME=tu_nombre_de_base_de_datos
DB_USER=tu_usuario_de_supabase
DB_PASSWORD=tu_contraseña_segura
DB_HOST=tu_host.supabase.com
DB_PORT=5432
DB_SSLMODE=require

# Django Secret Key
SECRET_KEY=tu_secret_key_aqui

# Debug Mode
DEBUG=True

# Hosts permitidos
ALLOWED_HOSTS=*
```

### 3. Generar una nueva Secret Key (Recomendado)

Para mayor seguridad, genera tu propia SECRET_KEY:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copia el resultado y pégalo en tu archivo `.env`.

## 🚫 Qué NO hacer

❌ **NUNCA** subas el archivo `.env` a GitHub  
❌ **NUNCA** compartas tus credenciales en público  
❌ **NUNCA** hagas commit de archivos con credenciales hardcodeadas  

## ✅ Qué SÍ hacer

✅ Usa el archivo `.env` para credenciales locales  
✅ Comparte el archivo `.env.example` (sin credenciales reales)  
✅ Agrega `.env` al `.gitignore` (ya está configurado)  
✅ Documenta qué variables se necesitan en `.env.example`  

## 🔍 Verificar que `.env` no se suba a GitHub

El archivo `.gitignore` ya incluye `.env`, pero puedes verificar:

```bash
git status
```

Si ves `.env` en la lista, **NO lo agregues**. Si ya lo agregaste por error:

```bash
git rm --cached .env
git commit -m "Remove .env from repository"
```

## 📦 Instalación de Dependencias

Este proyecto requiere `python-decouple` para leer variables de entorno:

```bash
pip install -r requirements.txt
```

## 🌐 Configuración para Producción

Cuando despliegues a producción:

1. Cambia `DEBUG=False` en tu `.env` de producción
2. Configura `ALLOWED_HOSTS` con tu dominio real
3. Usa variables de entorno del servidor (no archivo `.env`)
4. Genera una nueva SECRET_KEY única para producción

## 🆘 Problemas Comunes

### Error: "No se puede conectar a la base de datos"
- Verifica que el archivo `.env` existe
- Verifica que las credenciales son correctas
- Verifica que `python-decouple` está instalado

### Error: "SECRET_KEY not found"
- Asegúrate de tener el archivo `.env` en la raíz del proyecto Backend
- Verifica que la variable `SECRET_KEY` está definida en `.env`

## 📚 Más Información

- [Django Settings Best Practices](https://docs.djangoproject.com/en/stable/topics/settings/)
- [Python Decouple Documentation](https://github.com/HBNetwork/python-decouple)
- [Supabase Security Best Practices](https://supabase.com/docs/guides/platform/going-into-prod)

---

**Recuerda: La seguridad de tus datos depende de mantener tus credenciales privadas.** 🔐
