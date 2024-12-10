import json

from django.core.management.base import BaseCommand
from recipes.models import Tag

class Command(BaseCommand):
    help = 'Импортирует теги из data/tags.json'

    def handle(self, *args, **kwargs):
        try:
            with open('data/tags.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            tags = [
                Tag(
                    name=item['name'],
                    slug=item['slug'],
                ) for item in data
            ]

            Tag.objects.bulk_create(tags, ignore_conflicts=True)

            self.stdout.write(self.style.SUCCESS('Теги успешно импортированы.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ошибка: {e}'))