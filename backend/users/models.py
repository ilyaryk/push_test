from django.contrib.auth.models import AbstractUser
from django.db import models

from assistance.models import RoleChoices


class User(AbstractUser):
    "Класс переопределяет стандартную модель User."
    is_staff = True
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
