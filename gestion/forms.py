# gestion/forms.py
from django import forms
from .models import Laboratorio

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
        queryset=Laboratorio.objects.all(),
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