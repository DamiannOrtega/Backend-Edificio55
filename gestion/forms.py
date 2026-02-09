# gestion/forms.py
from django import forms
from .models import Laboratorio, PC, Mantenimiento, Estudiante, SerieReserva
from django.utils import timezone

# Lista de carreras de la UAA
CARRERAS_CHOICES = [
    ('', '-- Selecciona una carrera --'),
    ('Arquitectura', 'Arquitectura'),
    ('Contador Público', 'Contador Público'),
    ('Ing. Automotriz', 'Ing. Automotriz'),
    ('Ing. Biomédica', 'Ing. Biomédica'),
    ('Ing. Bioquímica', 'Ing. Bioquímica'),
    ('Ing. Civil', 'Ing. Civil'),
    ('Ing. Agronomía', 'Ing. Agronomía'),
    ('Ing. en Alimentos', 'Ing. en Alimentos'),
    ('Ing. en Computación Inteligente', 'Ing. en Computación Inteligente'),
    ('Ing. en Diseño Mecánico', 'Ing. en Diseño Mecánico'),
    ('Ing. en Electrónica', 'Ing. en Electrónica'),
    ('Ing. en Energías Renovables', 'Ing. en Energías Renovables'),
    ('Ing. en Manufactura y Automatización Industrial', 'Ing. en Manufactura y Automatización Industrial'),
    ('Ing. en Robótica', 'Ing. en Robótica'),
    ('Ing. en Sistemas Computacionales', 'Ing. en Sistemas Computacionales'),
    ('Ing. Industrial Estadístico', 'Ing. Industrial Estadístico'),
    ('Lic. en Actuación', 'Lic. en Actuación'),
    ('Lic. en Administración de Empresas', 'Lic. en Administración de Empresas'),
    ('Lic. en Administración de la Producción y Servicios', 'Lic. en Administración de la Producción y Servicios'),
    ('Lic. en Administración Financiera', 'Lic. en Administración Financiera'),
    ('Lic. en Administración y Gestión Fiscal de PYMES', 'Lic. en Administración y Gestión Fiscal de PYMES'),
    ('Lic. en Agronegocios', 'Lic. en Agronegocios'),
    ('Lic. en Artes Cinematográficas y Audiovisuales', 'Lic. en Artes Cinematográficas y Audiovisuales'),
    ('Lic. en Asesoría Psicopedagógica', 'Lic. en Asesoría Psicopedagógica'),
    ('Lic. en Biología', 'Lic. en Biología'),
    ('Lic. en Biotecnología', 'Lic. en Biotecnología'),
    ('Lic. en Ciencias Políticas y Administración Pública', 'Lic. en Ciencias Políticas y Administración Pública'),
    ('Lic. en Comercio Electrónico', 'Lic. en Comercio Electrónico'),
    ('Lic. en Comercio Internacional', 'Lic. en Comercio Internacional'),
    ('Lic. en Comunicación e Información', 'Lic. en Comunicación e Información'),
    ('Lic. en Comunicación Corporativa Estratégica', 'Lic. en Comunicación Corporativa Estratégica'),
    ('Lic. en Cultura Física y Deporte', 'Lic. en Cultura Física y Deporte'),
    ('Lic. en Derecho', 'Lic. en Derecho'),
    ('Lic. en Desarrollo de Videojuegos y Entornos Virtuales (modalidad virtual)', 'Lic. en Desarrollo de Videojuegos y Entornos Virtuales (modalidad virtual)'),
    ('Lic. en Diseño de Interiores', 'Lic. en Diseño de Interiores'),
    ('Lic. en Diseño de Modas en Indumentaria y Textiles', 'Lic. en Diseño de Modas en Indumentaria y Textiles'),
    ('Lic. en Diseño Gráfico', 'Lic. en Diseño Gráfico'),
    ('Lic. en Diseño Industrial', 'Lic. en Diseño Industrial'),
    ('Lic. en Docencia de Francés y Español como Lenguas Extranjeras', 'Lic. en Docencia de Francés y Español como Lenguas Extranjeras'),
    ('Lic. en Docencia del Idioma Inglés', 'Lic. en Docencia del Idioma Inglés'),
    ('Lic. en Economía', 'Lic. en Economía'),
    ('Lic. en Enfermería', 'Lic. en Enfermería'),
    ('Lic. en Estudios del Arte y Gestión Cultural', 'Lic. en Estudios del Arte y Gestión Cultural'),
    ('Lic. en Filosofía', 'Lic. en Filosofía'),
    ('Lic. en Gestión Turística', 'Lic. en Gestión Turística'),
    ('Lic. en Historia', 'Lic. en Historia'),
    ('Lic. en Informática y Tecnologías Computacionales', 'Lic. en Informática y Tecnologías Computacionales'),
    ('Lic. en Letras Hispánicas', 'Lic. en Letras Hispánicas'),
    ('Lic. en Logística Empresarial', 'Lic. en Logística Empresarial'),
    ('Lic. en Matemáticas Aplicadas', 'Lic. en Matemáticas Aplicadas'),
    ('Lic. en Mercadotecnia', 'Lic. en Mercadotecnia'),
    ('Lic. en Música', 'Lic. en Música'),
    ('Lic. en Nutrición', 'Lic. en Nutrición'),
    ('Lic. en Optometría', 'Lic. en Optometría'),
    ('Lic. en Psicología', 'Lic. en Psicología'),
    ('Lic. en Relaciones Industriales', 'Lic. en Relaciones Industriales'),
    ('Lic. en Sociología', 'Lic. en Sociología'),
    ('Lic. en Terapia Física', 'Lic. en Terapia Física'),
    ('Lic. en Trabajo Social', 'Lic. en Trabajo Social'),
    ('Lic. en Urbanismo', 'Lic. en Urbanismo'),
    ('Médico Cirujano', 'Médico Cirujano'),
    ('Médico Estomatólogo', 'Médico Estomatólogo'),
    ('Médico Veterinario Zootecnista', 'Médico Veterinario Zootecnista'),
    ('Químico Farmacéutico Biólogo', 'Químico Farmacéutico Biólogo'),
]

