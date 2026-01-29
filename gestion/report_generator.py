from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import pandas as pd
from datetime import datetime
from django.utils import timezone
from .models import Visita, Laboratorio, Software, Estudiante
from django.db.models import Q, Count
from django.conf import settings
import os
try:
    from svglib.svglib import svg2rlg
    SVG_SUPPORT = True
except ImportError:
    SVG_SUPPORT = False


class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configurar estilos personalizados para el reporte"""
        # Estilo para el título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#063579'),
            fontName='Helvetica-Bold',
            leading=32
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=15,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#1e293b'),
            fontName='Helvetica-Bold',
            leading=22
        ))
        
        # Estilo para subtítulos centrados
        self.styles.add(ParagraphStyle(
            name='CustomSubtitleCenter',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#475569'),
            fontName='Helvetica',
            leading=20
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            alignment=TA_LEFT,
            fontName='Helvetica',
            leading=14
        ))
        
        # Estilo para texto normal centrado
        self.styles.add(ParagraphStyle(
            name='CustomNormalCenter',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica',
            leading=14
        ))
        
        # Estilo para encabezados de tabla
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.white,
            fontName='Helvetica-Bold'
        ))

    def generate_pdf_report(self, filters, output_path=None):
        """Generar reporte PDF con excelente presentación"""
        if output_path is None:
            output_path = BytesIO()
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=60,
            bottomMargin=50
        )
        
        story = []
        
        # Página de portada
        story.extend(self._create_cover_page(filters))
        story.append(PageBreak())
        
        # Resumen ejecutivo
        story.extend(self._create_executive_summary(filters))
        story.append(PageBreak())
        
        # Estadísticas detalladas
        story.extend(self._create_detailed_statistics(filters))
        story.append(PageBreak())
        
        # Gráficos y análisis
        story.extend(self._create_charts_analysis(filters))
        story.append(PageBreak())
        
        # Tablas detalladas
        story.extend(self._create_detailed_tables(filters))
        story.append(PageBreak())
        
        # Sección de todas las visitas
        story.extend(self._create_all_visits_section(filters))
        
        # Construir el PDF
        doc.build(story)
        
        if isinstance(output_path, BytesIO):
            output_path.seek(0)
            return output_path.getvalue()
        
        return output_path

    def _create_cover_page(self, filters):
        """Crear página de portada del reporte"""
        elements = []
        
        # Logo de la UAA
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.svg')
        if not os.path.exists(logo_path):
            logo_path = os.path.join(settings.BASE_DIR, 'staticfiles', 'img', 'logo.svg')
        
        if os.path.exists(logo_path) and SVG_SUPPORT:
            try:
                # Intentar cargar SVG usando svglib
                drawing = svg2rlg(logo_path)
                if drawing:
                    # Escalar el logo apropiadamente
                    original_width = drawing.width
                    original_height = drawing.height
                    target_width = 2.5 * inch
                    scale_factor = target_width / original_width
                    drawing.width = target_width
                    drawing.height = original_height * scale_factor
                    drawing.scale(scale_factor, scale_factor)
                    # Centrar el logo usando una tabla
                    logo_table = Table([[drawing]], colWidths=[7*inch])
                    logo_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ]))
                    elements.append(logo_table)
                    elements.append(Spacer(1, 0.3*inch))
            except Exception as e:
                # Si falla, continuar sin logo
                print(f"No se pudo cargar el logo SVG: {e}")
                elements.append(Spacer(1, 1.5*inch))
        else:
            elements.append(Spacer(1, 1.5*inch))
        
        # Título principal
        title = Paragraph("REPORTE DE USO DE LABORATORIOS", self.styles['CustomTitle'])
        elements.append(title)
        
        elements.append(Spacer(1, 0.4*inch))
        
        # Subtítulo con información institucional
        subtitle_text = """
        <b>Edificio 55</b><br/>
        Departamento de Sistemas de Información<br/>
        Universidad Autónoma de Aguascalientes
        """
        subtitle = Paragraph(subtitle_text, self.styles['CustomSubtitleCenter'])
        elements.append(subtitle)
        
        elements.append(Spacer(1, 0.8*inch))
        
        # Información del período en un formato más formal
        period_info = self._get_period_info(filters)
        period_text = Paragraph(
            f"<b>Período de Análisis:</b><br/>{period_info}",
            self.styles['CustomNormalCenter']
        )
        elements.append(period_text)
        
        # Filtros aplicados
        filters_text = self._get_filters_text(filters)
        if filters_text:
            elements.append(Spacer(1, 0.3*inch))
            filters_para = Paragraph(
                f"<b>Filtros Aplicados:</b><br/>{filters_text}",
                self.styles['CustomNormalCenter']
            )
            elements.append(filters_para)
        
        elements.append(Spacer(1, 1.2*inch))
        
        # Fecha de generación
        current_date = timezone.localtime(timezone.now())
        date_text = Paragraph(
            f"<b>Fecha de Generación:</b><br/>{current_date.strftime('%d de %B de %Y')}<br/>{current_date.strftime('%H:%M horas')}",
            self.styles['CustomNormalCenter']
        )
        elements.append(date_text)
        
        return elements

    def _create_executive_summary(self, filters):
        """Crear resumen ejecutivo"""
        elements = []
        
        # Título de sección
        title = Paragraph("RESUMEN EJECUTIVO", self.styles['CustomSubtitle'])
        elements.append(title)
        
        # Obtener estadísticas principales
        stats = self._get_filtered_stats(filters)
        
        # Crear tabla de resumen
        summary_data = [
            ['Métrica', 'Valor', 'Descripción'],
            ['Total de Visitas', f"{stats['total_visitas']:,}", 'Número total de sesiones registradas'],
            ['Promedio Diario', f"{stats['promedio_diario']:.1f}", 'Visitas promedio por día'],
            ['Tiempo Total', f"{stats['tiempo_total_horas']:.1f} horas", 'Tiempo total de uso'],
            ['Usuarios Únicos', f"{stats['sesiones_unicas']:,}", 'Número de usuarios distintos'],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.2*inch, 1.8*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#063579')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
            ('TOPPADDING', (0, 0), (-1, 0), 14),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Análisis de tendencias
        analysis = self._get_trend_analysis(filters)
        if analysis:
            analysis_para = Paragraph(f"<b>Análisis de Tendencias:</b><br/>{analysis}", self.styles['CustomNormal'])
            elements.append(analysis_para)
        
        return elements

    def _create_detailed_statistics(self, filters):
        """Crear estadísticas detalladas"""
        elements = []
        
        title = Paragraph("ESTADÍSTICAS DETALLADAS", self.styles['CustomSubtitle'])
        elements.append(title)
        
        # Uso por laboratorio
        lab_usage = self._get_lab_usage_data(filters)
        if lab_usage:
            elements.append(Paragraph("Uso por Laboratorio", self.styles['CustomSubtitle']))
            
            lab_data = [['Laboratorio', 'Visitas', 'Horas', 'Promedio/Visita']]
            for lab in lab_usage:
                avg_time = lab['horas'] / lab['visitas'] if lab['visitas'] > 0 else 0
                lab_data.append([
                    lab['name'],
                    f"{lab['visitas']:,}",
                    f"{lab['horas']:.1f}h",
                    f"{avg_time:.1f}h"
                ])
            
            lab_table = Table(lab_data, colWidths=[2.2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            lab_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#063579')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
                ('TOPPADDING', (0, 0), (-1, 0), 14),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ]))
            
            elements.append(lab_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # Uso de software
        software_usage = self._get_software_usage_data(filters)
        if software_usage:
            elements.append(Paragraph("Uso de Software", self.styles['CustomSubtitle']))
            
            soft_data = [['Software', 'Usos', 'Porcentaje']]
            total_usos = sum(item['value'] for item in software_usage)
            for soft in software_usage:
                percentage = (soft['value'] / total_usos * 100) if total_usos > 0 else 0
                soft_data.append([
                    soft['name'],
                    f"{soft['value']:,}",
                    f"{percentage:.1f}%"
                ])
            
            soft_table = Table(soft_data, colWidths=[3.5*inch, 1.5*inch, 1.5*inch])
            soft_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#063579')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
                ('TOPPADDING', (0, 0), (-1, 0), 14),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ]))
            
            elements.append(soft_table)
        
        return elements

    def _create_charts_analysis(self, filters):
        """Crear análisis con gráficos"""
        elements = []
        
        title = Paragraph("ANÁLISIS GRÁFICO", self.styles['CustomSubtitle'])
        elements.append(title)
        
        # Crear gráfico de barras para laboratorios
        lab_usage = self._get_lab_usage_data(filters)
        if lab_usage:
            elements.append(Paragraph("Distribución de Uso por Laboratorio", self.styles['CustomSubtitle']))
            
            # Crear gráfico simple con texto
            chart_data = []
            for lab in lab_usage[:5]:  # Top 5 laboratorios
                chart_data.append(f"• {lab['name']}: {lab['visitas']} visitas ({lab['horas']:.1f}h)")
            
            chart_text = "<br/>".join(chart_data)
            chart_para = Paragraph(chart_text, self.styles['CustomNormal'])
            elements.append(chart_para)
            elements.append(Spacer(1, 0.3*inch))
        
        # Análisis de tendencias temporales
        daily_trend = self._get_daily_trend_data(filters)
        if daily_trend:
            elements.append(Paragraph("Tendencia por Día de la Semana", self.styles['CustomSubtitle']))
            
            trend_data = []
            for day in daily_trend:
                trend_data.append(f"• {day['dia']}: {day['visitas']} visitas")
            
            trend_text = "<br/>".join(trend_data)
            trend_para = Paragraph(trend_text, self.styles['CustomNormal'])
            elements.append(trend_para)
        
        return elements

    def _create_detailed_tables(self, filters):
        """Crear tablas detalladas"""
        elements = []
        
        title = Paragraph("TABLAS DETALLADAS", self.styles['CustomSubtitle'])
        elements.append(title)
        
        # Top usuarios
        top_users = self._get_top_users_data(filters)
        if top_users:
            elements.append(Paragraph("Usuarios Más Activos", self.styles['CustomSubtitle']))
            
            users_data = [['Usuario', 'Visitas', 'Horas Totales', 'Promedio/Visita']]
            for user in top_users:
                avg_time = user['horas'] / user['visitas'] if user['visitas'] > 0 else 0
                users_data.append([
                    user['nombre'][:30] + "..." if len(user['nombre']) > 30 else user['nombre'],
                    f"{user['visitas']:,}",
                    f"{user['horas']:.1f}h",
                    f"{avg_time:.1f}h"
                ])
            
            users_table = Table(users_data, colWidths=[3*inch, 1.2*inch, 1.2*inch, 1.2*inch])
            users_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#063579')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
                ('TOPPADDING', (0, 0), (-1, 0), 14),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ]))
            
            elements.append(users_table)
        
        return elements

    def _create_all_visits_section(self, filters):
        """Crear sección con todas las visitas"""
        elements = []
        
        title = Paragraph("REGISTRO COMPLETO DE VISITAS", self.styles['CustomSubtitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Obtener todas las visitas filtradas
        visitas = self._get_all_visits_for_pdf(filters)
        
        if not visitas:
            no_data = Paragraph("No hay visitas registradas para los filtros seleccionados.", self.styles['CustomNormal'])
            elements.append(no_data)
            return elements
        
        # Crear tabla con todas las visitas
        # Dividir en páginas si hay muchas visitas
        visitas_per_page = 20  # Número de visitas por página
        
        for i in range(0, len(visitas), visitas_per_page):
            page_visitas = visitas[i:i + visitas_per_page]
            
            # Encabezados de la tabla
            visits_data = [['Estudiante', 'PC', 'Laboratorio', 'Software', 'Fecha Inicio', 'Fecha Fin', 'Duración']]
            
            for visita in page_visitas:
                # Truncar nombres largos para que quepan en la tabla
                estudiante = visita['estudiante'][:25] + "..." if len(visita['estudiante']) > 25 else visita['estudiante']
                software = visita['software'][:20] + "..." if len(visita['software']) > 20 else visita['software']
                
                fecha_inicio = visita['fecha_inicio']
                fecha_fin = visita['fecha_fin'] if visita['fecha_fin'] else 'En curso'
                duracion = visita['duracion'] if visita['duracion'] else '-'
                
                visits_data.append([
                    estudiante,
                    visita['pc'],
                    visita['laboratorio'],
                    software,
                    fecha_inicio,
                    fecha_fin,
                    duracion
                ])
            
            # Crear tabla - ajustar anchos para que quepan en la página A4
            # Ancho total disponible: ~7.5 inch (A4 width - margins)
            visits_table = Table(visits_data, colWidths=[1.3*inch, 0.6*inch, 0.9*inch, 1*inch, 1.1*inch, 1.1*inch, 0.7*inch])
            visits_table.setStyle(TableStyle([
                # Encabezado
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#063579')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Estudiante alineado a la izquierda
                ('ALIGN', (3, 1), (3, -1), 'LEFT'),  # Software alineado a la izquierda
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                # Filas alternadas
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ]))
            
            elements.append(visits_table)
            
            # Agregar información de paginación si hay más visitas
            if i + visitas_per_page < len(visitas):
                elements.append(Spacer(1, 0.2*inch))
                page_info = Paragraph(
                    f"<i>Mostrando visitas {i+1} a {min(i+visitas_per_page, len(visitas))} de {len(visitas)} totales</i>",
                    self.styles['CustomNormal']
                )
                elements.append(page_info)
                elements.append(PageBreak())
        
        # Información final
        elements.append(Spacer(1, 0.3*inch))
        total_info = Paragraph(
            f"<b>Total de visitas mostradas: {len(visitas)}</b>",
            self.styles['CustomNormal']
        )
        elements.append(total_info)
        
        return elements

    def _get_all_visits_for_pdf(self, filters):
        """Obtener todas las visitas para el PDF"""
        try:
            filters_q = Q()
            if filters.get('date_from'):
                filters_q &= Q(fecha_hora_inicio__date__gte=filters['date_from'])
            if filters.get('date_to'):
                filters_q &= Q(fecha_hora_inicio__date__lte=filters['date_to'])
            if filters.get('laboratory') and filters['laboratory'] != 'all':
                filters_q &= Q(pc__laboratorio__id=filters['laboratory'])
            if filters.get('software') and filters['software'] != 'all':
                filters_q &= Q(software_utilizado__id=filters['software'])
            
            # Obtener todas las visitas (sin límite para el PDF)
            visitas = Visita.objects.filter(filters_q).select_related(
                'estudiante', 'pc__laboratorio', 'software_utilizado'
            ).order_by('-fecha_hora_inicio')
            
            data = []
            for visita in visitas:
                try:
                    fecha_inicio_local = timezone.localtime(visita.fecha_hora_inicio)
                    fecha_fin_local = timezone.localtime(visita.fecha_hora_fin) if visita.fecha_hora_fin else None
                    
                    # Calcular duración
                    duracion = None
                    if fecha_fin_local:
                        diff = fecha_fin_local - fecha_inicio_local
                        horas = int(diff.total_seconds() // 3600)
                        minutos = int((diff.total_seconds() % 3600) // 60)
                        if horas > 0:
                            duracion = f"{horas}h {minutos}m"
                        else:
                            duracion = f"{minutos}m"
                    
                    data.append({
                        'id': visita.id,
                        'estudiante': visita.estudiante.nombre_completo if visita.estudiante else 'N/A',
                        'laboratorio': visita.pc.laboratorio.nombre if visita.pc and visita.pc.laboratorio else 'N/A',
                        'pc': str(visita.pc) if visita.pc else 'N/A',
                        'software': visita.software_utilizado.nombre if visita.software_utilizado else 'N/A',
                        'fecha_inicio': fecha_inicio_local.strftime('%d/%m/%Y %H:%M'),
                        'fecha_fin': fecha_fin_local.strftime('%d/%m/%Y %H:%M') if fecha_fin_local else None,
                        'duracion': duracion,
                        'estado': 'En uso' if visita.fecha_hora_fin is None else 'Terminado'
                    })
                except Exception as e:
                    # Continuar con la siguiente visita si hay un error
                    continue
            
            return data
        except Exception as e:
            # Retornar lista vacía si hay un error
            return []

    def generate_excel_report(self, filters, output_path=None):
        """Generar reporte Excel con excelente presentación"""
        if output_path is None:
            output_path = BytesIO()
        
        # Crear Excel con múltiples hojas
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Hoja 1: Resumen Ejecutivo
            self._create_excel_summary_sheet(writer, filters)
            
            # Hoja 2: Uso por Laboratorio
            self._create_excel_lab_usage_sheet(writer, filters)
            
            # Hoja 3: Uso de Software
            self._create_excel_software_sheet(writer, filters)
            
            # Hoja 4: Usuarios Activos
            self._create_excel_users_sheet(writer, filters)
            
            # Hoja 5: Datos Detallados
            self._create_excel_detailed_sheet(writer, filters)
            
            # Hoja 6: Registro Completo de Visitas
            self._create_excel_all_visits_sheet(writer, filters)
        
        if isinstance(output_path, BytesIO):
            output_path.seek(0)
            return output_path.getvalue()
        
        return output_path

    def _create_excel_summary_sheet(self, writer, filters):
        """Crear hoja de resumen en Excel"""
        stats = self._get_filtered_stats(filters)
        
        summary_data = {
            'Métrica': [
                'Total de Visitas',
                'Promedio Diario',
                'Tiempo Total (horas)',
                'Usuarios Únicos',
                'Período de Análisis',
                'Fecha de Generación'
            ],
            'Valor': [
                stats['total_visitas'],
                f"{stats['promedio_diario']:.1f}",
                f"{stats['tiempo_total_horas']:.1f}",
                stats['sesiones_unicas'],
                self._get_period_info(filters),
                timezone.localtime(timezone.now()).strftime("%d/%m/%Y %H:%M")
            ]
        }
        
        df = pd.DataFrame(summary_data)
        df.to_excel(writer, sheet_name='Resumen Ejecutivo', index=False)
        
        # Formatear la hoja
        worksheet = writer.sheets['Resumen Ejecutivo']
        worksheet.column_dimensions['A'].width = 25
        worksheet.column_dimensions['B'].width = 20

    def _create_excel_lab_usage_sheet(self, writer, filters):
        """Crear hoja de uso por laboratorio"""
        lab_usage = self._get_lab_usage_data(filters)
        
        if lab_usage:
            lab_data = []
            for lab in lab_usage:
                avg_time = lab['horas'] / lab['visitas'] if lab['visitas'] > 0 else 0
                lab_data.append({
                    'Laboratorio': lab['name'],
                    'Visitas': lab['visitas'],
                    'Horas Totales': round(lab['horas'], 1),
                    'Promedio por Visita (h)': round(avg_time, 1),
                    'Eficiencia (%)': round((lab['visitas'] / sum(l['visitas'] for l in lab_usage) * 100), 1) if lab_usage else 0
                })
            
            df = pd.DataFrame(lab_data)
            df.to_excel(writer, sheet_name='Uso por Laboratorio', index=False)
            
            # Formatear
            worksheet = writer.sheets['Uso por Laboratorio']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 30)
                worksheet.column_dimensions[column_letter].width = adjusted_width

    def _create_excel_software_sheet(self, writer, filters):
        """Crear hoja de uso de software"""
        software_usage = self._get_software_usage_data(filters)
        
        if software_usage:
            total_usos = sum(item['value'] for item in software_usage)
            soft_data = []
            for soft in software_usage:
                percentage = (soft['value'] / total_usos * 100) if total_usos > 0 else 0
                soft_data.append({
                    'Software': soft['name'],
                    'Usos': soft['value'],
                    'Porcentaje (%)': round(percentage, 1),
                    'Categoría': self._get_software_category(soft['name'])
                })
            
            df = pd.DataFrame(soft_data)
            df.to_excel(writer, sheet_name='Uso de Software', index=False)

    def _create_excel_users_sheet(self, writer, filters):
        """Crear hoja de usuarios activos"""
        top_users = self._get_top_users_data(filters)
        
        if top_users:
            users_data = []
            for user in top_users:
                avg_time = user['horas'] / user['visitas'] if user['visitas'] > 0 else 0
                users_data.append({
                    'Usuario': user['nombre'],
                    'Visitas': user['visitas'],
                    'Horas Totales': round(user['horas'], 1),
                    'Promedio por Visita (h)': round(avg_time, 1),
                    'Ranking': len(users_data) + 1
                })
            
            df = pd.DataFrame(users_data)
            df.to_excel(writer, sheet_name='Usuarios Activos', index=False)

    def _create_excel_detailed_sheet(self, writer, filters):
        """Crear hoja con datos detallados"""
        # Obtener todas las visitas filtradas
        visitas = self._get_detailed_visits_data(filters)
        
        if visitas:
            visits_data = []
            for visita in visitas:
                duracion = 0
                if visita['fecha_fin'] and visita['fecha_inicio']:
                    inicio = timezone.datetime.fromisoformat(visita['fecha_inicio'].replace('Z', '+00:00'))
                    fin = timezone.datetime.fromisoformat(visita['fecha_fin'].replace('Z', '+00:00'))
                    duracion = (fin - inicio).total_seconds() / 3600
                
                visits_data.append({
                    'ID': visita['id'],
                    'Estudiante': visita['estudiante'],
                    'Laboratorio': visita['laboratorio'],
                    'PC': visita['pc'],
                    'Software': visita['software'],
                    'Fecha Inicio': visita['fecha_inicio'],
                    'Fecha Fin': visita['fecha_fin'] or 'En curso',
                    'Duración (h)': round(duracion, 2),
                    'Estado': visita['estado']
                })
            
            df = pd.DataFrame(visits_data)
            df.to_excel(writer, sheet_name='Datos Detallados', index=False)

    def _create_excel_all_visits_sheet(self, writer, filters):
        """Crear hoja con todas las visitas (similar a la sección del PDF)"""
        # Obtener todas las visitas filtradas
        visitas = self._get_all_visits_for_pdf(filters)
        
        if visitas:
            visits_data = []
            for visita in visitas:
                visits_data.append({
                    'ID': visita['id'],
                    'Estudiante': visita['estudiante'],
                    'PC': visita['pc'],
                    'Laboratorio': visita['laboratorio'],
                    'Software': visita['software'],
                    'Fecha Inicio': visita['fecha_inicio'],
                    'Fecha Fin': visita['fecha_fin'] or 'En curso',
                    'Duración': visita['duracion'] or '-',
                    'Estado': visita['estado']
                })
            
            df = pd.DataFrame(visits_data)
            df.to_excel(writer, sheet_name='Registro Completo de Visitas', index=False)
            
            # Formatear la hoja
            worksheet = writer.sheets['Registro Completo de Visitas']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 30)
                worksheet.column_dimensions[column_letter].width = adjusted_width

    # Métodos auxiliares para obtener datos
    def _get_filtered_stats(self, filters):
        """Obtener estadísticas filtradas"""
        from .views import api_reports_filtered_stats
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/api/reports/filtered-stats/', filters)
        
        # Simular la lógica de la API
        filters_q = Q()
        if filters.get('date_from'):
            filters_q &= Q(fecha_hora_inicio__date__gte=filters['date_from'])
        if filters.get('date_to'):
            filters_q &= Q(fecha_hora_inicio__date__lte=filters['date_to'])
        if filters.get('laboratory') and filters['laboratory'] != 'all':
            filters_q &= Q(pc__laboratorio__id=filters['laboratory'])
        if filters.get('software') and filters['software'] != 'all':
            filters_q &= Q(software_utilizado__id=filters['software'])
        
        visitas_filtradas = Visita.objects.filter(filters_q)
        total_visitas = visitas_filtradas.count()
        
        # Promedio diario
        if filters.get('date_from') and filters.get('date_to'):
            from datetime import datetime
            fecha_inicio = datetime.strptime(filters['date_from'], '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(filters['date_to'], '%Y-%m-%d').date()
            dias = (fecha_fin - fecha_inicio).days + 1
            promedio_diario = round(total_visitas / dias, 1) if dias > 0 else 0
        else:
            promedio_diario = 0
        
        # Tiempo total
        visitas_completadas = visitas_filtradas.filter(fecha_hora_fin__isnull=False)
        tiempo_total_horas = 0
        for visita in visitas_completadas:
            if visita.fecha_hora_fin and visita.fecha_hora_inicio:
                diff = visita.fecha_hora_fin - visita.fecha_hora_inicio
                tiempo_total_horas += diff.total_seconds() / 3600
        
        sesiones_unicas = visitas_filtradas.values('estudiante').distinct().count()
        
        return {
            'total_visitas': total_visitas,
            'promedio_diario': promedio_diario,
            'tiempo_total_horas': round(tiempo_total_horas, 1),
            'sesiones_unicas': sesiones_unicas
        }

    def _get_lab_usage_data(self, filters):
        """Obtener datos de uso por laboratorio"""
        from .views import api_reports_lab_usage
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/api/reports/lab-usage/', filters)
        
        # Simular la lógica de la API
        filters_q = Q()
        if filters.get('date_from'):
            filters_q &= Q(fecha_hora_inicio__date__gte=filters['date_from'])
        if filters.get('date_to'):
            filters_q &= Q(fecha_hora_inicio__date__lte=filters['date_to'])
        
        if filters.get('laboratory') and filters['laboratory'] != 'all':
            labs = Laboratorio.objects.filter(id=filters['laboratory'])
        else:
            labs = Laboratorio.objects.all()
        
        data = []
        for lab in labs:
            visitas = Visita.objects.filter(filters_q, pc__laboratorio=lab)
            total_visitas = visitas.count()
            
            horas_totales = 0
            for visita in visitas.filter(fecha_hora_fin__isnull=False):
                if visita.fecha_hora_fin and visita.fecha_hora_inicio:
                    diff = visita.fecha_hora_fin - visita.fecha_hora_inicio
                    horas_totales += diff.total_seconds() / 3600
            
            data.append({
                'name': lab.nombre,
                'visitas': total_visitas,
                'horas': round(horas_totales, 1)
            })
        
        return data

    def _get_software_usage_data(self, filters):
        """Obtener datos de uso de software"""
        from .views import api_reports_software_usage
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/api/reports/software-usage/', filters)
        
        # Simular la lógica de la API
        filters_q = Q()
        if filters.get('date_from'):
            filters_q &= Q(fecha_hora_inicio__date__gte=filters['date_from'])
        if filters.get('date_to'):
            filters_q &= Q(fecha_hora_inicio__date__lte=filters['date_to'])
        
        if filters.get('software') and filters['software'] != 'all':
            software_list = Software.objects.filter(id=filters['software'])
        else:
            software_list = Software.objects.all()
        
        data = []
        for soft in software_list:
            usos = Visita.objects.filter(filters_q, software_utilizado=soft).count()
            if usos > 0:
                data.append({
                    'name': soft.nombre,
                    'value': usos
                })
        
        return data

    def _get_daily_trend_data(self, filters):
        """Obtener datos de tendencia diaria"""
        from .views import api_reports_daily_trend
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/api/reports/daily-trend/', filters)
        
        # Simular la lógica de la API
        filters_q = Q()
        if filters.get('date_from'):
            filters_q &= Q(fecha_hora_inicio__date__gte=filters['date_from'])
        if filters.get('date_to'):
            filters_q &= Q(fecha_hora_inicio__date__lte=filters['date_to'])
        if filters.get('laboratory') and filters['laboratory'] != 'all':
            filters_q &= Q(pc__laboratorio__id=filters['laboratory'])
        
        visitas_por_dia = Visita.objects.filter(filters_q).extra(
            select={'day_of_week': 'extract(dow from fecha_hora_inicio)'}
        ).values('day_of_week').annotate(
            count=Count('id')
        ).order_by('day_of_week')
        
        dias_semana = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
        
        data = []
        for item in visitas_por_dia:
            dia_num = int(item['day_of_week'])
            data.append({
                'dia': dias_semana[dia_num],
                'visitas': item['count']
            })
        
        return data

    def _get_top_users_data(self, filters):
        """Obtener datos de usuarios más activos"""
        from .views import api_reports_top_users
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/api/reports/top-users/', filters)
        
        # Simular la lógica de la API
        filters_q = Q()
        if filters.get('date_from'):
            filters_q &= Q(fecha_hora_inicio__date__gte=filters['date_from'])
        if filters.get('date_to'):
            filters_q &= Q(fecha_hora_inicio__date__lte=filters['date_to'])
        if filters.get('laboratory') and filters['laboratory'] != 'all':
            filters_q &= Q(pc__laboratorio__id=filters['laboratory'])
        if filters.get('software') and filters['software'] != 'all':
            filters_q &= Q(software_utilizado__id=filters['software'])
        
        usuarios_stats = Visita.objects.filter(filters_q).values(
            'estudiante__nombre_completo'
        ).annotate(
            total_visitas=Count('id')
        ).order_by('-total_visitas')[:5]
        
        data = []
        for usuario in usuarios_stats:
            visitas_usuario = Visita.objects.filter(
                filters_q, 
                estudiante__nombre_completo=usuario['estudiante__nombre_completo']
            ).filter(fecha_hora_fin__isnull=False)
            
            horas_totales = 0
            for visita in visitas_usuario:
                if visita.fecha_hora_fin and visita.fecha_hora_inicio:
                    diff = visita.fecha_hora_fin - visita.fecha_hora_inicio
                    horas_totales += diff.total_seconds() / 3600
            
            data.append({
                'nombre': usuario['estudiante__nombre_completo'],
                'visitas': usuario['total_visitas'],
                'horas': round(horas_totales, 1)
            })
        
        return data

    def _get_detailed_visits_data(self, filters):
        """Obtener datos detallados de visitas"""
        filters_q = Q()
        if filters.get('date_from'):
            filters_q &= Q(fecha_hora_inicio__date__gte=filters['date_from'])
        if filters.get('date_to'):
            filters_q &= Q(fecha_hora_inicio__date__lte=filters['date_to'])
        if filters.get('laboratory') and filters['laboratory'] != 'all':
            filters_q &= Q(pc__laboratorio__id=filters['laboratory'])
        if filters.get('software') and filters['software'] != 'all':
            filters_q &= Q(software_utilizado__id=filters['software'])
        
        visitas = Visita.objects.filter(filters_q).select_related(
            'estudiante', 'pc__laboratorio', 'software_utilizado'
        ).order_by('-fecha_hora_inicio')[:100]  # Limitar a 100 registros
        
        data = []
        for visita in visitas:
            fecha_inicio_local = timezone.localtime(visita.fecha_hora_inicio)
            fecha_fin_local = timezone.localtime(visita.fecha_hora_fin) if visita.fecha_hora_fin else None
            
            data.append({
                'id': visita.id,
                'estudiante': visita.estudiante.nombre_completo,
                'laboratorio': visita.pc.laboratorio.nombre,
                'pc': str(visita.pc),
                'software': visita.software_utilizado.nombre if visita.software_utilizado else 'N/A',
                'fecha_inicio': fecha_inicio_local.strftime('%Y-%m-%d %H:%M'),
                'fecha_fin': fecha_fin_local.strftime('%Y-%m-%d %H:%M') if fecha_fin_local else None,
                'estado': 'En uso' if visita.fecha_hora_fin is None else 'Terminado'
            })
        
        return data

    def _get_period_info(self, filters):
        """Obtener información del período"""
        if filters.get('date_from') and filters.get('date_to'):
            return f"{filters['date_from']} a {filters['date_to']}"
        elif filters.get('period'):
            period_map = {
                'monthly': 'Último mes',
                'bimonthly': 'Últimos 2 meses',
                'quarterly': 'Últimos 3 meses',
                'semiannual': 'Últimos 6 meses',
                'annual': 'Último año'
            }
            return period_map.get(filters['period'], 'Período personalizado')
        return 'Todos los datos disponibles'

    def _get_filters_text(self, filters):
        """Obtener texto de filtros aplicados"""
        filters_text = []
        
        if filters.get('laboratory') and filters['laboratory'] != 'all':
            try:
                lab = Laboratorio.objects.get(id=filters['laboratory'])
                filters_text.append(f"Laboratorio: {lab.nombre}")
            except:
                pass
        
        if filters.get('software') and filters['software'] != 'all':
            try:
                soft = Software.objects.get(id=filters['software'])
                filters_text.append(f"Software: {soft.nombre}")
            except:
                pass
        
        if filters.get('userType') and filters['userType'] != 'all':
            user_types = {
                'student': 'Estudiantes',
                'professor': 'Profesores',
                'staff': 'Personal administrativo'
            }
            filters_text.append(f"Tipo de usuario: {user_types.get(filters['userType'], filters['userType'])}")
        
        return "<br/>".join(filters_text)

    def _get_trend_analysis(self, filters):
        """Obtener análisis de tendencias"""
        stats = self._get_filtered_stats(filters)
        
        if stats['total_visitas'] == 0:
            return "No hay datos suficientes para el análisis de tendencias."
        
        analysis = []
        
        if stats['promedio_diario'] > 0:
            analysis.append(f"El promedio diario de {stats['promedio_diario']:.1f} visitas indica un uso ")
            if stats['promedio_diario'] > 20:
                analysis.append("muy activo")
            elif stats['promedio_diario'] > 10:
                analysis.append("moderado")
            else:
                analysis.append("bajo")
            analysis.append(" de los laboratorios.")
        
        if stats['tiempo_total_horas'] > 0:
            avg_session = stats['tiempo_total_horas'] / stats['total_visitas']
            analysis.append(f"La duración promedio de {avg_session:.1f} horas por sesión sugiere un uso ")
            if avg_session > 3:
                analysis.append("intensivo")
            elif avg_session > 1.5:
                analysis.append("moderado")
            else:
                analysis.append("rápido")
            analysis.append(" de los recursos.")
        
        return " ".join(analysis)

    def _get_software_category(self, software_name):
        """Obtener categoría del software"""
        categories = {
            'AutoCAD': 'CAD/Diseño',
            'SolidWorks': 'CAD/Diseño',
            'MATLAB': 'Programación/Análisis',
            'LabVIEW': 'Programación/Análisis',
            'Office': 'Productividad',
            'Visual Studio': 'Programación/Análisis',
            'Python': 'Programación/Análisis'
        }
        
        for key, category in categories.items():
            if key.lower() in software_name.lower():
                return category
        
        return 'Otros'



