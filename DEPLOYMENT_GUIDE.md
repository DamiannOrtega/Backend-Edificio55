# 🚀 Guía de Despliegue en Internet - Versión Gratuita

## 📋 Resumen

Esta guía te ayudará a desplegar tu sistema de gestión de laboratorios en internet usando servicios gratuitos. Perfecto para un flujo bajo de visitas (hasta 10 por día) sin costos de hosting.

## 🎯 Arquitectura Propuesta

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Base de Datos │
│   (Vercel)      │◄──►│   (Railway)     │◄──►│   (Railway PG)  │
│   React Apps    │    │   Django API    │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Servicios Gratuitos Utilizados

### **1. Vercel (Frontend)**
- **Gratis**: Hasta 100GB de ancho de banda/mes
- **Perfecto para**: React apps estáticas
- **Ventajas**: Deploy automático desde GitHub, CDN global
- **Límites**: 100 builds/mes, 100GB bandwidth

### **2. Railway (Backend + Base de Datos)**
- **Gratis**: $5 de crédito/mes (suficiente para tu uso)
- **Perfecto para**: Django + PostgreSQL
- **Ventajas**: Deploy automático, base de datos incluida
- **Límites**: 512MB RAM, 1GB storage

### **3. GitHub (Código)**
- **Gratis**: Repositorios públicos ilimitados
- **Perfecto para**: Control de versiones y CI/CD
- **Ventajas**: Integración con Vercel y Railway

## 📦 Preparación del Proyecto

### **1. Estructura de Repositorios**

Crear 3 repositorios separados en GitHub:

```
github.com/tu-usuario/
├── laboratorios-backend     # Django API
├── laboratorios-frontend    # React Dashboard + Reports
└── laboratorios-registro    # React Form
```

### **2. Configuración para Producción**

#### **Backend (Django)**

Crear `Backend-Edificio55/requirements.txt`:
```txt
Django==4.2.25
django-cors-headers==4.9.0
django-jazzmin==3.0.1
psycopg2-binary==2.9.10
pytz==2025.2
six==1.17.0
sqlparse==0.5.3
tzdata==2025.2
reportlab==4.2.5
openpyxl==3.1.5
pandas==2.2.3
gunicorn==21.2.0
whitenoise==6.6.0
python-decouple==3.8
```

Crear `Backend-Edificio55/Procfile`:
```
web: gunicorn sistema_labs.wsgi:application --bind 0.0.0.0:$PORT
```

Crear `Backend-Edificio55/runtime.txt`:
```
python-3.12.6
```

Actualizar `Backend-Edificio55/sistema_labs/settings.py`:
```python
import os
from decouple import config

# Configuración de producción
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Base de datos de Railway
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT'),
    }
}

# CORS para producción
CORS_ALLOWED_ORIGINS = [
    "https://tu-dashboard.vercel.app",
    "https://tu-registro.vercel.app",
]

# Archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

#### **Frontend (React)**

Crear `insight-form-viz-main/vercel.json`:
```json
{
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "VITE_API_URL": "https://tu-backend.railway.app"
  }
}
```

Actualizar `insight-form-viz-main/src/services/api.ts`:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://tu-backend.railway.app';
```

## 🚀 Pasos de Despliegue

### **Paso 1: Desplegar Backend en Railway**

