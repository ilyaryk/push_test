from django.db import models


class RoleChoices(models.TextChoices):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
