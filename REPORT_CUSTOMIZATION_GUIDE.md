# 📊 Guía de Personalización de Reportes PDF y Excel

## 📋 Introducción

Esta guía te ayudará a modificar el diseño, formato y contenido de los reportes PDF y Excel generados por el sistema. El generador está diseñado para ser fácilmente personalizable sin afectar la funcionalidad principal.

## 🏗️ Arquitectura del Generador

```
report_generator.py
├── ReportGenerator (Clase principal)
├── _create_cover_page()      # Portada del PDF
├── _create_executive_summary() # Resumen ejecutivo
├── _create_detailed_statistics() # Estadísticas detalladas
├── _create_charts_analysis() # Análisis gráfico
├── _create_detailed_tables() # Tablas detalladas
├── generate_pdf_report()     # Generador PDF principal
├── generate_excel_report()   # Generador Excel principal
└── Métodos auxiliares        # Obtener datos
```

## 🎨 Personalización de PDF

### **1. Modificar la Portada**

Ubicación: `_create_cover_page()` en `report_generator.py`

```python
def _create_cover_page(self, filters):
    elements = []
    
    # Logo personalizado
    elements.append(Spacer(1, 1*inch))
    
    # Título principal - CAMBIAR AQUÍ
    title = Paragraph("TU TÍTULO PERSONALIZADO", self.styles['CustomTitle'])
    elements.append(title)
    
    # Subtítulo - CAMBIAR AQUÍ
    subtitle = Paragraph("Tu Institución - Tu Departamento", self.styles['CustomSubtitle'])
    elements.append(subtitle)
    
    # Información adicional personalizada
    elements.append(Spacer(1, 0.5*inch))
    custom_info = Paragraph(
        "<b>Información Personalizada:</b><br/>"
        "• Punto 1<br/>"
        "• Punto 2<br/>"
        "• Punto 3", 
        self.styles['CustomNormal']
    )
    elements.append(custom_info)
    
    return elements
```

### **2. Personalizar Colores y Estilos**

Ubicación: `setup_custom_styles()` en `report_generator.py`

```python
def setup_custom_styles(self):
    """Configurar estilos personalizados para el reporte"""
    
    # Estilo para el título principal - CAMBIAR COLORES
    self.styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=self.styles['Heading1'],
        fontSize=28,  # CAMBIAR TAMAÑO
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#YOUR_COLOR')  # CAMBIAR COLOR
    ))
    
    # Estilo para subtítulos - CAMBIAR COLORES
    self.styles.add(ParagraphStyle(
        name='CustomSubtitle',
        parent=self.styles['Heading2'],
        fontSize=18,  # CAMBIAR TAMAÑO
        spaceAfter=20,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#YOUR_COLOR')  # CAMBIAR COLOR
    ))
    
    # Agregar nuevos estilos personalizados
    self.styles.add(ParagraphStyle(
        name='CustomHighlight',
        parent=self.styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#FF6B35'),
        backColor=colors.HexColor('#FFF3E0'),
        borderPadding=10,
        borderColor=colors.HexColor('#FF6B35'),
        borderWidth=1
    ))
```

### **3. Modificar Tablas**

Ubicación: Cualquier método `_create_*_table()`

```python
def _create_custom_table(self, data, title):
    """Crear tabla personalizada"""
    elements = []
    
    # Título de la tabla
    elements.append(Paragraph(title, self.styles['CustomSubtitle']))
    
    # Crear tabla con datos personalizados
    table_data = [['Columna 1', 'Columna 2', 'Columna 3']]
    for item in data:
        table_data.append([
            item['campo1'],
            f"{item['campo2']:,}",  # Formato con comas
            f"{item['campo3']:.1f}%"  # Formato de porcentaje
        ])
    
    # Crear tabla
    custom_table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    
    # Estilo personalizado - CAMBIAR COLORES
    custom_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#YOUR_HEADER_COLOR')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#YOUR_ROW_COLOR')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        # Agregar efectos especiales
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
    ]))
    
    elements.append(custom_table)
    return elements
```

### **4. Agregar Gráficos Personalizados**

