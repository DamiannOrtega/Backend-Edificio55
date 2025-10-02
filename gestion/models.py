from django.db import models

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

# Modelo para la tabla Estudiantes
class Estudiante(models.Model):
    # Usamos CharField para el ID porque puede que no sea solo un número (ej. 'A012345')
    id = models.CharField(max_length=20, primary_key=True)
    nombre_completo = models.CharField(max_length=150)
    correo = models.EmailField(unique=True) # EmailField valida que el formato sea de correo
    celular = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.nombre_completo

# Modelo para las reservas de clases completas
class ReservaClase(models.Model):
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    profesor = models.CharField(max_length=100, blank=True, null=True)
    materia = models.CharField(max_length=100, blank=True, null=True)
    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin = models.DateTimeField()

    def __str__(self):
        return f'Reserva de {self.laboratorio.nombre} para {self.materia}'

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