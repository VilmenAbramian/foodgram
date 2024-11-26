import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (
    FavoriteRecipes, Ingredient,
    RecipeIngredient, Recipe,
    ShoppingList, Tag
)
from users.models import Subscriptions, User
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')
        extra_kwargs = {'color': {'write_only': True}}


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    '''
    Serializer для модели Recipe - чтение данных
    '''
    author = UserSerializer()
    ingredients = IngredientInRecipeSerializer(
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

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return FavoriteRecipes.objects.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return ShoppingList.objects.filter(recipe=obj).exists()
        return False


class AddIngredientSerializer(serializers.ModelSerializer):
    '''
    Serializer для поля ingredients в моделе Recipe
    для добавления ингредиентов в рецепт.
    '''
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    '''
    Serializer для модели Recipe - запись, обновление, удаление данных
    '''
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    image = Base64ImageField(required=True, allow_null=False)

    ingredients = AddIngredientSerializer(many=True, write_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'tags', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def validate_ingredients(self, ingredients):
        if not ingredients or len(ingredients) == 0:
            raise ValidationError(
                'В рецепте должен быть хотя бы один ингредиент!'
            )
        ingredients_list = []
        for item in ingredients:
            if item in ingredients_list:
                raise ValidationError(
                    'В рецепте не может быть повторяющихся элементов!'
                )
            if item['amount'] <= 0:
                raise ValidationError(
                    'Количество ингредиента должно быть больше 0!'
                )
            ingredients_list.append(item)
        return ingredients

    def validate_tags(self, tags):
        if not tags or len(tags) == 0:
            raise ValidationError('В рецепте должен быть хотя бы один тег!')
        tags_list = []
        for item in tags:
            if item in tags_list:
                raise ValidationError(
                    'В рецепте не может быть повторяющихся элементов!'
                )
            tags_list.append(item)
        return tags

    def to_representation(self, recipe_obj):
        serializer = RecipeReadSerializer(recipe_obj, context=self.context)
        representation = serializer.data
        representation['ingredients'] = IngredientInRecipeSerializer(
            recipe_obj.recipe_ingredients.all(), many=True
        ).data
        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError('Автор рецепта не определён!')

        validated_data['author'] = request.user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)

        for ingredient in ingredients:
            RecipeIngredient.objects.update_or_create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])

        instance.recipe_ingredients.all().delete()
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        instance.tags.set(tags)
        return super().update(instance, validated_data)


class RecipeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name',
            'last_name', 'email', 'is_subscribed',
            'avatar', 'recipes_count', 'recipes'
        )

    def get_is_subscribed(self, author):
        return Subscriptions.objects.filter(
            user=self.context['request'].user, author=author
        ).exists()

    def get_recipes_count(self, author):
        recipes = Recipe.objects.filter(author=author)
        return len(recipes)

    def get_recipes(self, author):
        recipes = Recipe.objects.filter(author=author)
        recipes_limit = self.context.get('limit', 0)
        if recipes_limit:
            recipes = recipes[:recipes_limit]
        return RecipeMiniSerializer(recipes, many=True).data
