from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)

    def __str__(self):
        return self.name[:15]


class Ingredient(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name[:15]


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE, related_name='author')
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='static/', null=True, blank=True)
    text = models.TextField()
    cooking_time = models.IntegerField()
    ingredients = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    tags = models.ForeignKey(Tag, on_delete=models.CASCADE)

    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('pub_date',)

    def __str__(self):
        return self.name[:15]


class Favorite(models.Model):
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
