# Sistema de Reportes - Edificio 55

## Descripción General

El sistema de reportes del Edificio 55 permite generar análisis detallados del uso de los laboratorios de computación, incluyendo estadísticas, gráficos y exportación a PDF para presentaciones departamentales.

## Características Principales

### 📊 Dashboard de Reportes
- **Estadísticas en tiempo real**: Visitas totales, PCs en uso, estudiantes registrados
- **Gráficos interactivos**: Uso por laboratorio, software más utilizado, tendencias diarias
- **Interfaz moderna**: Diseño responsivo con Plotly.js para visualizaciones

### 📈 Generación de Reportes por Período
- **Períodos disponibles**: Semanal, mensual, bimestral, trimestral, semestral, anual
- **Configuración flexible**: Selección de fechas, opciones de contenido
- **Filtros inteligentes**: Solo muestra datos del período seleccionado

### 📄 Exportación a PDF
- **Reportes profesionales**: Formato listo para presentación departamental
- **Contenido personalizable**: Gráficos, tablas y estadísticas opcionales
- **Diseño corporativo**: Logo UAA, colores institucionales

## Funcionalidades Detalladas

### 1. Dashboard Principal (`/gestion/reportes/`)

#### Estadísticas Generales
- Total de visitas registradas
- Visitas del último mes
- PCs en uso vs total de PCs
- Estudiantes registrados

#### Gráficos Interactivos
- **Uso por Laboratorio**: Gráfico de barras mostrando visitas por laboratorio
- **Uso por Software**: Top 10 de software más utilizado
- **Visitas por Día**: Tendencias de los últimos 30 días

#### Reportes Recientes
- Lista de configuraciones de reportes generados
- Acceso directo para ver y exportar reportes
- Información de período y fecha de creación

### 2. Generación de Reportes

#### Configuración de Período
```python
PERIODO_CHOICES = [
    ('semanal', 'Semanal'),
    ('mensual', 'Mensual'),
    ('bimestral', 'Bimestral'),
    ('trimestral', 'Trimestral'),
    ('semestral', 'Semestral'),
    ('anual', 'Anual'),
]
```

#### Opciones de Contenido
- ✅ **Incluir Gráficos**: Gráficos de barras y líneas
- ✅ **Incluir Tablas**: Datos detallados en formato tabla
- ✅ **Incluir Estadísticas**: Métricas y KPIs

### 3. Análisis de Datos

#### Estadísticas Calculadas
- Total de visitas del período
- Visitas completas vs activas
- Tiempo promedio de uso
- Duración del período en días

#### Datos por Categoría
- **Por Laboratorio**: Número de visitas por cada laboratorio
- **Por Software**: Frecuencia de uso de cada software
- **Por Estudiante**: Top estudiantes más activos
- **Por Día**: Distribución temporal de visitas

### 4. Exportación a PDF

#### Características del PDF
- **Header profesional**: Logo UAA, información del período
- **Estadísticas resumidas**: Métricas clave en tarjetas
- **Tablas detalladas**: Datos organizados por categoría
- **Gráficos integrados**: Visualizaciones en formato vectorial
- **Pie de página**: Información de generación y copyright

#### Estructura del Documento
1. **Portada**: Título, período, fechas, generado por
2. **Estadísticas Generales**: Métricas principales
3. **Uso por Laboratorio**: Tabla y gráfico
4. **Uso por Software**: Tabla y gráfico
5. **Estudiantes Activos**: Ranking de uso
6. **Visitas por Día**: Cronología detallada

## Acceso al Sistema

### Desde el Panel de Administración
1. Iniciar sesión en `/admin/`
2. Navegar a "Gestion" → "Dashboard de Reportes"
3. O ir directamente a `/gestion/reportes/`

### Permisos Requeridos
- `gestion.view_configuracionreporte`: Para acceder al dashboard
- `gestion.add_configuracionreporte`: Para crear reportes
- `gestion.change_configuracionreporte`: Para modificar configuraciones

## API Endpoints

### Dashboard de Reportes
```
GET /gestion/reportes/
```
Muestra el dashboard principal con estadísticas y gráficos.