```python
def _create_custom_chart(self, data, chart_type='bar'):
    """Crear gráfico personalizado"""
    elements = []
    
    # Crear gráfico con ReportLab
    drawing = Drawing(400, 300)
    
    if chart_type == 'bar':
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.height = 200
        chart.width = 300
        chart.data = [item['value'] for item in data]
        chart.categoryAxis.categoryNames = [item['name'] for item in data]
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max(item['value'] for item in data) * 1.1
        
        # Personalizar colores
        chart.bars[0].fillColor = colors.HexColor('#YOUR_CHART_COLOR')
        chart.bars[0].strokeColor = colors.HexColor('#YOUR_BORDER_COLOR')
        
        drawing.add(chart)
    
    elif chart_type == 'pie':
        pie = Pie()
        pie.x = 200
        pie.y = 200
        pie.width = 150
        pie.height = 150
        pie.data = [item['value'] for item in data]
        pie.labels = [item['name'] for item in data]
        
        # Personalizar colores
        pie.slices[0].fillColor = colors.HexColor('#YOUR_COLOR_1')
        pie.slices[1].fillColor = colors.HexColor('#YOUR_COLOR_2')
        # ... más colores
        
        drawing.add(pie)
    
    elements.append(drawing)
    return elements
```

### **5. Agregar Páginas Personalizadas**

```python
def _create_custom_page(self, filters):
    """Crear página personalizada"""
    elements = []
    
    # Título de página
    title = Paragraph("TU PÁGINA PERSONALIZADA", self.styles['CustomTitle'])
    elements.append(title)
    
    # Contenido personalizado
    content = Paragraph(
        "Aquí puedes agregar cualquier contenido personalizado:<br/>"
        "• Texto con formato<br/>"
        "• <b>Texto en negrita</b><br/>"
        "• <i>Texto en cursiva</i><br/>"
        "• <u>Texto subrayado</u>",
        self.styles['CustomNormal']
    )
    elements.append(content)
    
    # Tabla personalizada
    custom_data = self._get_custom_data(filters)
    elements.extend(self._create_custom_table(custom_data, "Datos Personalizados"))
    
    return elements

def generate_pdf_report(self, filters, output_path=None):
    """Generar reporte PDF con páginas personalizadas"""
    # ... código existente ...
    
    # Agregar página personalizada
    story.extend(self._create_custom_page(filters))
    story.append(PageBreak())
    
    # ... resto del código ...
```

## 📊 Personalización de Excel

### **1. Modificar Hojas Existentes**

Ubicación: Métodos `_create_excel_*_sheet()`

```python
def _create_excel_custom_sheet(self, writer, filters):
    """Crear hoja personalizada en Excel"""
    
    # Datos personalizados
    custom_data = {
        'Métrica Personalizada': [
            'Nueva Métrica 1',
            'Nueva Métrica 2',
            'Nueva Métrica 3',
            'Nueva Métrica 4'
        ],
        'Valor': [
            self._calculate_custom_metric_1(filters),
            self._calculate_custom_metric_2(filters),
            self._calculate_custom_metric_3(filters),
            self._calculate_custom_metric_4(filters)
        ],
        'Descripción': [
            'Descripción de la métrica 1',
            'Descripción de la métrica 2',
            'Descripción de la métrica 3',
            'Descripción de la métrica 4'
        ]
    }
    
    df = pd.DataFrame(custom_data)
    df.to_excel(writer, sheet_name='Hoja Personalizada', index=False)
    
    # Formatear la hoja
    worksheet = writer.sheets['Hoja Personalizada']
    
    # Ajustar ancho de columnas
    worksheet.column_dimensions['A'].width = 25
    worksheet.column_dimensions['B'].width = 15
    worksheet.column_dimensions['C'].width = 40
    
    # Aplicar estilos
    from openpyxl.styles import Font, PatternFill, Alignment
    
    # Estilo para encabezados
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    
    for cell in worksheet[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")
    
    # Estilo para datos
    for row in worksheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(horizontal="center")
```

### **2. Agregar Gráficos en Excel**

