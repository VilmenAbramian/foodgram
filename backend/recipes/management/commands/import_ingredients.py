from recipes.models import Ingredient
from .base import ImportDataCommand


class Command(ImportDataCommand):
    help = 'Импортирует ингредиенты из data/ingredients.json'
    model = Ingredient
    json_file_path = 'data/ingredients.json'
