from django.contrib import admin
from .models import Laboratorio, Software, PC, Estudiante, ReservaClase, Visita, SerieReserva, DiaSemana, Mantenimiento, SesionActiva, CalendarioSemanal
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from .forms import RecurrenciaForm, MantenimientoForm, EstudianteAdminForm, SerieReservaAdminForm
from .widgets import ColorPickerWidget
from datetime import timedelta, datetime
from django.urls import path
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from django.utils.safestring import mark_safe

# --- Clases de Administración existentes ---

class SoftwareInline(admin.TabularInline):
    model = Software.laboratorios.through
    verbose_name = "Software Instalado"
    verbose_name_plural = "Software Instalado"
    extra = 1

class SoftwareAdmin(admin.ModelAdmin):
    # 1. Ordena la lista alfabéticamente por nombre
    ordering = ('nombre',)

    # 2. Añade un filtro por laboratorios
    list_filter = ('laboratorios',)

    # 3. Mejora las columnas que se muestran en la lista
    list_display = ('nombre', 'version', 'get_laboratorios')

    # Opcional: añade una barra de búsqueda
    search_fields = ('nombre',)

    # Esta función crea el texto para la columna "Laboratorios"
    def get_laboratorios(self, obj):
        # Une los nombres de todos los laboratorios asociados con una coma
        return ", ".join([lab.nombre for lab in obj.laboratorios.all()])
    get_laboratorios.short_description = 'Instalado en' # Nombre de la columna

class PCInline(admin.TabularInline):
    model = PC
    extra = 1
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Ordenar laboratorios alfabéticamente"""
        if db_field.name == "laboratorio":
            kwargs["queryset"] = Laboratorio.objects.all().order_by('nombre')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class PCAdmin(admin.ModelAdmin):
    # Columnas a mostrar en la lista
    list_display = ('__str__', 'laboratorio', 'estado', 'get_disponibilidad')

    # Panel de filtro a la derecha
    list_filter = ('laboratorio', 'estado')

    # Orden por defecto: primero por laboratorio, luego por número de PC
    ordering = ('laboratorio', 'numero_pc')

    # Barra de búsqueda
    search_fields = ('laboratorio__nombre', 'numero_pc')
    
    # Acciones personalizadas
    actions = ['actualizar_estados_segun_reservas']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Ordenar laboratorios alfabéticamente"""
        if db_field.name == "laboratorio":
            kwargs["queryset"] = Laboratorio.objects.all().order_by('nombre')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_disponibilidad(self, obj):
        """Muestra si la PC está disponible para uso individual"""
        if obj.esta_disponible_para_uso():
            return "✅ Disponible para uso individual"
        else:
            return "❌ No disponible para uso individual"
    get_disponibilidad.short_description = 'Disponibilidad'
    
    def actualizar_estados_segun_reservas(self, request, queryset):
        """Acción para actualizar estados de PCs según reservas activas"""
        from django.core.management import call_command
        call_command('actualizar_estados_pcs')
        self.message_user(request, "✅ Estados de PCs actualizados según reservas activas")
    actualizar_estados_segun_reservas.short_description = "Actualizar estados según reservas activas"
    
    def save_model(self, request, obj, form, change):
        """Sobrescribe el método save para crear mantenimiento automáticamente"""
        from django.utils import timezone
        
        # Si es una edición (change=True), verificar si el estado cambió a Mantenimiento
        if change:
            # Obtener el objeto original de la base de datos
            original_obj = PC.objects.get(pk=obj.pk)
            estado_anterior = original_obj.estado
            estado_nuevo = obj.estado
            
            # Si el estado cambió a Mantenimiento, crear un registro de mantenimiento
            if estado_anterior != 'Mantenimiento' and estado_nuevo == 'Mantenimiento':
                # Verificar si ya existe un mantenimiento activo para esta PC
                mantenimiento_activo = Mantenimiento.objects.filter(
                    pc=obj,
                    fecha_fin__isnull=True
                ).exists()
                
                if not mantenimiento_activo:
                    Mantenimiento.objects.create(
                        pc=obj,
                        descripcion='',  # Vacío porque se cambió desde PC
                        fecha_inicio=timezone.now()
                    )
                    self.message_user(request, f"✅ Se creó automáticamente un registro de mantenimiento para {obj}", messages.SUCCESS)
        
        # Guardar el objeto
        super().save_model(request, obj, form, change)

class LaboratorioAdmin(admin.ModelAdmin):
    # 1. Añade el inline para PCs
    inlines = [PCInline, SoftwareInline]

    # 2. Mejora las columnas que se muestran en la lista
    list_display = ('nombre', 'get_pc_count', 'get_software_count')

    # 3. Añade una barra de búsqueda
    search_fields = ('nombre', 'descripcion')

    # 4. Añade un filtro por descripción (si no está vacía)
    list_filter = ('descripcion',)

    # Esta función cuenta las PCs en cada laboratorio
    def get_pc_count(self, obj):
        return obj.pc_set.count()
    get_pc_count.short_description = 'Número de PCs'

    # Esta función cuenta el software instalado en cada laboratorio
    def get_software_count(self, obj):
        return obj.software_instalado.count()
    get_software_count.short_description = 'Software Instalado'

class VisitaAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'pc', 'software_utilizado', 'fecha_hora_inicio', 'fecha_hora_fin', 'get_duracion')
    list_filter = ('fecha_hora_inicio', 'pc__laboratorio', 'software_utilizado')
    search_fields = ('estudiante__nombre_completo', 'pc__laboratorio__nombre')
    date_hierarchy = 'fecha_hora_inicio'
    ordering = ('-fecha_hora_inicio',)
    
    def get_duracion(self, obj):
        if obj.fecha_hora_fin:
            duracion = obj.fecha_hora_fin - obj.fecha_hora_inicio
            horas = int(duracion.total_seconds() // 3600)
            minutos = int((duracion.total_seconds() % 3600) // 60)
            return f"{horas}h {minutos}m"
        return "En curso"
    get_duracion.short_description = 'Duración'

class EstudianteAdmin(admin.ModelAdmin):
    """Administración mejorada para Visitantes (Estudiantes)"""
    form = EstudianteAdminForm  # Usar formulario personalizado con dropdown de carreras
    
    list_display = (
        'id', 
        'nombre_completo', 
        'carrera',
        'correo', 
        'get_fecha_primer_registro',
        'get_total_visitas',
        'get_software_mas_usado',
        'get_ultima_visita'
    )
    
    list_filter = ('visita__fecha_hora_inicio', 'carrera')
    search_fields = ('id', 'nombre_completo', 'correo', 'carrera')
    ordering = ('nombre_completo',)
    
    def get_queryset(self, request):
        """Optimizar consultas para evitar N+1 queries"""
        qs = super().get_queryset(request)
        return qs.prefetch_related('visita_set', 'visita_set__software_utilizado')
    
    def get_fecha_primer_registro(self, obj):
        """Retorna la fecha de la primera visita del estudiante"""
        primera_visita = obj.visita_set.order_by('fecha_hora_inicio').first()
        if primera_visita:
            return primera_visita.fecha_hora_inicio.strftime('%d/%m/%Y %H:%M')
        return "Sin visitas"
    get_fecha_primer_registro.short_description = 'Primer Registro'
    get_fecha_primer_registro.admin_order_field = 'visita__fecha_hora_inicio'
    
    def get_total_visitas(self, obj):
        """Retorna el total de visitas del estudiante"""
        total = obj.visita_set.count()
        if total > 0:
            return format_html('<span style="font-weight: bold; color: #0066cc;">{}</span>', total)
        return 0
    get_total_visitas.short_description = 'Total Visitas'
    
    def get_software_mas_usado(self, obj):
        """Retorna el software más utilizado por el estudiante"""
        from django.db.models import Count
        
        software_stats = obj.visita_set.values('software_utilizado__nombre').annotate(
            count=Count('software_utilizado')
        ).order_by('-count').first()
        
        if software_stats and software_stats['software_utilizado__nombre']:
            nombre = software_stats['software_utilizado__nombre']
            count = software_stats['count']
            return format_html(
                '<span style="color: #28a745;">{}</span> <span style="color: #6c757d; font-size: 0.9em;">({}x)</span>',
                nombre, count
            )
        return format_html('<span style="color: #999;">N/A</span>')
    get_software_mas_usado.short_description = 'Software Más Usado'
    
    def get_ultima_visita(self, obj):
        """Retorna la fecha de la última visita del estudiante"""
        ultima_visita = obj.visita_set.order_by('-fecha_hora_inicio').first()
        if ultima_visita:
            fecha = ultima_visita.fecha_hora_inicio
            # Calcular hace cuánto tiempo
            from django.utils import timezone
            ahora = timezone.now()
            diferencia = ahora - fecha
            
            if diferencia.days == 0:
                tiempo_texto = "Hoy"
            elif diferencia.days == 1:
                tiempo_texto = "Ayer"
            elif diferencia.days < 7:
                tiempo_texto = f"Hace {diferencia.days} días"
            elif diferencia.days < 30:
                semanas = diferencia.days // 7
                tiempo_texto = f"Hace {semanas} semana{'s' if semanas > 1 else ''}"
            else:
                meses = diferencia.days // 30
                tiempo_texto = f"Hace {meses} mes{'es' if meses > 1 else ''}"
            
            return format_html(
                '<span style="color: #495057;">{}</span><br><span style="color: #6c757d; font-size: 0.85em;">{}</span>',
                fecha.strftime('%d/%m/%Y %H:%M'),
                tiempo_texto
            )
        return format_html('<span style="color: #999;">Sin visitas</span>')
    get_ultima_visita.short_description = 'Última Visita'
    get_ultima_visita.admin_order_field = '-visita__fecha_hora_inicio'

class MantenimientoAdmin(admin.ModelAdmin):
    """Administración de mantenimientos de PCs"""
    form = MantenimientoForm
    list_display = ('pc', 'get_laboratorio', 'descripcion', 'fecha_inicio', 'fecha_fin', 'get_estado', 'get_duracion', 'acciones')
    list_filter = ('fecha_inicio', 'pc__laboratorio', 'fecha_fin')
    search_fields = ('pc__laboratorio__nombre', 'pc__numero_pc', 'descripcion')
    date_hierarchy = 'fecha_inicio'
    ordering = ('-fecha_inicio',)
    
    fieldsets = (
        ('Información del Mantenimiento', {
            'fields': ('laboratorio', 'pc', 'descripcion', 'fecha_inicio', 'fecha_fin'),
            'description': 'Seleccione primero el laboratorio para filtrar las PCs disponibles'
        }),
    )
    
    readonly_fields = ()
    
    class Media:
        js = ('js/mantenimiento_form.js',)
    
    def get_laboratorio(self, obj):
        """Retorna el laboratorio al que pertenece la PC"""
        return obj.pc.laboratorio.nombre
    get_laboratorio.short_description = 'Laboratorio'
    
    def get_estado(self, obj):
        """Retorna el estado del mantenimiento con formato visual"""
        if obj.fecha_fin:
            return format_html('<span style="color: green; font-weight: bold;">✓ Terminado</span>')
        return format_html('<span style="color: orange; font-weight: bold;">● Activo</span>')
    get_estado.short_description = 'Estado'
    
    def get_duracion(self, obj):
        """Retorna la duración del mantenimiento"""
        return obj.get_duracion()
    get_duracion.short_description = 'Duración'
    
    def acciones(self, obj):
        """Botones de acción para cada mantenimiento"""
        if not obj.fecha_fin:
            finalizar_url = reverse('admin:finalizar_mantenimiento', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background-color: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Finalizar Mantenimiento</a>',
                finalizar_url
            )
        return format_html('<span style="color: #6c757d;">Finalizado</span>')
    acciones.short_description = 'Acciones'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('finalizar-mantenimiento/<int:mantenimiento_id>/', self.admin_site.admin_view(self.finalizar_mantenimiento_view), name='finalizar_mantenimiento'),
            path('get-pcs/', self.admin_site.admin_view(self.get_pcs_view), name='get_pcs'),
        ]
        return custom_urls + urls
    
    def get_pcs_view(self, request):
        """Vista AJAX para obtener las PCs de un laboratorio"""
        from django.http import JsonResponse
        import logging
        
        logger = logging.getLogger(__name__)
        laboratorio_id = request.GET.get('laboratorio_id')
        
        logger.info(f'get_pcs_view llamado con laboratorio_id: {laboratorio_id}')
        
        if laboratorio_id:
            try:
                pcs = PC.objects.filter(laboratorio_id=laboratorio_id).order_by('numero_pc')
                pcs_data = [{'id': pc.id, 'nombre': str(pc)} for pc in pcs]
                logger.info(f'PCs encontradas: {len(pcs_data)}')
                response = JsonResponse({'pcs': pcs_data})
                return response
            except Exception as e:
                logger.error(f'Error en get_pcs_view: {str(e)}')
                return JsonResponse({'error': str(e), 'pcs': []}, status=400)
        return JsonResponse({'pcs': []})
    
    def finalizar_mantenimiento_view(self, request, mantenimiento_id):
        """Vista para finalizar un mantenimiento"""
        from django.utils import timezone
        
        try:
            mantenimiento = Mantenimiento.objects.get(id=mantenimiento_id)
            
            if mantenimiento.fecha_fin:
                messages.warning(request, 'Este mantenimiento ya está finalizado')
            else:
                mantenimiento.fecha_fin = timezone.now()
                mantenimiento.save()
                
                # Cambiar el estado de la PC a Disponible si estaba en Mantenimiento
                if mantenimiento.pc.estado == 'Mantenimiento':
                    mantenimiento.pc.estado = 'Disponible'
                    mantenimiento.pc.save()
                
                messages.success(request, f'✅ Mantenimiento de {mantenimiento.pc} finalizado correctamente')
            
            return redirect('admin:gestion_mantenimiento_changelist')
        except Mantenimiento.DoesNotExist:
            messages.error(request, 'Mantenimiento no encontrado')
            return redirect('admin:gestion_mantenimiento_changelist')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Personaliza el queryset para el campo PC basado en el laboratorio"""
        if db_field.name == "pc":
            # Si hay un laboratorio seleccionado en el GET o POST, filtrar PCs
            laboratorio_id = request.GET.get('laboratorio') or request.POST.get('laboratorio')
            if laboratorio_id:
                kwargs["queryset"] = PC.objects.filter(laboratorio_id=laboratorio_id).order_by('numero_pc')
            else:
                # Si no hay laboratorio seleccionado, no mostrar PCs
                kwargs["queryset"] = PC.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """Sobrescribe el método save para:
        - Manejar el campo laboratorio (solo filtrado, no se guarda)
        - Asegurar que la PC cambie a estado 'Mantenimiento' cuando haya un mantenimiento activo
        - Opcionalmente devolver la PC a 'Disponible' si el mantenimiento se marca como finalizado aquí
        """
        from django.utils import timezone

        original_fecha_fin = None
        if change:
            # Obtener el estado anterior del mantenimiento
            try:
                original = Mantenimiento.objects.get(pk=obj.pk)
                original_fecha_fin = original.fecha_fin
            except Mantenimiento.DoesNotExist:
                pass

        # Establecer fecha_inicio por defecto si no está establecida
        if not obj.fecha_inicio:
            obj.fecha_inicio = timezone.now()

        super().save_model(request, obj, form, change)

        # Si el mantenimiento NO tiene fecha_fin, considerarlo activo
        if obj.pc:
            if obj.fecha_fin is None:
                # Asegurar que la PC esté en estado 'Mantenimiento'
                if obj.pc.estado != "Mantenimiento":
                    obj.pc.estado = "Mantenimiento"
                    obj.pc.save()
            else:
                # Si antes no tenía fecha_fin (activo) y ahora sí, podemos devolver la PC a 'Disponible'
                # (esto cubre el caso de que el admin edite manualmente sin usar el botón de finalizar)
                if original_fecha_fin is None and obj.pc.estado == "Mantenimiento":
                    obj.pc.estado = "Disponible"
                    obj.pc.save()
    
    def get_queryset(self, request):
        """Optimizar consultas para evitar N+1 queries"""
        qs = super().get_queryset(request)
        return qs.select_related('pc', 'pc__laboratorio')

class ReservaClaseAdmin(admin.ModelAdmin):
    list_display = ('laboratorio', 'profesor', 'materia', 'fecha_hora_inicio', 'fecha_hora_fin', 'serie')
    list_filter = (
        'laboratorio', 
        'serie',
        'profesor',
        'materia',
        ('fecha_hora_inicio', admin.DateFieldListFilter),
    )
    search_fields = ('profesor', 'materia', 'laboratorio__nombre', 'serie__nombre')
    date_hierarchy = 'fecha_hora_inicio'
    ordering = ('-fecha_hora_inicio',)
    
    def get_queryset(self, request):
        """Optimizar consultas para evitar N+1 queries"""
        qs = super().get_queryset(request)
        return qs.select_related('laboratorio', 'serie')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Ordenar laboratorios alfabéticamente"""
        if db_field.name == "laboratorio":
            kwargs["queryset"] = Laboratorio.objects.all().order_by('nombre')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Use color picker widget for color field"""
        if db_field.name == 'color':
            kwargs['widget'] = ColorPickerWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    def get_urls(self):
        """Add custom URLs for calendar view"""
        urls = super().get_urls()
        custom_urls = [
            path('calendario-semanal/', self.admin_site.admin_view(self.calendario_semanal_view), name='gestion_reservaclase_calendario'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        """Add calendar link to the changelist view"""
        extra_context = extra_context or {}
        extra_context['show_calendario_link'] = True
        return super().changelist_view(request, extra_context)
    
    def calendario_semanal_view(self, request):
        """Vista del calendario semanal"""
        from datetime import datetime, timedelta, time
        from django.utils import timezone
        from collections import defaultdict
        
        # Get week offset (0 = current week, -1 = previous week, 1 = next week)
        week_offset = int(request.GET.get('week_offset', 0))
        
        # Get selected laboratory
        selected_lab = request.GET.get('laboratorio', '')
        
        # Get custom date if provided
        custom_date = request.GET.get('date', '')
        
        # Calculate week start (Monday) and end (Friday)
        if custom_date:
            try:
                selected_date = datetime.strptime(custom_date, '%Y-%m-%d').date()
                days_since_monday = selected_date.weekday()
                week_start = selected_date - timedelta(days=days_since_monday)
            except ValueError:
                today = timezone.now().date()
                days_since_monday = today.weekday()
                week_start = today - timedelta(days=days_since_monday) + timedelta(weeks=week_offset)
        else:
            today = timezone.now().date()
            days_since_monday = today.weekday()  # 0 = Monday, 6 = Sunday
            week_start = today - timedelta(days=days_since_monday) + timedelta(weeks=week_offset)
        
        week_end = week_start + timedelta(days=4)  # Friday
        
        # Generate time slots in compact format (7:00-8:00, 8:00-9:00, etc.)
        time_slots = []
        for hour in range(7, 21):  # 7 AM to 9 PM (last slot is 20:00-21:00)
            time_slots.append({
                'start': f"{hour:02d}:00",
                'end': f"{hour+1:02d}:00",
                'display': f"{hour:02d}:00 - {hour+1:02d}:00",
                'hour': hour
            })
        
        # Get all laboratories
        laboratorios = Laboratorio.objects.all().order_by('nombre')
        
        # Build query for reservations using datetime range to fix timezone
        week_start_dt = timezone.make_aware(datetime.combine(week_start, time.min))
        week_end_dt = timezone.make_aware(datetime.combine(week_end, time.max))
        
        reservas_query = ReservaClase.objects.filter(
            fecha_hora_inicio__gte=week_start_dt,
            fecha_hora_inicio__lte=week_end_dt
        ).select_related('laboratorio', 'serie')
        
        # Filter by laboratory if selected
        if selected_lab:
            reservas_query = reservas_query.filter(laboratorio_id=selected_lab)
        
        reservas = reservas_query.order_by('fecha_hora_inicio')
        
        # Build days structure
        days = []
        day_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        
        for i in range(5):  # Monday to Friday
            day_date = week_start + timedelta(days=i)
            day_reservations = defaultdict(list)
            
            # Get reservations for this day
            day_reservas = [r for r in reservas if r.fecha_hora_inicio.date() == day_date]
            
            # Organize reservations by hour slot
            for reserva in day_reservas:
                # Get the hour of the reservation start time (in local time)
                start_hour = reserva.fecha_hora_inicio.astimezone().hour
                end_hour = reserva.fecha_hora_fin.astimezone().hour
                
                # Add reservation to all hour slots it spans
                for hour in range(start_hour, end_hour):
                    slot_key = f"{hour:02d}:00 - {hour+1:02d}:00"
                    # Only add once per hour slot
                    if reserva not in day_reservations[slot_key]:
                        day_reservations[slot_key].append(reserva)
            
            days.append({
                'date': day_date,
                'name': day_names[i],
                'reservations_by_slot': dict(day_reservations)
            })
        
        # Get today's date for the date picker default
        today_str = timezone.now().date().isoformat()
        
        context = {
            'title': 'Calendario Semanal de Reservas',
            'week_start': week_start,
            'week_end': week_end,
            'week_offset': week_offset,
            'days': days,
            'time_slots': time_slots,
            'laboratorios': laboratorios,
            'selected_lab': selected_lab,
            'today_str': today_str,
            'custom_date': custom_date or today_str,
            'site_header': 'Administración de Edificio 55',
            'site_title': 'Edificio 55',
        }
        
        return render(request, 'admin/gestion/reservaclase/calendario_semanal.html', context)

class ReservaClaseInline(admin.TabularInline):
    model = ReservaClase
    extra = 0
    fields = ('fecha_hora_inicio', 'fecha_hora_fin', 'profesor', 'materia')
    readonly_fields = ('fecha_hora_inicio', 'fecha_hora_fin', 'profesor', 'materia')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

class SerieReservaAdmin(admin.ModelAdmin):
    form = SerieReservaAdminForm  # Usar formulario personalizado con dropdown de carreras
    
    list_display = ('nombre', 'laboratorio', 'profesor', 'materia', 'fecha_inicio', 'fecha_fin', 'get_dias_display', 'get_horario', 'get_ocurrencias_count', 'activa')
    list_filter = ('laboratorio', 'profesor', 'activa', 'fecha_inicio')
    search_fields = ('nombre', 'profesor', 'materia', 'laboratorio__nombre')
    ordering = ('-creada_el',)
    date_hierarchy = 'fecha_inicio'
    actions = ['regenerar_reservas', 'eliminar_reservas_existentes', 'actualizar_colores_reservas']
    inlines = [ReservaClaseInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'laboratorio', 'profesor', 'materia', 'color', 'carrera', 'semestre', 'numero_alumnos')
        }),
        ('Horarios y Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin', 'hora_inicio', 'hora_fin')
        }),
        ('Días de la Semana', {
            'fields': ('dias_semana',),
            'description': 'Selecciona los días de la semana (puedes elegir múltiples días)'
        }),
        ('Estado', {
            'fields': ('activa',)
        }),
    )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Ordenar laboratorios alfabéticamente"""
        if db_field.name == "laboratorio":
            kwargs["queryset"] = Laboratorio.objects.all().order_by('nombre')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Use color picker widget for color field"""
        if db_field.name == 'color':
            kwargs['widget'] = ColorPickerWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Personaliza el queryset para ordenar los días de la semana correctamente"""
        if db_field.name == 'dias_semana':
            # Mapeo de orden: Domingo=0, Lunes=1, Martes=2, Miércoles=3, Jueves=4, Viernes=5, Sábado=6
            from .models import DiaSemana
            from django.db.models import Case, When, IntegerField
            
            orden_dias = {'D': 0, 'L': 1, 'M': 2, 'X': 3, 'J': 4, 'V': 5, 'S': 6}
            
            # Crear un queryset ordenado usando Case/When
            when_conditions = [When(codigo=codigo, then=orden) for codigo, orden in orden_dias.items()]
            kwargs['queryset'] = DiaSemana.objects.annotate(
                orden_dia=Case(*when_conditions, default=99, output_field=IntegerField())
            ).order_by('orden_dia')
        
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    
    def get_dias_display(self, obj):
        return obj.get_dias_display()
    get_dias_display.short_description = 'Días'
    
    def get_horario(self, obj):
        return f"{obj.hora_inicio.strftime('%H:%M')} - {obj.hora_fin.strftime('%H:%M')}"
    get_horario.short_description = 'Horario'
    
    def get_ocurrencias_count(self, obj):
        return obj.ocurrencias.count()
    get_ocurrencias_count.short_description = 'Reservas Programadas'
    
    def regenerar_reservas(self, request, queryset):
        """Acción para regenerar las reservas de las series seleccionadas"""
        total_reservas_creadas = 0
        for serie in queryset:
            if serie.activa and serie.dias_semana.exists():
                self.crear_reservas_recurrentes(serie)
                total_reservas_creadas += serie.ocurrencias.count()
        else:
                self.message_user(request, f"⚠️ La serie '{serie.nombre}' está inactiva o no tiene días seleccionados.", level='WARNING')
        
        self.message_user(request, f"✅ Se regeneraron las reservas para {queryset.count()} serie(s). Total de reservas: {total_reservas_creadas}")
    regenerar_reservas.short_description = "Regenerar reservas para las series seleccionadas"
    
    def eliminar_reservas_existentes(self, request, queryset):
        """Acción para eliminar todas las reservas existentes de las series seleccionadas"""
        total_eliminadas = 0
        for serie in queryset:
            eliminadas = serie.ocurrencias.count()
            serie.ocurrencias.all().delete()
            total_eliminadas += eliminadas
        
        self.message_user(request, f"Se eliminaron {total_eliminadas} reservas de {queryset.count()} serie(s).")
    eliminar_reservas_existentes.short_description = "Eliminar reservas existentes de las series seleccionadas"
    
    def actualizar_colores_reservas(self, request, queryset):
        """Acción para actualizar los colores de las reservas existentes con el color de su serie"""
        total_actualizadas = 0
        for serie in queryset:
            # Actualizar todas las reservas de esta serie con el color de la serie
            actualizadas = serie.ocurrencias.update(color=serie.color)
            total_actualizadas += actualizadas
        
        self.message_user(request, f"✅ Se actualizaron {total_actualizadas} reservas con los colores de {queryset.count()} serie(s).")
    actualizar_colores_reservas.short_description = "Actualizar colores de reservas con el color de la serie"
    
    def save_model(self, request, obj, form, change):
        """Sobrescribe el método save para crear automáticamente las reservas recurrentes"""
        super().save_model(request, obj, form, change)
        
    def save_related(self, request, form, formsets, change):
        """Sobrescribe el método save_related para crear reservas después de guardar las relaciones"""
        super().save_related(request, form, formsets, change)
        
        # Crear reservas después de que se hayan guardado los días de la semana
        obj = form.instance
        if obj.activa and obj.dias_semana.exists():
            self.crear_reservas_recurrentes(obj)
    
    def crear_reservas_recurrentes(self, serie):
        """Crea las reservas individuales basadas en la serie"""
        from datetime import datetime, timedelta, date, time
        from django.utils import timezone
        
        # Mapeo de días de la semana
        dias_map = {
            'L': 0, 'M': 1, 'X': 2, 'J': 3, 'V': 4, 'S': 5, 'D': 6
        }
        
        # Obtener los días de la semana como números
        dias_codigos = serie.get_dias_codigos()
        dias_numeros = [dias_map[d] for d in dias_codigos]
        
        # Contadores para estadísticas
        reservas_creadas = 0
        reservas_existentes = 0
        
        # Fecha actual
        fecha_actual = serie.fecha_inicio
        
        # Crear reservas para cada día en el rango de fechas
        while fecha_actual <= serie.fecha_fin:
            # Si el día de la semana está en la lista de días de la serie
            if fecha_actual.weekday() in dias_numeros:
                # Crear datetime combinando fecha y hora
                fecha_hora_inicio = timezone.make_aware(
                    datetime.combine(fecha_actual, serie.hora_inicio)
                )
                fecha_hora_fin = timezone.make_aware(
                    datetime.combine(fecha_actual, serie.hora_fin)
                )
                
                # Verificar si ya existe una reserva para este horario
                reserva_existente = ReservaClase.objects.filter(
                    laboratorio=serie.laboratorio,
                    fecha_hora_inicio=fecha_hora_inicio,
                    fecha_hora_fin=fecha_hora_fin,
                    serie=serie
                ).exists()
                
                # Solo crear si no existe
                if not reserva_existente:
                    ReservaClase.objects.create(
                        serie=serie,
                        laboratorio=serie.laboratorio,
                        profesor=serie.profesor,
                        materia=serie.materia,
                        fecha_hora_inicio=fecha_hora_inicio,
                        fecha_hora_fin=fecha_hora_fin,
                        color=serie.color,  # Heredar el color de la serie
                        carrera=serie.carrera,  # Heredar carrera
                        semestre=serie.semestre,  # Heredar semestre
                        numero_alumnos=serie.numero_alumnos  # Heredar número de alumnos
                    )
                    reservas_creadas += 1
                else:
                    reservas_existentes += 1
            
            # Avanzar al siguiente día
            fecha_actual += timedelta(days=1)
        
        # Mostrar mensaje informativo
        if reservas_creadas > 0:
            print(f"✅ Se crearon {reservas_creadas} nuevas reservas para la serie '{serie.nombre}'")
        if reservas_existentes > 0:
            print(f"ℹ️ {reservas_existentes} reservas ya existían y no se duplicaron")

class DiaSemanaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo')
    
    def get_queryset(self, request):
        """Ordena los días de la semana: Domingo, Lunes, Martes, etc."""
        from django.db.models import Case, When, IntegerField
        orden_dias = {'D': 0, 'L': 1, 'M': 2, 'X': 3, 'J': 4, 'V': 5, 'S': 6}
        when_conditions = [When(codigo=codigo, then=orden) for codigo, orden in orden_dias.items()]
        return super().get_queryset(request).annotate(
            orden_dia=Case(*when_conditions, default=99, output_field=IntegerField())
        ).order_by('orden_dia')

# --- Registramos todos los modelos con sus clases personalizadas ---
admin.site.register(Laboratorio, LaboratorioAdmin)
admin.site.register(Software, SoftwareAdmin)
admin.site.register(PC, PCAdmin)
admin.site.register(Estudiante, EstudianteAdmin)
admin.site.register(ReservaClase, ReservaClaseAdmin)
admin.site.register(Visita, VisitaAdmin)
admin.site.register(SerieReserva, SerieReservaAdmin)
admin.site.register(DiaSemana, DiaSemanaAdmin)
admin.site.register(Mantenimiento, MantenimientoAdmin)


# --- Admin para Sesiones Activas (Turno Vespertino) ---
class SesionActivaAdmin(admin.ModelAdmin):
    """
    Admin para mostrar solo las sesiones activas (sin fecha_hora_fin).
    Diseñado para el turno vespertino.
    """
    list_display = ('get_estudiante', 'get_id_estudiante', 'get_pc', 'get_laboratorio', 'software_utilizado', 'fecha_hora_inicio', 'get_tiempo_transcurrido', 'acciones')
    list_filter = ('pc__laboratorio', 'fecha_hora_inicio')
    search_fields = ('estudiante__nombre_completo', 'estudiante__id', 'pc__numero_pc')
    ordering = ('-fecha_hora_inicio',)
    
    # Sobrescribir permisos para usar los de 'visita' en lugar de 'sesionactiva'
    def has_module_permission(self, request):
        """Permite ver el módulo si tiene permisos de visita"""
        return request.user.has_perm('gestion.view_visita')
    
    def has_view_permission(self, request, obj=None):
        """Permite ver si tiene permiso de view_visita"""
        return request.user.has_perm('gestion.view_visita')
    
    def has_add_permission(self, request):
        """No permitir agregar sesiones desde aquí"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar directamente"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Permitir 'eliminar' (finalizar) si tiene permiso de delete_visita"""
        return request.user.has_perm('gestion.delete_visita')
    
    def get_queryset(self, request):
        """Mostrar solo sesiones activas (sin fecha_hora_fin)"""
        qs = super().get_queryset(request)
        return qs.filter(fecha_hora_fin__isnull=True)
    
    def get_estudiante(self, obj):
        return obj.estudiante.nombre_completo
    get_estudiante.short_description = 'Estudiante'
    
    def get_id_estudiante(self, obj):
        return obj.estudiante.id
    get_id_estudiante.short_description = 'ID Estudiante'
    
    def get_pc(self, obj):
        return obj.pc
    get_pc.short_description = 'PC'
    
    def get_laboratorio(self, obj):
        return obj.pc.laboratorio.nombre
    get_laboratorio.short_description = 'Laboratorio'
    get_laboratorio.admin_order_field = 'pc__laboratorio__nombre'
    
    def get_tiempo_transcurrido(self, obj):
        """Calcula el tiempo transcurrido desde el inicio"""
        from django.utils import timezone
        tiempo = timezone.now() - obj.fecha_hora_inicio
        horas = int(tiempo.total_seconds() // 3600)
        minutos = int((tiempo.total_seconds() % 3600) // 60)
        return f'{horas}h {minutos}m'
    get_tiempo_transcurrido.short_description = 'Tiempo Transcurrido'
    
    def acciones(self, obj):
        """Botón para finalizar sesión"""
        finalizar_url = reverse('admin:finalizar_sesion', args=[obj.pk])
        return format_html(
            '<a class="button" href="{}" style="background-color: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Finalizar Sesión</a>',
            finalizar_url
        )
    acciones.short_description = 'Acciones'
    
    def get_urls(self):
        """Agregar URL personalizada para finalizar sesión"""
        urls = super().get_urls()
        custom_urls = [
            path('finalizar-sesion/<int:sesion_id>/', self.admin_site.admin_view(self.finalizar_sesion_view), name='finalizar_sesion'),
        ]
        return custom_urls + urls
    
    def finalizar_sesion_view(self, request, sesion_id):
        """Vista para finalizar una sesión activa"""
        from django.utils import timezone
        
        try:
            sesion = Visita.objects.get(id=sesion_id, fecha_hora_fin__isnull=True)
            
            # Finalizar la sesión
            sesion.fecha_hora_fin = timezone.now()
            sesion.save()
            
            # Liberar la PC
            if sesion.pc.estado == 'En Uso':
                sesion.pc.estado = 'Disponible'
                sesion.pc.save()
            
            messages.success(request, f'✅ Sesión de {sesion.estudiante.nombre_completo} en {sesion.pc} finalizada correctamente')
            
        except Visita.DoesNotExist:
            messages.error(request, 'Sesión no encontrada o ya finalizada')
        
        return redirect('admin:gestion_sesionactiva_changelist')


# --- Admin para Calendario Semanal (Acceso Directo) ---
class CalendarioSemanalAdmin(admin.ModelAdmin):
    """
    Admin que redirige directamente al calendario semanal.
    Aparece como una sección independiente en el menú lateral.
    """
    
    class Media:
        css = {
            'all': ('admin/css/calendario_icon.css',)
        }
    
    def has_module_permission(self, request):
        """Mostrar en el menú si tiene permisos para ver reservas"""
        return request.user.has_perm('gestion.view_reservaclase')
    
    def changelist_view(self, request, extra_context=None):
        """Redirigir directamente al calendario semanal"""
        return redirect('admin:gestion_reservaclase_calendario')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(SesionActiva, SesionActivaAdmin)
admin.site.register(CalendarioSemanal, CalendarioSemanalAdmin)