class EstudianteAdminForm(forms.ModelForm):
    """Formulario personalizado para el admin de Estudiante con dropdown de carreras"""
    
    carrera = forms.ChoiceField(
        choices=CARRERAS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'vTextField'}),
        label='Carrera'
    )
    
    class Meta:
        model = Estudiante
        fields = '__all__'


class SerieReservaAdminForm(forms.ModelForm):
    """Formulario personalizado para el admin de SerieReserva con dropdown de carreras"""
    
    carrera = forms.ChoiceField(
        choices=CARRERAS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'vTextField'}),
        label='Carrera'
    )
    
    class Meta:
        model = SerieReserva
        fields = '__all__'



class RecurrenciaForm(forms.Form):
    DIAS_SEMANA = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    laboratorio = forms.ModelChoiceField(
        queryset=Laboratorio.objects.all().order_by('nombre'),
        label="Laboratorio a reservar"
    )
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha de inicio del período"
    )
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha de fin del período"
    )
    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="Hora de inicio de la clase"
    )
    hora_fin = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="Hora de fin de la clase"
    )
    dias = forms.MultipleChoiceField(
        choices=DIAS_SEMANA,
        widget=forms.CheckboxSelectMultiple,
        label="Días de la semana en que se repite"
    )
    materia = forms.CharField(max_length=100, required=False)
    profesor = forms.CharField(max_length=100, required=False)

