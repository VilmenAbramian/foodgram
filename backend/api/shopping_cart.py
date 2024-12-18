from collections import defaultdict
from datetime import date

HEADER_TEMPLATE = "Список покупок от {date}"
PRODUCT_TEMPLATE = "{index}) {name} - {amount} {unit}"
RECIPE_TEMPLATE = "{index}) {name}"


def shopping_cart(filling_basket):
    header = HEADER_TEMPLATE.format(date=date.today().strftime('%d.%m.%Y'))
    ingredient_groups = defaultdict(lambda: {'total_amount': 0, 'unit': ''})
    recipes = set()
    for ingredient in filling_basket:
        ingredient_name = ingredient['ingredient__name']
        ingredient_unit = ingredient['ingredient__measurement_unit']
        ingredient_groups[(ingredient_name,
                           ingredient_unit)]['total_amount'] += (
            ingredient)['total_amount']
        ingredient_groups[(ingredient_name,
                           ingredient_unit)]['unit'] = ingredient_unit
        recipes.add(ingredient['recipe__name'])
    products = [
        PRODUCT_TEMPLATE.format(
            index=index,
            name=ingredient[0][0].capitalize(),
            amount=ingredient[1]['total_amount'],
            unit=ingredient[1]['unit']
        )
        for index, ingredient in enumerate(ingredient_groups.items(), start=1)
    ]
    recipes_list = [
        RECIPE_TEMPLATE.format(index=index, name=recipe)
        for index, recipe in enumerate(recipes, start=1)
    ]
    return '\n'.join([
        header,
        'Список ингредиентов:',
        *products,
        'Список рецептов:',
        *recipes_list,
    ])
