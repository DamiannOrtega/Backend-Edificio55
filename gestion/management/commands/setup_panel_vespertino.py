"""
Management command para configurar el grupo y usuario del turno vespertino
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from gestion.models import Mantenimiento, Visita


class Command(BaseCommand):
    help = 'Configura el grupo y usuario para el turno vespertino'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== Configurando Panel Vespertino ===\n'))

        # Crear grupo "Turno Vespertino"
        grupo, created = Group.objects.get_or_create(name='Turno Vespertino')
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "Turno Vespertino" creado'))
        else:
            self.stdout.write(self.style.WARNING('→ Grupo "Turno Vespertino" ya existe'))

        # Asignar permisos específicos al grupo
        # Permisos para Mantenimiento (todos)
        mant_ct = ContentType.objects.get_for_model(Mantenimiento)
        permisos_mant = Permission.objects.filter(content_type=mant_ct)
        grupo.permissions.add(*permisos_mant)
        
        # Permisos para SesionActiva (ver y eliminar/finalizar)
        from gestion.models import SesionActiva
        sesion_ct = ContentType.objects.get_for_model(SesionActiva)
        permisos_sesion = Permission.objects.filter(content_type=sesion_ct)
        grupo.permissions.add(*permisos_sesion)
        
        self.stdout.write(self.style.SUCCESS('✓ Permisos asignados al grupo'))

        # Crear usuario admin_tarde
        username = 'admin_tarde'
        password = 'tarde2026'  # Cambiar esto en producción
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': 'Administrador',
                'last_name': 'Turno Tarde',
                'is_staff': True,  # Necesario para login
                'is_active': True,
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Usuario "{username}" creado'))
            self.stdout.write(self.style.WARNING(f'  Contraseña: {password}'))
        else:
            self.stdout.write(self.style.WARNING(f'→ Usuario "{username}" ya existe'))
        
        # Agregar usuario al grupo
        user.groups.add(grupo)
        self.stdout.write(self.style.SUCCESS(f'✓ Usuario agregado al grupo "Turno Vespertino"'))

        # Resumen
        self.stdout.write(self.style.SUCCESS('\n=== Configuración Completada ===\n'))
        self.stdout.write(self.style.SUCCESS('Credenciales de acceso:'))
        self.stdout.write(f'  URL: http://localhost:8000/panel-vespertino/login/')
        self.stdout.write(f'  Usuario: {username}')
        self.stdout.write(f'  Contraseña: {password}')
        self.stdout.write(self.style.WARNING('\n⚠️  IMPORTANTE: Cambia la contraseña en producción\n'))
