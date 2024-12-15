import json
from django.core.management.base import BaseCommand


class ImportDataCommand(BaseCommand):
    """Базовый класс для импорта данных."""
    help = ''
    model = None
    json_file_path = ''
    fields = ()

    def handle(self, *args, **kwargs):
        try:
            if not self.model or not self.json_file_path or not self.fields:
                raise ValueError(
                    'Необходимо определить model, json_file_path и fields.'
                )
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            objects = [
                self.model(**{field: item[field] for field in self.fields})
                for item in data
            ]
            self.model.objects.bulk_create(objects, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(
                f'{self.model._meta.verbose_name_plural.capitalize()} '
                'успешно импортированы.'
            ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ошибка: {e}'))
