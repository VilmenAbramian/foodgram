from collections import defaultdict
from datetime import date

HEADER_TEMPLATE = "Список покупок от {date}"
PRODUCT_TEMPLATE = "{index}) {description} - {amount}"
RECIPE_TEMPLATE = "{index}) {name}"


def shopping_cart(filling_basket):
    header = HEADER_TEMPLATE.format(date=date.today().strftime('%d.%m.%Y'))
    ingredient_groups = defaultdict(lambda: 0)
    recipes = set()
    for ingredient in filling_basket:
        ingredient_key = (
            ingredient['ingredient__name'].capitalize(),
            ingredient['ingredient__measurement_unit']
        )
        ingredient_groups[ingredient_key] += ingredient['total_amount']
        recipes.add(ingredient['recipe__name'])
    sorted_ingredients = sorted(
        ingredient_groups.items(),
        key=lambda item: item[0][0]
    )
    products = [
        PRODUCT_TEMPLATE.format(
            index=index,
            description=f"{name} ({unit})",
            amount=total_amount
        )
        for index, ((name, unit), total_amount) in enumerate(
            sorted_ingredients, start=1
        )
    ]
    recipes_list = [
        RECIPE_TEMPLATE.format(index=index, name=recipe)
        for index, recipe in enumerate(sorted(recipes), start=1)
    ]
    return '\n'.join([
        header,
        'Список ингредиентов:',
        *products,
        'Список рецептов:',
        *recipes_list,
    ])
