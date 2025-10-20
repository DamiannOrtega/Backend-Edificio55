# 🏢 Sistema de Gestión de Laboratorios - Edificio 55

Un sistema completo y moderno para la gestión de laboratorios de cómputo, desarrollado con Django (Backend) y React (Frontend). Incluye reservas automáticas, control de PCs, registro de visitas de estudiantes y generación de reportes avanzados.

## 🎯 Visión General

Este sistema permite a las instituciones educativas gestionar eficientemente sus laboratorios de cómputo, automatizando procesos como reservas de clases, control de disponibilidad de PCs y seguimiento del uso de recursos por parte de estudiantes.

### ✨ Características Destacadas

- 🤖 **Automatización Inteligente:** Las PCs cambian automáticamente de estado según reservas activas
- 📅 **Series de Reservas:** Crear clases recurrentes (ej: Lunes a Viernes 8:00-9:00) con un clic
- 📊 **Reportes Avanzados:** Análisis completo de uso, ocupación y rendimiento
- 🌐 **Interfaz Moderna:** Frontend responsive con React y TypeScript
- 🔒 **Control de Acceso:** Prevención automática de conflictos de horarios

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Base de       │
│   React + TS    │◄──►│   Django + DRF  │◄──►│   Datos         │
│   Tailwind CSS  │    │   Python        │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Inicio Rápido

### Prerrequisitos
- Python 3.8+
- Node.js 16+
- PostgreSQL (opcional)

### Instalación Completa

1. **Clonar repositorios:**
```bash
# Backend
git clone <backend-repo-url> Backend-Edificio55
cd Backend-Edificio55

# Frontend
git clone <frontend-repo-url> Frontend-Edificio55
cd ../Frontend-Edificio55
```

2. **Configurar Backend:**
```bash
cd Backend-Edificio55
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

3. **Configurar Frontend:**
```bash
cd Frontend-Edificio55
npm install
cp .env.example .env.local
npm run dev
```

4. **Acceder al sistema:**
- **Frontend:** http://localhost:5173
- **Admin Panel:** http://localhost:8000/admin

## 📚 Documentación

### Guías por Componente
- 📖 [Backend - Guía Completa](Backend-Edificio55/README.md)
- 🌐 [Frontend - Guía de Desarrollo](Frontend-Edificio55/README.md)
- 🚀 [Guía de Despliegue](Backend-Edificio55/DEPLOYMENT_GUIDE.md)
- 📊 [Sistema de Reportes](Backend-Edificio55/SISTEMA_REPORTES.md)
- ⚙️ [Personalización de Reportes](Backend-Edificio55/REPORT_CUSTOMIZATION_GUIDE.md)

### Documentación Técnica
- 🔧 [API Documentation](Backend-Edificio55/API_DOCS.md)
- 🗄️ [Database Schema](Backend-Edificio55/DATABASE_SCHEMA.md)
- 🧪 [Testing Guide](Backend-Edificio55/TESTING_GUIDE.md)

## 🎮 Funcionalidades Principales

### 🖥️ Gestión de Laboratorios
- **Control Individual de PCs:** Cada computadora puede ser gestionada independientemente
- **Estados Automáticos:** Las PCs cambian automáticamente según reservas activas
- **Software por Laboratorio:** Catálogo de aplicaciones instaladas
- **Mantenimiento:** Control de PCs fuera de servicio

### 📅 Sistema de Reservas Inteligente
- **Reservas Individuales:** Crear reservas específicas para clases
- **Series Recurrentes:** Crear series de clases (ej: Lunes a Viernes)
- **Generación Automática:** El sistema crea automáticamente todas las reservas individuales
- **Prevención de Conflictos:** No permite reservas solapadas

### 👥 Gestión de Estudiantes
- **Registro de Visitas:** Check-in/Check-out automático
- **Control de Disponibilidad:** Solo muestra PCs realmente disponibles
- **Historial Completo:** Seguimiento detallado de uso
- **Software Utilizado:** Registro de aplicaciones usadas

### 📊 Reportes y Analytics
- **Reportes Personalizados:** Análisis por período, laboratorio, estudiante
- **Dashboard en Tiempo Real:** Vista actualizada de ocupación
- **Exportación:** PDF, Excel, CSV
- **Programación:** Reportes automáticos por email

## 🛠️ Tecnologías

### Backend
- **Django 4.2+** - Framework web robusto
- **Django REST Framework** - API REST completa
- **PostgreSQL** - Base de datos relacional
- **Celery** - Tareas asíncronas
- **Redis** - Cache y broker de mensajes

### Frontend
- **React 18+** - Biblioteca de UI moderna
- **TypeScript** - Tipado estático
- **Vite** - Build tool ultra-rápido
- **Tailwind CSS** - Framework de estilos
- **Shadcn/ui** - Componentes de interfaz

### DevOps
- **Docker** - Containerización
- **GitHub Actions** - CI/CD
- **Nginx** - Servidor web
- **Gunicorn** - WSGI server

## 📈 Casos de Uso

### 🎓 Para Instituciones Educativas
- **Control de Laboratorios:** Gestión completa de recursos de cómputo
- **Optimización de Horarios:** Maximizar el uso de laboratorios
- **Reportes Institucionales:** Análisis de uso y rendimiento
- **Control de Acceso:** Prevenir uso no autorizado durante clases

### 👨‍🏫 Para Profesores
- **Reservas Simples:** Reservar laboratorios fácilmente
- **Series de Clases:** Configurar horarios recurrentes
- **Disponibilidad:** Ver en tiempo real qué laboratorios están libres
- **Historial:** Revisar uso de laboratorios por materia

### 👨‍🎓 Para Estudiantes
- **Registro Fácil:** Check-in rápido con formulario intuitivo
- **Disponibilidad Clara:** Solo ven PCs realmente disponibles
- **Historial Personal:** Seguimiento de su uso de laboratorios
- **Notificaciones:** Alertas sobre cambios de horarios

### 🏢 Para Administradores
- **Panel Completo:** Vista integral del sistema
- **Reportes Detallados:** Análisis profundo de uso
- **Configuración:** Personalizar laboratorios y software
- **Mantenimiento:** Gestionar estados de PCs

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=tu-secret-key
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com

# Frontend (.env.local)
VITE_API_URL=https://api.tu-dominio.com
VITE_APP_NAME=Sistema de Laboratorios
```

