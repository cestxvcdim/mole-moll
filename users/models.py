from django.contrib.auth.models import AbstractUser
from django.db import models

NULLABLE = {'blank': True, 'null': True}


class User(AbstractUser):
    username = None
    phone_number = models.CharField(max_length=12, unique=True, verbose_name='номер телефона')
    first_name = models.CharField(max_length=30, verbose_name='имя')
    last_name = models.CharField(max_length=30, verbose_name='фамилия')

    email = models.EmailField(**NULLABLE, verbose_name='почта')
    avatar = models.ImageField(upload_to='users/', **NULLABLE, verbose_name='фото профиля')
    country = models.CharField(max_length=50, **NULLABLE, verbose_name='страна')

    token = models.CharField(max_length=100, **NULLABLE, verbose_name='токен')

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'


class Subscription(models.Model):
    price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='цена')
    payment_date = models.DateField(auto_now_add=True, verbose_name='дата покупки')

    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions', verbose_name='подписчик')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='автор')

    def __str__(self):
        return f'{self.subscriber.first_name} {self.subscriber.last_name}, {self.author.first_name} {self.author.last_name}'

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(fields=['subscriber', 'author'], name='unique_subscriber_author')
        ]
