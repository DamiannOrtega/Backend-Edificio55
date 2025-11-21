# gestion/forms.py
from django import forms
from .models import Laboratorio, PC, Mantenimiento
from django.utils import timezone

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
    laboratorio = forms.ModelChoiceField(
        queryset=Laboratorio.objects.all().order_by('nombre'),
        label="Laboratorio",
        required=True,
        empty_label="Seleccione un laboratorio",
        help_text="Seleccione primero el laboratorio para ver las PCs disponibles"
    )
    
    class Meta:
        model = Mantenimiento
        fields = ['pc', 'descripcion', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'pc': forms.Select(attrs={'id': 'id_pc'}),
            'descripcion': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ingrese los detalles del mantenimiento...'}),
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local', 'required': True}),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'pc': 'PC',
            'descripcion': 'Descripción',
            'fecha_inicio': 'Fecha y Hora de Inicio',
            'fecha_fin': 'Fecha y Hora de Fin (opcional)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si es una edición, establecer el laboratorio inicial
        if self.instance and self.instance.pk:
            self.fields['laboratorio'].initial = self.instance.pc.laboratorio
            self.fields['pc'].queryset = PC.objects.filter(laboratorio=self.instance.pc.laboratorio).order_by('numero_pc')
        else:
            # Si es nuevo, no mostrar PCs hasta que se seleccione un laboratorio
            self.fields['pc'].queryset = PC.objects.none()
            # Establecer fecha_inicio por defecto si no está establecida
            if not self.initial.get('fecha_inicio'):
                from django.utils import timezone
                now = timezone.now()
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