### Configuración de Laboratorios
```python
# settings.py
LAB_HOURS_START = "08:00"
LAB_HOURS_END = "22:00"
AUTO_CHECKOUT_TIME = 30  # minutos
RESERVATION_ADVANCE_DAYS = 30
```

## 🧪 Testing

### Ejecutar Todas las Pruebas
```bash
# Backend
cd Backend-Edificio55
python manage.py test

# Frontend
cd Frontend-Edificio55
npm test

# Cobertura
npm run test:coverage
```

### Pruebas de Integración
```bash
# Ejecutar suite completa
python manage.py test --settings=sistema_labs.test_settings
```

## 🚀 Despliegue

### Despliegue con Docker
```bash
# Build y deploy completo
docker-compose up -d

# Solo backend
docker-compose up -d backend

# Solo frontend
docker-compose up -d frontend
```

### Despliegue Manual
1. **Backend:** Configurar servidor con Gunicorn + Nginx
2. **Frontend:** Build estático en servidor web
3. **Base de Datos:** Configurar PostgreSQL
4. **SSL:** Configurar certificados SSL

## 📊 Métricas y Monitoreo

### KPIs del Sistema
- **Ocupación de Laboratorios:** % de uso por laboratorio
- **Tiempo de Respuesta:** Latencia de la API
- **Disponibilidad:** Uptime del sistema
- **Satisfacción:** Feedback de usuarios

### Herramientas de Monitoreo
- **Logs:** Django logging + ELK stack
- **Métricas:** Prometheus + Grafana
- **Alertas:** Email + Slack notifications
- **Performance:** APM con New Relic

## 🤝 Contribución

### Cómo Contribuir
1. **Fork** del repositorio
2. **Crear rama** para feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Crear Pull Request**

### Estándares de Desarrollo
- **Backend:** PEP 8, Black, isort
- **Frontend:** ESLint, Prettier, TypeScript strict
- **Commits:** Conventional Commits
- **Documentación:** Docstrings + README actualizados

### Roadmap
- [ ] **v2.0:** Dashboard en tiempo real con WebSockets
- [ ] **v2.1:** App móvil con React Native
- [ ] **v2.2:** Integración con sistemas académicos
- [ ] **v2.3:** IA para predicción de demanda

## 🆘 Soporte

### Documentación
- 📖 [Wiki del Proyecto](https://github.com/tu-repo/wiki)
- 💬 [FAQ](https://github.com/tu-repo/wiki/faq)
- 🎥 [Video Tutoriales](https://youtube.com/playlist?list=tu-playlist)

### Comunidad
- 💬 [Discord Server](https://discord.gg/tu-servidor)
- 📧 [Email de Soporte](mailto:soporte@edificio55.com)
- 🐛 [Reportar Issues](https://github.com/tu-repo/issues)

### Soporte Comercial
- 📞 **Teléfono:** +1 (555) 123-4567
- 📧 **Email:** enterprise@edificio55.com
- 💼 **Consultoría:** Servicios de implementación y personalización

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT**. Ver el archivo [LICENSE](LICENSE) para más detalles.

### Términos de Uso
- ✅ Uso comercial permitido
- ✅ Modificación permitida
- ✅ Distribución permitida
- ✅ Uso privado permitido
- ❌ Sin garantía de soporte

## 🙏 Agradecimientos

- **Comunidad Django** por el excelente framework
- **Equipo de React** por las herramientas modernas
- **Tailwind CSS** por el sistema de estilos
- **Contribuidores** que han mejorado el proyecto

---

<div align="center">

**Desarrollado con ❤️ para la educación**

[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://djangoproject.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[🌐 Sitio Web](https://edificio55.com) • [📖 Documentación](https://docs.edificio55.com) • [💬 Discord](https://discord.gg/edificio55)

</div>