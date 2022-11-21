from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        validators=(validate_username,),
    )
    email = models.EmailField(
        "Электронная почта",
        max_length=254,
        unique=True,
        blank=False,
        null=False,
    )
    first_name = models.CharField(
        "Имя пользователя", max_length=150, blank=True
    )
    last_name = models.CharField(
        "Фамилия пользователя", max_length=150, blank=True
    )

    USERNAME_FIELD = "email"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "пользователи"