class MantenimientoForm(forms.ModelForm):
    """Formulario personalizado para Mantenimiento con selector de laboratorio"""

    # Campo auxiliar para elegir laboratorio (no pertenece al modelo)
    laboratorio = forms.ModelChoiceField(
        queryset=Laboratorio.objects.all().order_by('nombre'),
        label="Laboratorio",
        required=True,
        empty_label="Seleccione un laboratorio",
        help_text="Seleccione primero el laboratorio para ver las PCs disponibles",
    )

    # Definir explícitamente los campos de fecha/hora para que NO usen SplitDateTime
    fecha_inicio = forms.DateTimeField(
        label="Fecha y Hora de Inicio",
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "required": True,
            }
        ),
        required=True,
    )

    fecha_fin = forms.DateTimeField(
        label="Fecha y Hora de Fin (opcional)",
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
            }
        ),
        required=False,
    )

    class Meta:
        model = Mantenimiento
        fields = ["pc", "descripcion", "fecha_inicio", "fecha_fin"]
        widgets = {
            "pc": forms.Select(attrs={"id": "id_pc"}),
            "descripcion": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Ingrese los detalles del mantenimiento...",
                }
            ),
        }
        labels = {
            "pc": "PC",
            "descripcion": "Descripción",
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si es una edición, establecer el laboratorio inicial
        if self.instance and self.instance.pk:
            self.fields['laboratorio'].initial = self.instance.pc.laboratorio
            self.fields['pc'].queryset = PC.objects.filter(laboratorio=self.instance.pc.laboratorio).order_by('numero_pc')
            
            # Convertir fechas existentes a zona horaria local para el widget datetime-local
            if self.instance.fecha_inicio:
                fecha_inicio_local = timezone.localtime(self.instance.fecha_inicio)
                self.initial['fecha_inicio'] = fecha_inicio_local.strftime('%Y-%m-%dT%H:%M')
            if self.instance.fecha_fin:
                fecha_fin_local = timezone.localtime(self.instance.fecha_fin)
                self.initial['fecha_fin'] = fecha_fin_local.strftime('%Y-%m-%dT%H:%M')
        else:
            # Si es nuevo, no mostrar PCs hasta que se seleccione un laboratorio
            self.fields['pc'].queryset = PC.objects.none()
            # Establecer fecha_inicio por defecto si no está establecida
            if not self.initial.get('fecha_inicio'):
                # Convertir a la zona horaria local antes de formatear
                now = timezone.localtime(timezone.now())
                # Formatear para datetime-local (YYYY-MM-DDTHH:MM)
                fecha_str = now.strftime('%Y-%m-%dT%H:%M')
                self.initial['fecha_inicio'] = fecha_str
            
            # Verificar si hay datos del formulario (POST) o parámetros GET
            laboratorio_id = None
            if self.data:
                laboratorio_id = self.data.get('laboratorio')
            elif hasattr(self, 'initial') and 'laboratorio' in self.initial:
                laboratorio_id = self.initial.get('laboratorio')
            
            if laboratorio_id:
                try:
                    laboratorio_id = int(laboratorio_id)
                    self.fields['pc'].queryset = PC.objects.filter(laboratorio_id=laboratorio_id).order_by('numero_pc')
                except (ValueError, TypeError):
                    pass
    
    def clean_fecha_inicio(self):
        """Asegurar que la fecha_inicio se interprete como hora local"""
        fecha_inicio = self.cleaned_data.get('fecha_inicio')
        if fecha_inicio:
            # Si el datetime es naive (sin zona horaria), asumir que es hora local
            # Esto es lo que envía el widget datetime-local
            if timezone.is_naive(fecha_inicio):
                # Convertir a zona horaria local (datetime-local siempre envía hora local)
                fecha_inicio = timezone.make_aware(fecha_inicio, timezone.get_current_timezone())
            # Si ya es aware, mantenerlo así (ya está en la zona horaria correcta)
        return fecha_inicio
    
    def clean_fecha_fin(self):
        """Asegurar que la fecha_fin se interprete como hora local"""
        fecha_fin = self.cleaned_data.get('fecha_fin')
        if fecha_fin:
            # Si el datetime es naive (sin zona horaria), asumir que es hora local
            # Esto es lo que envía el widget datetime-local
            if timezone.is_naive(fecha_fin):
                # Convertir a zona horaria local (datetime-local siempre envía hora local)
                fecha_fin = timezone.make_aware(fecha_fin, timezone.get_current_timezone())
            # Si ya es aware, mantenerlo así (ya está en la zona horaria correcta)
        return fecha_fin
    
    def clean(self):
        """Validación personalizada"""
        cleaned_data = super().clean()
        pc = cleaned_data.get('pc')
        laboratorio = cleaned_data.get('laboratorio')
        
        # Validar que la PC pertenezca al laboratorio seleccionado
        if pc and laboratorio:
            if pc.laboratorio != laboratorio:
                raise forms.ValidationError({
                    'pc': 'La PC seleccionada no pertenece al laboratorio elegido.'
                })
        
        # Remover el campo laboratorio de cleaned_data ya que no es parte del modelo
        if 'laboratorio' in cleaned_data:
            del cleaned_data['laboratorio']
        
        return cleaned_data
    
    def save(self, commit=True):
        """Sobrescribe el método save para no guardar el campo laboratorio"""
        # Remover laboratorio de los datos antes de guardar
        if 'laboratorio' in self.cleaned_data:
            del self.cleaned_data['laboratorio']
        
        instance = super().save(commit=False)
        # El campo laboratorio es solo para filtrado, no se guarda
        if commit:
            instance.save()
        return instance