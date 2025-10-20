from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ReservaClase, PC
from django.utils import timezone

@receiver(post_save, sender=ReservaClase)
def actualizar_estado_pcs_despues_reserva(sender, instance, created, **kwargs):
    """Actualiza el estado de las PCs cuando se crea o modifica una reserva"""
    actualizar_estados_pcs_laboratorio(instance.laboratorio)

@receiver(post_delete, sender=ReservaClase)
def actualizar_estado_pcs_despues_eliminar_reserva(sender, instance, **kwargs):
    """Actualiza el estado de las PCs cuando se elimina una reserva"""
    actualizar_estados_pcs_laboratorio(instance.laboratorio)

def actualizar_estados_pcs_laboratorio(laboratorio):
    """Actualiza el estado de todas las PCs de un laboratorio según las reservas activas"""
    now = timezone.now()
    
    # Verificar si hay reservas activas en este laboratorio
    reservas_activas = ReservaClase.objects.filter(
        laboratorio=laboratorio,
        fecha_hora_inicio__lte=now,
        fecha_hora_fin__gte=now
    ).exists()
    
    # Obtener todas las PCs del laboratorio
    pcs_laboratorio = PC.objects.filter(laboratorio=laboratorio)
    
    if reservas_activas:
        # Si hay reservas activas, marcar PCs disponibles como reservadas
        pcs_laboratorio.filter(estado='Disponible').update(estado='Reservada')
    else:
        # Si no hay reservas activas, marcar PCs reservadas como disponibles
        pcs_laboratorio.filter(estado='Reservada').update(estado='Disponible')