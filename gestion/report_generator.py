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
from io import BytesIO
import pandas as pd
from datetime import datetime
from django.utils import timezone
from .models import Visita, Laboratorio, Software, Estudiante
from django.db.models import Q, Count
import os


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
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1e40af')
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#374151')
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            alignment=TA_LEFT
        ))
        
        # Estilo para encabezados de tabla
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.white
        ))

    def generate_pdf_report(self, filters, output_path=None):
        """Generar reporte PDF con excelente presentación"""
        if output_path is None:
            output_path = BytesIO()
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
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
        
        # Construir el PDF
        doc.build(story)
        
        if isinstance(output_path, BytesIO):
            output_path.seek(0)
            return output_path.getvalue()
        
        return output_path

    def _create_cover_page(self, filters):
        """Crear página de portada del reporte"""
        elements = []
        
        # Logo/Header
        elements.append(Spacer(1, 2*inch))
        
        # Título principal
        title = Paragraph("REPORTE DE USO DE LABORATORIOS", self.styles['CustomTitle'])
        elements.append(title)
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Subtítulo
        subtitle = Paragraph("Edificio 55 - Universidad Autónoma de Aguascalientes", self.styles['CustomSubtitle'])
        elements.append(subtitle)
        
        elements.append(Spacer(1, 1*inch))
        
        # Información del período
        period_info = self._get_period_info(filters)
        period_text = Paragraph(f"<b>Período de Análisis:</b> {period_info}", self.styles['CustomNormal'])
        elements.append(period_text)
        
        # Filtros aplicados
        filters_text = self._get_filters_text(filters)
        if filters_text:
            elements.append(Spacer(1, 0.3*inch))
            filters_para = Paragraph(f"<b>Filtros Aplicados:</b><br/>{filters_text}", self.styles['CustomNormal'])
            elements.append(filters_para)
        
        elements.append(Spacer(1, 1*inch))
        
        # Fecha de generación
        current_date = timezone.localtime(timezone.now()).strftime("%d de %B de %Y")
        date_text = Paragraph(f"<b>Fecha de Generación:</b> {current_date}", self.styles['CustomNormal'])
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
        
        summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
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
            
            lab_table = Table(lab_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            lab_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fdf4')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
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
            
            soft_table = Table(soft_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            soft_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fef2f2')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
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
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#faf5ff')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            elements.append(users_table)
        
        return elements

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


