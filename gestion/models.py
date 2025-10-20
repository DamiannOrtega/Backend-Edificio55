from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta

# Modelo para la tabla Laboratorios
class Laboratorio(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True) # blank=True y null=True hacen que no sea obligatorio
    def __str__(self):
        return self.nombre

# Modelo para la tabla Software
class Software(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    version = models.CharField(max_length=50, blank=True, null=True)
    # Aquí es donde definimos la relación muchos-a-muchos.
    # Un software puede estar en muchos laboratorios.
    laboratorios = models.ManyToManyField(Laboratorio, related_name='software_instalado')

    def __str__(self):
        return self.nombre

# Modelo para la tabla PCs
class PC(models.Model):
    ESTADO_CHOICES = [
        ('Disponible', 'Disponible'),
        ('En Uso', 'En Uso'),
        ('Mantenimiento', 'Mantenimiento'),
        ('Reservada', 'Reservada'),
    ]
    numero_pc = models.IntegerField()
    # Relación uno-a-muchos: Una PC pertenece a UN solo laboratorio.
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Disponible')

    def __str__(self):
        # Tomamos el último caracter del nombre del lab (ej: 'A' de 'Laboratorio A')
        # y lo unimos con el número de la PC.
        letra_lab = self.laboratorio.nombre[-1]
        return f'{letra_lab}{self.numero_pc}'
    
    def esta_disponible_para_uso(self):
        """Verifica si la PC está disponible para uso individual (no períodos de clase)"""
        from django.utils import timezone
        now = timezone.now()
        
        # Si está en mantenimiento, no está disponible
        if self.estado == 'Mantenimiento':
            return False
            
        # Si está en uso individual, no está disponible
        if self.estado == 'En Uso':
            return False
            
        # Verificar si hay una reserva activa en este laboratorio
        reserva_activa = ReservaClase.objects.filter(
            laboratorio=self.laboratorio,
            fecha_hora_inicio__lte=now,
            fecha_hora_fin__gte=now
        ).exists()
        
        # Si hay reserva activa, no está disponible para uso individual
        if reserva_activa:
            return False
            
        return True

# Modelo para la tabla Estudiantes
class Estudiante(models.Model):
    # Usamos CharField para el ID porque puede que no sea solo un número (ej. 'A012345')
    id = models.CharField(max_length=20, primary_key=True)
    nombre_completo = models.CharField(max_length=150)
    correo = models.EmailField(unique=True) # EmailField valida que el formato sea de correo
    celular = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.nombre_completo

class DiaSemana(models.Model):
    """Modelo para representar los días de la semana"""
    codigo = models.CharField(max_length=1, unique=True)
    nombre = models.CharField(max_length=10)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Día de la Semana"
        verbose_name_plural = "Días de la Semana"

class SerieReserva(models.Model):
    """ Representa una serie de reservas recurrentes, ej. 'Clase de Redes L-V 10-11' """
    
    nombre = models.CharField(max_length=200, help_text="Ej: Clase de Redes - Semestre Otoño 2025")
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    profesor = models.CharField(max_length=100, blank=True)
    materia = models.CharField(max_length=100, blank=True)
    
    # Fechas de inicio y fin de la serie
    fecha_inicio = models.DateField(default=timezone.now, help_text="Fecha de inicio de la serie de reservas")
    fecha_fin = models.DateField(default=timezone.now, help_text="Fecha de fin de la serie de reservas")
    
    # Horarios
    hora_inicio = models.TimeField(default='08:00', help_text="Hora de inicio (ej: 08:00)")
    hora_fin = models.TimeField(default='09:00', help_text="Hora de fin (ej: 09:00)")
    
    # Días de la semana - ahora es una relación muchos a muchos
    dias_semana = models.ManyToManyField(DiaSemana, help_text="Selecciona los días de la semana")
    
    # Campos de control
    activa = models.BooleanField(default=True, help_text="Si la serie está activa")
    creada_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Serie de Reserva"
        verbose_name_plural = "Series de Reservas"

    def __str__(self):
        return self.nombre
    
    def get_dias_display(self):
        """Retorna los días de la semana en formato legible"""
        dias = self.dias_semana.all().order_by('codigo')
        return ', '.join([dia.nombre for dia in dias])
    
    def get_dias_codigos(self):
        """Retorna los códigos de los días para el procesamiento"""
        return [dia.codigo for dia in self.dias_semana.all()]
    
# Modelo para las reservas de clases completas
class ReservaClase(models.Model):

    serie = models.ForeignKey(SerieReserva, on_delete=models.CASCADE, null=True, blank=True, related_name="ocurrencias")
    
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    profesor = models.CharField(max_length=100, blank=True, null=True)
    materia = models.CharField(max_length=100, blank=True, null=True)
    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin = models.DateTimeField()

    def __str__(self):
        return f'Reserva de {self.laboratorio.nombre} para {self.materia}'
    
    def esta_activa(self):
        """Verifica si la reserva está actualmente activa"""
        from django.utils import timezone
        now = timezone.now()
        return self.fecha_hora_inicio <= now <= self.fecha_hora_fin
    
    def actualizar_estado_pcs(self):
        """Actualiza el estado de todas las PCs del laboratorio según esta reserva"""
        pcs_laboratorio = PC.objects.filter(laboratorio=self.laboratorio)
        
        if self.esta_activa():
            # Si la reserva está activa, marcar PCs como reservadas (excepto las que están en uso individual)
            pcs_laboratorio.filter(estado='Disponible').update(estado='Reservada')
        else:
            # Si la reserva no está activa, marcar PCs como disponibles (excepto las que están en uso individual)
            pcs_laboratorio.filter(estado='Reservada').update(estado='Disponible')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Actualizar estado de PCs después de guardar
        self.actualizar_estado_pcs()
    
    def delete(self, *args, **kwargs):
        # Actualizar estado de PCs antes de eliminar
        self.actualizar_estado_pcs()
        super().delete(*args, **kwargs)

# Modelo para el historial de visitas de los alumnos
class Visita(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    pc = models.ForeignKey(PC, on_delete=models.CASCADE)
    software_utilizado = models.ForeignKey(Software, on_delete=models.SET_NULL, null=True, blank=True)
    # auto_now_add pone la fecha y hora actual automáticamente al crear el registro.
    fecha_hora_inicio = models.DateTimeField(auto_now_add=True)
    fecha_hora_fin = models.DateTimeField(null=True, blank=True) # Se llena al hacer check-out

    def __str__(self):
        return f'Visita de {self.estudiante.nombre_completo} en {self.pc}'
