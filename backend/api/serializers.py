from djoser.serializers import (
    UserCreateSerializer,
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


# --------------- Сериалайзеры для User ---------------
class CustomUserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + ('avatar',)


class CustomUserSerializer(UserSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ('avatar', 'is_subscribed')
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscriptions.objects.filter(
            user=request.user, author=user
        ).exists()


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
        read_only_fields = ('__all__',)


class RecipeReadSerializer(serializers.ModelSerializer):
    '''
    Serializer для модели Recipe - чтение данных
    '''
    author = CustomUserSerializer()
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

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        return not user.is_anonymous and FavoriteRecipes.objects.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        return not user.is_anonymous and ShoppingList.objects.filter(
            recipe=recipe
        ).exists()


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
        if 'image' not in serializer_data or serializer_data['image'] is None:
            raise serializers.ValidationError(
                'Поле "image" обязательно для заполнения!'
            )
        return serializer_data

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError(
                'В рецепте должен быть хотя бы один ингредиент!'
            )
        ingredients_list = []
        for item in ingredients:
            if item in ingredients_list:
                raise ValidationError(
                    'В рецепте не может быть повторяющихся ингредиентов!'
                )
            ingredients_list.append(item)
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError('В рецепте должен быть хотя бы один тег!')
        tags_list = []
        for item in tags:
            if item in tags_list:
                raise ValidationError(
                    'В рецепте не может быть повторяющихся тегов!'
                )
            tags_list.append(item)
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
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Это обязательное поле!'}
            )
        tags = validated_data.pop('tags', [])
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Это обязательное поле!'}
            )
        recipe.recipe_ingredients.all().delete()
        self.write_data(recipe, ingredients, tags)
        return super().update(recipe, validated_data)

    def write_data(self, recipe, ingredients, tags):
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        recipe.tags.set(tags)


class RecipeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(CustomUserSerializer):
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count', 'recipes',
        )

    def get_recipes(self, author):
        recipes = Recipe.objects.filter(author=author)
        recipes_limit = self.context.get('limit', 0)
        if recipes_limit:
            recipes = recipes[:recipes_limit]
        return RecipeMiniSerializer(recipes, many=True).data
