from django.contrib.auth.models import AbstractUser
from django.db import models


class RoleChoices(models.TextChoices):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
