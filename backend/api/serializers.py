from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from django.core.validators import MinValueValidator

#from drf_extra_fields.fields import Base64ImageField
from assistance.utils import Base64ImageField
from users.models import User
from recipes.models import (Recipe, Ingredient, Tag,
                            AmountOfIngredient, Favorite, Follow, Cart)



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('first_name', 'last_name', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}
        model = User

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
	    first_name=validated_data['first_name'],
	    last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
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
    recipe = SlugRelatedField(slug_field='recipe',
                              queryset=Recipe.objects.all())

    class Meta:
        fields = '__all__'
        model = Cart
        validators = (
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=('user', 'recipe'),
                message=('Предмет уже в корзине)')
            ),
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class IngredientsCreateOrUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=(MinValueValidator(1),)
    )

    class Meta:
        model = AmountOfIngredient
        fields = (
            'id',
            'amount',
        )


class IngredientsReadOnlySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = AmountOfIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class UserNoRecipeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            )

    def get_is_subscribed(self, user):
        follower = self.context.get('request').user
        return Follow.objects.filter(user=follower, following=user).exists()


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserNoRecipeSerializer(read_only=True)
    ingredients = IngredientsReadOnlySerializer(
        many=True,
        source='amounts_of_ingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Favorite.objects.filter(user=user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Cart.objects.filter(user=user, recipe=recipe).exists()


class RecipeCreateOrUpdateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientsCreateOrUpdateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(MinValueValidator(1),)
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Рецепт должен содержать минимум 1 ингредиент!'
            )
        for ingredient in ingredients:
            if ingredients.count(ingredient) > 1:
                raise serializers.ValidationError(
                    'У рецепта не может быть два одинаковых ингредиента!'
                )
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Для рецепта нужен хотя бы один тег!'
            )
        return tags

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Время приготовления меньше 1 минуты!'
            )
        return cooking_time

    def create_ingredients_amounts(self, ingredients, recipe):
        '''Создает смежную модель для хранения ингредиентов и их кол-ва'''
        objs = []
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            objs.append(AmountOfIngredient(
                ingredient_id=ingredient['id'],
                recipe=recipe,
                amount=amount))
        AmountOfIngredient.objects.bulk_create(objs)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe,
                                        ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(recipe=instance,
                                        ingredients=ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, data):
        return RecipeReadOnlySerializer(
            context=self.context).to_representation(data)



class RecipeInSubscribeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class UserReadOnlySerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeInSubscribeSerializer(many=True)
    #recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
           'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, user):
        follower = self.context.get('request').user
        return Follow.objects.filter(user=follower, following=user).exists()

    def get_recipes_count(self, user):
        return user.recipes.count()

#    def get_recipes(self, user):
 #       queryset = user.recipes.all()
  #      return JSONRenderer().render(RecipeReadOnlySerializer(queryset, many=True).data)
class UserAnonSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
           )



class RecipeAnonSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserAnonSerializer(read_only=True)
    ingredients = IngredientsReadOnlySerializer(
        many=True,
        source='amounts_of_ingredients')
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )


