from django.contrib import admin
from .models import Laboratorio, Software, PC, Estudiante, ReservaClase, Visita, SerieReserva, DiaSemana
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import RecurrenciaForm
from datetime import timedelta, datetime
from django.urls import path
from django.utils.html import format_html
from django.urls import reverse

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

class ReservaClaseInline(admin.TabularInline):
    model = ReservaClase
    extra = 0
    fields = ('fecha_hora_inicio', 'fecha_hora_fin', 'profesor', 'materia')
    readonly_fields = ('fecha_hora_inicio', 'fecha_hora_fin', 'profesor', 'materia')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

class SerieReservaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'laboratorio', 'profesor', 'materia', 'fecha_inicio', 'fecha_fin', 'get_dias_display', 'get_horario', 'get_ocurrencias_count', 'activa')
    list_filter = ('laboratorio', 'profesor', 'activa', 'fecha_inicio')
    search_fields = ('nombre', 'profesor', 'materia', 'laboratorio__nombre')
    ordering = ('-creada_el',)
    date_hierarchy = 'fecha_inicio'
    actions = ['regenerar_reservas', 'eliminar_reservas_existentes']
    inlines = [ReservaClaseInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'laboratorio', 'profesor', 'materia')
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
                        fecha_hora_fin=fecha_hora_fin
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
    ordering = ('codigo',)

# --- Registramos todos los modelos con sus clases personalizadas ---
admin.site.register(Laboratorio, LaboratorioAdmin)
admin.site.register(Software, SoftwareAdmin)
admin.site.register(PC, PCAdmin)
admin.site.register(Estudiante)
admin.site.register(ReservaClase, ReservaClaseAdmin)
admin.site.register(Visita, VisitaAdmin)
admin.site.register(SerieReserva, SerieReservaAdmin)
admin.site.register(DiaSemana, DiaSemanaAdmin)