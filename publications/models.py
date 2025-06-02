from django.db import models

from users.models import User

NULLABLE = {'blank': True, 'null': True}


class Publication(models.Model):
    title = models.CharField(max_length=100, verbose_name='название')
    body = models.TextField(verbose_name='содержание')
    image = models.ImageField(upload_to='publications/', **NULLABLE, verbose_name='изображение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')

    views_count = models.IntegerField(default=0, verbose_name='количество просмотров')
    likes = models.ManyToManyField(User, related_name='liked_publications', verbose_name='лайки')
    is_free = models.BooleanField(default=True, verbose_name='бесплатно?')

    author = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='publications', **NULLABLE, verbose_name='автор')

    def likes_count(self):
        return self.likes.count()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'публикации'


class Commentary(models.Model):
    body = models.TextField(verbose_name='содержание')
    likes = models.ManyToManyField(User, related_name='liked_commentaries', verbose_name='лайки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')

    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='commentaries', verbose_name='публикация')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, **NULLABLE, verbose_name='автор')

    def likes_count(self):
        return self.likes.count()

    def __str__(self):
        return self.body

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
