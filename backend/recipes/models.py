from django.db import models
from django.core.validators import MinValueValidator

from api.models import User


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
