from django.core.management.base import BaseCommand

from apps.books.models import Category

CATEGORIES = [
    'Literatura Clásica',
    'Ficción',
    'No Ficción',
    'Ciencia Ficción',
    'Fantasía',
    'Misterio y Suspenso',
    'Romance',
    'Historia',
    'Biografías',
    'Ciencia y Tecnología',
    'Infantil',
    'Juvenil',
    'Autoayuda',
    'Negocios y Economía',
    'Arte y Fotografía',
    'Poesía',
    'Cocina',
    'Religión y Espiritualidad',
    'Cómics y Novela Gráfica',
    'Educación',
]


class Command(BaseCommand):
    help = 'Seed the default book categories (safe to run more than once).'

    def handle(self, *args, **options):
        created = 0
        for name in CATEGORIES:
            _, was_created = Category.objects.get_or_create(name=name)
            created += was_created
        self.stdout.write(
            self.style.SUCCESS(
                f'{created} created, {len(CATEGORIES) - created} already existed.'
            )
        )
