from django.contrib.auth.models import AbstractUser
from django.db import models

from recipes.models import Recipe


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