```python
def _add_excel_charts(self, writer, data):
    """Agregar gráficos a Excel"""
    from openpyxl.chart import BarChart, PieChart, Reference
    
    # Obtener la hoja
    worksheet = writer.sheets['Uso por Laboratorio']
    
    # Crear gráfico de barras
    chart = BarChart()
    chart.title = "Uso por Laboratorio"
    chart.x_axis.title = "Laboratorios"
    chart.y_axis.title = "Visitas"
    
    # Referencias de datos
    data_ref = Reference(worksheet, min_col=2, min_row=1, max_row=len(data)+1)
    categories_ref = Reference(worksheet, min_col=1, min_row=2, max_row=len(data)+1)
    
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(categories_ref)
    
    # Posicionar gráfico
    worksheet.add_chart(chart, "E2")
```

### **3. Personalizar Formato de Celdas**

```python
def _format_excel_cells(self, worksheet, data_range):
    """Formatear celdas específicas"""
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from openpyxl.formatting.rule import ColorScaleRule
    
    # Bordes
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Aplicar bordes a todas las celdas
    for row in worksheet.iter_rows(min_row=1, max_row=len(data_range)+1):
        for cell in row:
            cell.border = thin_border
    
    # Escala de colores para valores
    color_scale = ColorScaleRule(
        start_type='min', start_color='00FF0000',  # Rojo para mínimo
        mid_type='percentile', mid_value=50, mid_color='00FFFF00',  # Amarillo para medio
        end_type='max', end_color='0000FF00'  # Verde para máximo
    )
    
    # Aplicar escala de colores a columna de valores
    worksheet.conditional_formatting.add('B2:B100', color_scale)
```

## 🔧 Configuración Avanzada

### **1. Variables de Configuración**

Crear `Backend-Edificio55/gestion/report_config.py`:

```python
# Configuración de reportes
REPORT_CONFIG = {
    'company': {
        'name': 'Universidad Autónoma de Aguascalientes',
        'department': 'Edificio 55',
        'logo_path': 'static/img/logo.png',
        'address': 'Av. Universidad 940, Aguascalientes, Ags.',
        'phone': '(449) 910-7400',
        'email': 'edificio55@uaa.mx'
    },
    'colors': {
        'primary': '#1e40af',
        'secondary': '#059669',
        'accent': '#dc2626',
        'warning': '#f59e0b',
        'info': '#3b82f6'
    },
    'pdf': {
        'page_size': 'A4',
        'margins': {
            'top': 72,
            'bottom': 18,
            'left': 72,
            'right': 72
        },
        'font_family': 'Helvetica',
        'title_font_size': 24,
        'subtitle_font_size': 16,
        'normal_font_size': 10
    },
    'excel': {
        'default_width': 15,
        'header_height': 20,
        'row_height': 15
    }
}
```

### **2. Usar Configuración en el Generador**

```python
from .report_config import REPORT_CONFIG

class ReportGenerator:
    def __init__(self):
        self.config = REPORT_CONFIG
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Usar configuración para estilos"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=self.config['pdf']['title_font_size'],
            textColor=colors.HexColor(self.config['colors']['primary'])
        ))
```

### **3. Plantillas Personalizables**

Crear `Backend-Edificio55/gestion/report_templates.py`:

```python
# Plantillas de texto para reportes
REPORT_TEMPLATES = {
    'cover_page': {
        'title': 'REPORTE DE USO DE LABORATORIOS',
        'subtitle': '{company_name} - {department}',
        'period_info': 'Período de Análisis: {date_from} a {date_to}',
        'generation_date': 'Fecha de Generación: {current_date}'
    },
    'executive_summary': {
        'title': 'RESUMEN EJECUTIVO',
        'description': 'Este reporte presenta un análisis detallado del uso de los laboratorios...'
    },
    'conclusions': {
        'title': 'CONCLUSIONES Y RECOMENDACIONES',
        'templates': [
            'El análisis muestra un uso {usage_level} de los recursos.',
            'Se recomienda {recommendation} para optimizar el uso.',
            'La tendencia indica {trend_description}.'
        ]
    }
}

def get_template(template_key, **kwargs):
    """Obtener plantilla con variables reemplazadas"""
    template = REPORT_TEMPLATES[template_key]
    if isinstance(template, dict):
        return {k: v.format(**kwargs) for k, v in template.items()}
    return template.format(**kwargs)
```

## 🚀 Ejemplos de Personalización

### **Ejemplo 1: Reporte para Autoridades**

