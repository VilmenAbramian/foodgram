import json

from django.core.management.base import BaseCommand


class ImportDataCommand(BaseCommand):
    """Базовый класс для импорта данных."""
    help = ''
    model = None
    json_file_path = ''

    def handle(self, *args, **kwargs):
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            objects = [
                self.model(**item)
                for item in data
            ]
            self.model.objects.bulk_create(objects, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(
                f'{self.model._meta.verbose_name_plural} '
                'успешно импортированы. '
                f'Добавлено: {len(objects)}.'
            ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                'Ошибка при импорте данных в модель '
                f'"{self.model._meta.object_name}" '
                f'из файла "{self.json_file_path}": {e}'
            ))
