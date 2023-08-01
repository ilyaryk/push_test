from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator 

class RoleChoices(models.TextChoices):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class User(AbstractUser):
    "Класс переопределяет стандартную модель User."
    username = models.CharField(
        max_length=150,
        blank=False,
        unique=True,
    )
    email = models.EmailField(
        blank=False,
        unique=True,
        max_length=254,
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )
    password = models.CharField(
        max_length=150,
        blank=False,
        null=False,
    )
    role = models.CharField(
        max_length=150,
        blank=False,
        choices=RoleChoices.choices,
        default=RoleChoices.USER,
    )


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE, related_name='author')
    name = models.CharField(max_length=200,
                            blank=False,
                            null=False)
    image = models.ImageField(
        upload_to='static/', null=True, blank=True)
    text = models.TextField(default='default',
                            blank=False,
                            null=False)
    cooking_time = models.IntegerField(validators=[MinValueValidator(1)],
                                       blank=False,
                                       null=False)
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('pub_date',)

    def __str__(self):
        return self.name[:15]


class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='ingredients',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    name = models.CharField(max_length=100)
    measurement_unit = models.CharField(default='кг', max_length=100)

    def __str__(self):
        return self.name[:15]


class Tag(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='tags',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)

    def __str__(self):
        return self.name[:15]


class Favorite(models.Model):
    class Meta:
        db_table = 'api_favorite'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite')]
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE, related_name='fan')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE, related_name='fav')


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following')


class Cart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='buyer')
    item = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='item')