```python
def generate_executive_pdf(self, filters, output_path=None):
    """Generar PDF ejecutivo simplificado"""
    # Solo páginas esenciales
    story = []
    story.extend(self._create_cover_page(filters))
    story.append(PageBreak())
    story.extend(self._create_executive_summary(filters))
    story.append(PageBreak())
    story.extend(self._create_key_metrics(filters))
    
    # Generar PDF
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    doc.build(story)
```

### **Ejemplo 2: Reporte Técnico Detallado**

```python
def generate_technical_pdf(self, filters, output_path=None):
    """Generar PDF técnico con todos los detalles"""
    story = []
    story.extend(self._create_cover_page(filters))
    story.append(PageBreak())
    story.extend(self._create_executive_summary(filters))
    story.append(PageBreak())
    story.extend(self._create_detailed_statistics(filters))
    story.append(PageBreak())
    story.extend(self._create_technical_analysis(filters))
    story.append(PageBreak())
    story.extend(self._create_raw_data_tables(filters))
    
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    doc.build(story)
```

### **Ejemplo 3: Reporte por Departamento**

```python
def generate_department_pdf(self, filters, department, output_path=None):
    """Generar PDF específico para un departamento"""
    # Filtrar datos por departamento
    department_filters = {**filters, 'department': department}
    
    story = []
    story.extend(self._create_department_cover(department))
    story.append(PageBreak())
    story.extend(self._create_department_metrics(department_filters))
    story.append(PageBreak())
    story.extend(self._create_department_recommendations(department))
    
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    doc.build(story)
```

## 📝 Testing de Personalizaciones

### **1. Script de Prueba**

Crear `Backend-Edificio55/test_reports.py`:

```python
from gestion.report_generator import ReportGenerator

def test_custom_reports():
    """Probar reportes personalizados"""
    generator = ReportGenerator()
    
    # Filtros de prueba
    test_filters = {
        'date_from': '2025-01-01',
        'date_to': '2025-01-17',
        'laboratory': 'all',
        'software': 'all'
    }
    
    # Probar PDF personalizado
    pdf_content = generator.generate_executive_pdf(test_filters)
    with open('test_executive.pdf', 'wb') as f:
        f.write(pdf_content)
    
    # Probar Excel personalizado
    excel_content = generator.generate_technical_excel(test_filters)
    with open('test_technical.xlsx', 'wb') as f:
        f.write(excel_content)
    
    print("Reportes de prueba generados exitosamente")

if __name__ == '__main__':
    test_custom_reports()
```

### **2. Comando de Django**

Crear `Backend-Edificio55/gestion/management/commands/test_reports.py`:

```python
from django.core.management.base import BaseCommand
from gestion.report_generator import ReportGenerator

class Command(BaseCommand):
    help = 'Generar reportes de prueba'

    def handle(self, *args, **options):
        generator = ReportGenerator()
        
        # Generar reportes de prueba
        test_filters = {
            'date_from': '2025-01-01',
            'date_to': '2025-01-17'
        }
        
        # PDF ejecutivo
        pdf_content = generator.generate_executive_pdf(test_filters)
        with open('reporte_ejecutivo.pdf', 'wb') as f:
            f.write(pdf_content)
        
        self.stdout.write(
            self.style.SUCCESS('Reportes generados exitosamente')
        )
```

## 🔄 Mantenimiento y Actualizaciones

### **1. Versionado de Reportes**

```python
# En report_generator.py
class ReportGenerator:
    VERSION = "1.2.0"
    
    def _create_cover_page(self, filters):
        # ... código existente ...
        
        # Agregar versión
        version_text = Paragraph(
            f"Versión del Reporte: {self.VERSION}",
            self.styles['CustomNormal']
        )
        elements.append(version_text)
```

### **2. Logging de Generación**

```python
import logging

logger = logging.getLogger(__name__)

def generate_pdf_report(self, filters, output_path=None):
    """Generar PDF con logging"""
    logger.info(f"Iniciando generación de PDF con filtros: {filters}")
    
    try:
        # ... código de generación ...
        logger.info("PDF generado exitosamente")
        return output_path
    except Exception as e:
        logger.error(f"Error generando PDF: {str(e)}")
        raise
```

---

**Con esta guía puedes personalizar completamente los reportes según tus necesidades específicas sin afectar la funcionalidad principal del sistema.**


