"""
Management command para poblar la base de datos con las carreras iniciales.
Uso: python manage.py seed_carreras
"""
from django.core.management.base import BaseCommand
from gestion.models import Carrera
from gestion.forms import CARRERAS_CHOICES


class Command(BaseCommand):
    help = 'Crea las carreras iniciales en la base de datos'

    def handle(self, *args, **options):
        count = 0
        for valor, _ in CARRERAS_CHOICES:
            if valor:
                _, created = Carrera.objects.get_or_create(nombre=valor)
                if created:
                    count += 1
        self.stdout.write(
            self.style.SUCCESS(
                f'Carreras creadas: {count}. Total en BD: {Carrera.objects.count()}'
            )
        )
