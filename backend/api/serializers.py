from djoser.serializers import (
    UserSerializer
)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (
    FavoriteRecipes, Ingredient,
    RecipeIngredient, Recipe,
    ShoppingList, Subscriptions,
    Tag, User
)


MIN_AMOUNT = 1


# --------------- Сериалайзер для User ---------------
class FoodgramUserSerializer(UserSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (*UserSerializer.Meta.fields, 'avatar', 'is_subscribed')

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        return (
            request is not None and not request.user.is_anonymous
            and Subscriptions.objects.filter(
                user=request.user, author=user
            ).exists()
        )


# --------------- Сериалайзеры для recipes ---------------
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = fields


class RecipeReadSerializer(serializers.ModelSerializer):
    '''
    Serializer для модели Recipe - чтение данных
    '''
    author = FoodgramUserSerializer()
    ingredients = IngredientInRecipeReadSerializer(
        many=True,
        source='recipe_ingredients',
        read_only=True
    )

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def check_user_relation(self, recipe, relation_model):
        return (not self.context.get('request').user.is_anonymous
                and relation_model.objects.filter(recipe=recipe).exists())

    def get_is_favorited(self, recipe):
        return self.check_user_relation(recipe, FavoriteRecipes)

    def get_is_in_shopping_cart(self, recipe):
        return self.check_user_relation(recipe, ShoppingList)


class AddIngredientSerializer(serializers.ModelSerializer):
    '''
    Serializer для поля ingredients в моделе Recipe
    для добавления ингредиентов в рецепт.
    '''
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=MIN_AMOUNT)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    '''
    Serializer для модели Recipe - запись, обновление, удаление данных
    '''
    image = Base64ImageField(required=True, allow_null=False)
    ingredients = AddIngredientSerializer(many=True, write_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def validate(self, serializer_data):
        image = serializer_data.get('image')
        if not image:
            raise serializers.ValidationError(
                'Поле "image" не может быть пустым!'
            )
        return serializer_data

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError(
                'В рецепте должен быть хотя бы один ингредиент!'
            )
        if len(ingredients) != len(
                {item['id'] for item in ingredients}
        ):
            raise ValidationError(
                'В рецепте не может быть повторяющихся ингредиентов!'
            )
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError('В рецепте должен быть хотя бы один тег!')
        if len(tags) != len(set(tags)):
            raise ValidationError(
                'В рецепте не может быть повторяющихся тегов!'
            )
        return tags

    def to_representation(self, recipe_obj):
        serializer = RecipeReadSerializer(recipe_obj, context=self.context)
        representation = serializer.data
        representation['ingredients'] = IngredientInRecipeReadSerializer(
            recipe_obj.recipe_ingredients.all(), many=True
        ).data
        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author'] = request.user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        self.write_data(recipe, ingredients, tags)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        self.validate_ingredients(ingredients)
        self.validate_tags(tags)
        recipe.recipe_ingredients.all().delete()
        self.write_data(recipe, ingredients, tags)
        return super().update(recipe, validated_data)

    def write_data(self, recipe, ingredients, tags):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        )
        recipe.tags.set(tags)


class RecipeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializerFoodgram(FoodgramUserSerializer):
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            *FoodgramUserSerializer.Meta.fields, 'recipes_count', 'recipes'
        )

    def get_recipes(self, author):
        recipes_limit = self.context['request'].GET.get(
            'recipes_limit', 10**10
        )
        try:
            recipes_limit = int(recipes_limit)
        except ValueError:
            raise serializers.ValidationError(
                {'limit': 'Параметр должен быть целым числом!'}
            )
        return [
            {
                'id': recipe.id,
                'name': recipe.name,
                'cooking_time': recipe.cooking_time,
                'image': recipe.image.url if recipe.image else None,
            }
            for recipe in author.recipes.all()[:recipes_limit]
        ]
