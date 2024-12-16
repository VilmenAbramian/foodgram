from datetime import date


HEADER_TEMPLATE = "Список покупок от {date}"
PRODUCT_TEMPLATE = "{index}) {name} - {amount} {unit}"
RECIPE_TEMPLATE = "{index}) {name}"


def shopping_cart(filling_basket):
    header = HEADER_TEMPLATE.format(date=date.today().strftime('%d.%m.%Y'))
    products = [
        PRODUCT_TEMPLATE.format(
            index=index,
            name=ingredient["ingredient__name"].capitalize(),
            amount=ingredient["total_amount"],
            unit=ingredient["ingredient__measurement_unit"]
        )
        for index, ingredient in enumerate(filling_basket, start=1)
    ]
    recipes = [
        RECIPE_TEMPLATE.format(index=i, name=recipe)
        for i, recipe in enumerate(
            {ingredient['recipe__name'] for
             ingredient in filling_basket}, start=1
        )
    ]
    return '\n'.join([
        header,
        'Список ингредиентов:',
        *products,
        'Список рецептов:',
        *recipes,
    ])
