from recipes.models import Tag
from .base import ImportDataCommand


class Command(ImportDataCommand):
    help = 'Импортирует теги из data/tags.json'
    model = Tag
    json_file_path = 'data/tags.json'
