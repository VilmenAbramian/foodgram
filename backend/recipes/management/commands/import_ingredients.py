import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из data/ingredients.json'

    def handle(self, *args, **kwargs):
        try:
            with open('data/ingredients.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            ingredients = [
                Ingredient(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                ) for item in data
            ]
            Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)

            self.stdout.write(self.style.SUCCESS(
                'Ингредиенты успешно импортированы.'
            ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ошибка: {e}'))
