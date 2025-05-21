from django.contrib.auth.models import AbstractUser
from django.db import models

NULLABLE = {'blank': True, 'null': True}

class User(AbstractUser):
    username = None
    phone_number = models.CharField(max_length=20, unique=True, verbose_name='номер телефона')

    email = models.EmailField(unique=True, **NULLABLE, verbose_name='почта')
    avatar = models.ImageField(upload_to='users/', **NULLABLE, verbose_name='фото профиля')
    country = models.CharField(max_length=50, **NULLABLE, verbose_name='страна')

    token = models.CharField(max_length=100, **NULLABLE, verbose_name='токен')

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