1. **Crear cuenta en Railway**
   - Ir a [railway.app](https://railway.app)
   - Registrarse con GitHub

2. **Crear nuevo proyecto**
   ```bash
   # Instalar Railway CLI
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Crear proyecto
   railway init laboratorios-backend
   ```

3. **Configurar base de datos**
   - En el dashboard de Railway
   - Añadir servicio "PostgreSQL"
   - Copiar variables de conexión

4. **Configurar variables de entorno**
   ```bash
   railway variables set SECRET_KEY=tu-secret-key-super-seguro
   railway variables set DEBUG=False
   railway variables set ALLOWED_HOSTS=tu-backend.railway.app
   railway variables set DATABASE_NAME=${{Postgres.DATABASE}}
   railway variables set DATABASE_USER=${{Postgres.USER}}
   railway variables set DATABASE_PASSWORD=${{Postgres.PASSWORD}}
   railway variables set DATABASE_HOST=${{Postgres.HOST}}
   railway variables set DATABASE_PORT=${{Postgres.PORT}}
   ```

5. **Deploy**
   ```bash
   railway up
   ```

### **Paso 2: Desplegar Frontend en Vercel**

1. **Crear cuenta en Vercel**
   - Ir a [vercel.com](https://vercel.com)
   - Registrarse con GitHub

2. **Importar repositorio**
   - Conectar repositorio de GitHub
   - Configurar build settings:
     - **Framework Preset**: Vite
     - **Build Command**: `npm run build`
     - **Output Directory**: `dist`

3. **Configurar variables de entorno**
   ```
   VITE_API_URL=https://tu-backend.railway.app
   ```

4. **Deploy automático**
   - Vercel detecta cambios en GitHub
   - Deploy automático en cada push

### **Paso 3: Configurar Dominios Personalizados (Opcional)**

#### **Railway (Backend)**
```bash
# En Railway dashboard
# Settings > Domains
# Añadir: api.tudominio.com
```

#### **Vercel (Frontend)**
```bash
# En Vercel dashboard
# Settings > Domains
# Añadir: dashboard.tudominio.com
# Añadir: registro.tudominio.com
```

## 🔧 Configuración Post-Deploy

### **1. Migrar Base de Datos**
```bash
# Conectar a Railway
railway connect

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Cargar datos iniciales
python manage.py loaddata datos_iniciales.json
```

### **2. Configurar CORS**
Actualizar `CORS_ALLOWED_ORIGINS` con URLs de producción:
```python
CORS_ALLOWED_ORIGINS = [
    "https://tu-dashboard.vercel.app",
    "https://tu-registro.vercel.app",
    "https://dashboard.tudominio.com",
    "https://registro.tudominio.com",
]
```

### **3. Configurar SSL**
- Railway: Automático
- Vercel: Automático
- Dominios personalizados: Configurar en Cloudflare (gratis)

## 📊 Monitoreo y Mantenimiento

### **1. Logs de Railway**
```bash
# Ver logs en tiempo real
railway logs

# Ver logs específicos
railway logs --service backend
```

### **2. Métricas de Vercel**
- Dashboard de Vercel
- Analytics de visitas
- Performance metrics

### **3. Backup de Base de Datos**
```bash
# Backup manual
railway run pg_dump $DATABASE_URL > backup.sql

# Restore
railway run psql $DATABASE_URL < backup.sql
```

## 💰 Costos Estimados

### **Uso Gratuito (Recomendado)**
- **Railway**: $0 (dentro del límite de $5/mes)
- **Vercel**: $0 (dentro de límites gratuitos)
- **GitHub**: $0
- **Total**: $0/mes

### **Uso con Dominio Personalizado**
- **Railway**: $0
- **Vercel**: $0
- **Dominio**: $10-15/año
- **Total**: ~$1.25/mes

## 🔒 Seguridad en Producción

### **1. Variables de Entorno**
```bash
# Nunca commitear .env
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
```

### **2. HTTPS**
- Automático en Railway y Vercel
- Redirigir HTTP a HTTPS

### **3. Rate Limiting**
```python
# En settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
    }
}
```

## 🚨 Solución de Problemas

### **Error de CORS**
```python
# Verificar CORS_ALLOWED_ORIGINS
# Añadir URL exacta del frontend
```

### **Error de Base de Datos**
```bash
# Verificar variables de entorno
railway variables

# Reconectar base de datos
railway connect
```

### **Error de Build**
```bash
# Verificar logs de build
vercel logs

# Rebuild manual
vercel --prod
```

## 📈 Escalabilidad Futura

### **Si crece el uso:**
1. **Railway Pro** ($5/mes) - Más recursos
2. **Vercel Pro** ($20/mes) - Más bandwidth
3. **Base de datos dedicada** - Mejor performance

### **Optimizaciones:**
1. **CDN** - Cloudflare (gratis)
2. **Caching** - Redis en Railway
3. **Monitoring** - Sentry (gratis)

## 📞 Soporte

- **Railway**: Discord community
- **Vercel**: GitHub discussions
- **Django**: Stack Overflow
- **React**: React community

---

**Tiempo estimado de deploy**: 2-3 horas  
**Costo mensual**: $0 (dentro de límites gratuitos)  
**Mantenimiento**: Mínimo (deploy automático)