### Generar Reporte
```
POST /gestion/reportes/generar/
```
Crea una nueva configuración de reporte y genera los datos.

**Payload:**
```json
{
    "nombre": "Reporte Semestral 2025-1",
    "periodo": "semestral",
    "fecha_inicio": "2025-01-15",
    "fecha_fin": "2025-06-15",
    "incluir_graficos": true,
    "incluir_tablas": true,
    "incluir_estadisticas": true
}
```

### Ver Reporte
```
GET /gestion/reportes/ver/<config_id>/
```
Muestra un reporte específico con todos los datos y gráficos.

### Exportar PDF
```
GET /gestion/reportes/exportar/<config_id>/
```
Descarga el reporte en formato PDF.

### Estadísticas en Tiempo Real
```
GET /gestion/api/estadisticas-tiempo-real/
```
API para obtener estadísticas actuales (visitas activas, PCs en uso, etc.).

## Modelos de Datos

### ConfiguracionReporte
```python
class ConfiguracionReporte(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    periodo = models.CharField(max_length=20, choices=PERIODO_CHOICES)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    incluir_graficos = models.BooleanField(default=True)
    incluir_tablas = models.BooleanField(default=True)
    incluir_estadisticas = models.BooleanField(default=True)
    creado_por = models.CharField(max_length=100, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
```

## Tecnologías Utilizadas

### Backend
- **Django 4.2.25**: Framework web
- **PostgreSQL**: Base de datos
- **ReportLab**: Generación de PDFs
- **Plotly**: Gráficos interactivos
- **Pandas**: Análisis de datos

### Frontend
- **Plotly.js**: Visualizaciones interactivas
- **Bootstrap**: Framework CSS
- **Font Awesome**: Iconos
- **JavaScript**: Interactividad

## Instalación y Configuración

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Crear Superusuario (si es necesario)
```bash
python manage.py createsuperuser
```

### 4. Iniciar Servidor
```bash
python manage.py runserver
```

## Uso Recomendado

### Para Administradores
1. **Revisión diaria**: Consultar el dashboard para estadísticas generales
2. **Reportes semanales**: Generar reportes semanales para seguimiento
3. **Reportes departamentales**: Crear reportes mensuales/semestrales para presentaciones

### Para Departamentos
1. **Solicitar reportes**: Los administradores pueden generar reportes específicos
2. **Exportar PDFs**: Descargar reportes en formato profesional
3. **Análisis de tendencias**: Revisar gráficos para identificar patrones de uso

## Casos de Uso

### 1. Reporte Semanal de Uso
- **Período**: Lunes a domingo
- **Contenido**: Gráficos + tablas + estadísticas
- **Uso**: Revisión operativa semanal

### 2. Reporte Semestral para Departamento
- **Período**: 6 meses académicos
- **Contenido**: Solo estadísticas + tablas (sin gráficos)
- **Uso**: Presentación a autoridades universitarias

### 3. Análisis de Software
- **Período**: Último mes
- **Contenido**: Solo gráficos de software
- **Uso**: Decisión de licencias y actualizaciones

## Mantenimiento

### Limpieza de Datos
- Los reportes se mantienen indefinidamente
- Considerar limpieza anual de configuraciones muy antiguas
- Los datos de visitas se conservan según política de retención

### Monitoreo de Rendimiento
- Los reportes con períodos muy largos pueden ser lentos
- Considerar paginación para reportes con muchos datos
- Monitorear uso de memoria en generación de PDFs

## Soporte y Desarrollo

### Logs y Debugging
- Revisar logs de Django para errores en generación de reportes
- Verificar permisos de usuario para acceso a reportes
- Comprobar conectividad con base de datos

### Mejoras Futuras
- [ ] Reportes programados automáticos
- [ ] Notificaciones por email
- [ ] Más tipos de gráficos (pie charts, heatmaps)
- [ ] Comparativas entre períodos
- [ ] Exportación a Excel
- [ ] Dashboard en tiempo real con WebSockets

---

**Desarrollado para la Universidad Autónoma de Aguascalientes - Edificio 55**


