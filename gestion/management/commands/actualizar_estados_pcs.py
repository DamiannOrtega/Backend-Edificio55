from django.core.management.base import BaseCommand
from django.utils import timezone
from gestion.models import PC, ReservaClase

class Command(BaseCommand):
    help = 'Actualiza el estado de todas las PCs basándose en las reservas activas'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Obtener todas las reservas activas
        reservas_activas = ReservaClase.objects.filter(
            fecha_hora_inicio__lte=now,
            fecha_hora_fin__gte=now
        )
        
        # Obtener laboratorios con reservas activas
        laboratorios_reservados = set(reserva.laboratorio for reserva in reservas_activas)
        
        # Marcar PCs como reservadas en laboratorios con reservas activas
        for laboratorio in laboratorios_reservados:
            pcs_actualizadas = PC.objects.filter(
                laboratorio=laboratorio,
                estado='Disponible'
            ).update(estado='Reservada')
            
            if pcs_actualizadas > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {pcs_actualizadas} PCs marcadas como Reservadas en {laboratorio.nombre}')
                )
        
        # Marcar PCs como disponibles en laboratorios sin reservas activas
        laboratorios_todos = set(PC.objects.values_list('laboratorio', flat=True).distinct())
        laboratorios_sin_reserva = laboratorios_todos - laboratorios_reservados
        
        for laboratorio_id in laboratorios_sin_reserva:
            from gestion.models import Laboratorio
            laboratorio = Laboratorio.objects.get(id=laboratorio_id)
            
            pcs_actualizadas = PC.objects.filter(
                laboratorio=laboratorio,
                estado='Reservada'
            ).update(estado='Disponible')
            
            if pcs_actualizadas > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {pcs_actualizadas} PCs marcadas como Disponibles en {laboratorio.nombre}')
                )
        
        # Mostrar resumen de reservas activas
        if reservas_activas.exists():
            self.stdout.write(self.style.WARNING('\n📋 Reservas activas:'))
            for reserva in reservas_activas:
                self.stdout.write(
                    f'  - {reserva.laboratorio.nombre}: {reserva.materia} '
                    f'({reserva.fecha_hora_inicio.strftime("%H:%M")} - {reserva.fecha_hora_fin.strftime("%H:%M")})'
                )
        else:
            self.stdout.write(self.style.SUCCESS('✅ No hay reservas activas en este momento'))
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎯 Estados de PCs actualizados correctamente a las {now.strftime("%H:%M:%S")}')
        )
