from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from .models import Favorite, Follow, User, Cart
from recipes.models import Recipe, Ingredient, Tag


class RecipeSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)
    ingredients = serializers.StringRelatedField(many=True, read_only=True)
    tags = serializers.SlugRelatedField(many=True, read_only=True,
                                        slug_field='tags')

    class Meta:
        fields = ('author', 'name', 'image', 'text', 'cooking_time',
                  'ingredients', 'tags', 'pub_date')
        model = Recipe


class TagSerializer(serializers.ModelSerializer):
    recipe = serializers.StringRelatedField(many=True)

    class Meta:
        fields = ('name', 'color', 'slug', 'recipe')
        model = Tag


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Favorite


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""
    user = SlugRelatedField(slug_field='username',
                            read_only=True,
                            default=serializers.CurrentUserDefault())
    following = SlugRelatedField(slug_field='username',
                                 queryset=User.objects.all())

    def validate_following(self, data):
        if self.context['request'].user == data:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.')
        return data

    class Meta:
        fields = '__all__'
        model = Follow
        validators = (
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message=('Вы уже подписаны!')
            ),
        )


class CartSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(slug_field='buyer',
                            read_only=True,
                            default=serializers.CurrentUserDefault())
    item = SlugRelatedField(slug_field='item',
                            queryset=Recipe.objects.all())

    class Meta:
        fields = '__all__'
        model = Cart
        validators = (
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=('user', 'following'),
                message=('Предмет уже в корзине)')
            ),
        )


class IngredientSerializer(serializers.ModelSerializer):
    recipe = serializers.StringRelatedField(many=True)

    class Meta:
        fields = ('name', 'measurement_unit', 'recipe')
        model = Ingredient
