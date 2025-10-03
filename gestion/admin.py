from django.contrib import admin
from .models import Laboratorio, Software, PC, Estudiante, ReservaClase, Visita

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
    list_display = ('__str__', 'laboratorio', 'estado')

    # Panel de filtro a la derecha
    list_filter = ('laboratorio', 'estado')

    # Orden por defecto: primero por laboratorio, luego por número de PC
    ordering = ('laboratorio', 'numero_pc')

    # Opcional: añade una barra de búsqueda
    search_fields = ('numero_pc',)

class LaboratorioAdmin(admin.ModelAdmin):
    inlines = [SoftwareInline, PCInline]
    list_display = ('nombre', 'descripcion')

class ReservaClaseAdmin(admin.ModelAdmin):
    list_display = ('laboratorio', 'materia', 'profesor', 'fecha_hora_inicio', 'fecha_hora_fin')
    list_filter = ('laboratorio', 'fecha_hora_inicio')
    search_fields = ('materia', 'profesor')

# --- NUEVA CLASE PARA ADMINISTRAR LAS VISITAS ---
class VisitaAdmin(admin.ModelAdmin):
    # Muestra estas columnas en la lista. Podemos "navegar" a modelos relacionados.
    list_display = ('estudiante', 'get_pc', 'get_laboratorio', 'fecha_hora_inicio', 'fecha_hora_fin')

    # Añade un filtro a la derecha por fecha y por laboratorio (a través de la PC).
    list_filter = ('fecha_hora_inicio', 'pc__laboratorio')

    # Añade una barra de búsqueda que buscará por ID/nombre de estudiante o por número de PC.
    search_fields = ('estudiante__id', 'estudiante__nombre_completo', 'pc__numero_pc')

    # Funciones para obtener el nombre de la PC y el Laboratorio en la lista
    def get_pc(self, obj):
        return str(obj.pc)
    get_pc.short_description = 'PC' # Nombre de la columna

    def get_laboratorio(self, obj):
        return obj.pc.laboratorio.nombre
    get_laboratorio.short_description = 'Laboratorio' # Nombre de la columna


# --- Registramos todos los modelos con sus clases personalizadas ---
admin.site.register(Laboratorio, LaboratorioAdmin)
admin.site.register(Software, SoftwareAdmin)
admin.site.register(PC, PCAdmin)
admin.site.register(Estudiante)
admin.site.register(ReservaClase, ReservaClaseAdmin)
admin.site.register(Visita, VisitaAdmin) # <-- Registramos Visita con su nueva clase personalizada