"""
Comando Django para finalizar todas las sesiones activas
Se ejecuta automáticamente al iniciar el sistema para limpiar sesiones pendientes
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from gestion.models import Visita, PC


class Command(BaseCommand):
    help = 'Finaliza todas las sesiones activas (sin hora de salida)'

    def handle(self, *args, **options):
        # Buscar todas las sesiones activas
        sesiones_activas = Visita.objects.filter(fecha_hora_fin__isnull=True)
        count = sesiones_activas.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('✓ No hay sesiones activas para finalizar'))
            return
        
        # Finalizar todas las sesiones
        hora_actual = timezone.now()
        pcs_liberadas = []
        
        for sesion in sesiones_activas:
            sesion.fecha_hora_fin = hora_actual
            sesion.save()
            
            # Liberar la PC (cambiar estado a Disponible si estaba En Uso)
            if sesion.pc and sesion.pc.estado == 'En Uso':
                sesion.pc.estado = 'Disponible'
                sesion.pc.save()
                pcs_liberadas.append(str(sesion.pc))
        
        # Mostrar resumen
        self.stdout.write(self.style.SUCCESS(f'✓ {count} sesión(es) finalizada(s) correctamente'))
        if pcs_liberadas:
            self.stdout.write(self.style.SUCCESS(f'✓ {len(pcs_liberadas)} PC(s) liberada(s): {", ".join(pcs_liberadas)}'))
