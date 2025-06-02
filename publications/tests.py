from django.test import TestCase, Client
from django.urls import reverse

from users.models import User, Subscription
from publications.models import Publication, Commentary


class PublicationViewsTestCase(TestCase):
    def setUp(self):
        # Создаём автора вручную (UserManager.create_user не подходит с кастомной моделью)
        self.author = User(
            phone_number='79001112233',
            first_name='Автор',
            last_name='Тест'
        )
        self.author.set_password('pass')
        self.author.save()

        # Создаём подписчика
        self.subscriber = User(
            phone_number='79004445566',
            first_name='Подписчик',
            last_name='Тест'
        )
        self.subscriber.set_password('pass')
        self.subscriber.save()

        # Публикации: бесплатная и платная
        self.free_pub = Publication.objects.create(
            title='Бесплатная',
            body='Текст',
            author=self.author,
            is_free=True
        )
        self.paid_pub = Publication.objects.create(
            title='Платная',
            body='Текст',
            author=self.author,
            is_free=False
        )

        # Комментарий к бесплатной публикации
        self.comment = Commentary.objects.create(
            author=self.subscriber,
            publication=self.free_pub,
            body='Коммент'
        )

        self.client = Client()


    def test_detail_view_increments_views_and_access_control(self):
        detail_url = reverse('publications:publication-detail', args=[self.free_pub.pk])

        # Без логина → редирект (302)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 302)

        # Логинимся подписчиком
        self.client.login(phone_number='79004445566', password='pass')

        # Доступ к бесплатной: OK + инкремент
        before = self.free_pub.views_count
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.free_pub.refresh_from_db()
        self.assertEqual(self.free_pub.views_count, before + 1)

        # Доступ к платной без подписки: 302 или 403
        paid_url = reverse('publications:publication-detail', args=[self.paid_pub.pk])
        response = self.client.get(paid_url)
        self.assertNotEqual(response.status_code, 200)

        # Подписываем и повторяем
        Subscription.objects.create(subscriber=self.subscriber, author=self.author, price=100)
        response = self.client.get(paid_url)
        self.assertEqual(response.status_code, 200)
        self.paid_pub.refresh_from_db()
        self.assertEqual(self.paid_pub.views_count, 1)

    def test_create_view_requires_login_and_creates_publication(self):
        create_url = reverse('publications:publication-create')

        # Без логина → редирект
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 302)

        # Логинимся подписчиком
        self.client.login(phone_number='79004445566', password='pass')
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 200)

        data = {'title': 'Новая', 'body': 'Контент', 'is_free': True}
        response = self.client.post(create_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Publication.objects.filter(title='Новая', author=self.subscriber).exists()
        )

    def test_update_and_delete_permissions(self):
        update_url = reverse('publications:publication-update', args=[self.free_pub.pk])
        delete_url = reverse('publications:publication-delete', args=[self.free_pub.pk])

        # Логинимся не автором
        self.client.login(phone_number='79004445566', password='pass')
        response = self.client.get(update_url)
        self.assertNotEqual(response.status_code, 200)
        response = self.client.post(delete_url)
        self.assertNotEqual(response.status_code, 200)

        # Логинимся автором
        self.client.logout()
        self.client.login(phone_number='79001112233', password='pass')
        response = self.client.post(update_url, {
            'title': 'Изменено',
            'body': 'Ok',
            'is_free': True
        })
        self.assertEqual(response.status_code, 302)
        self.free_pub.refresh_from_db()
        self.assertEqual(self.free_pub.title, 'Изменено')

        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Publication.objects.filter(pk=self.free_pub.pk).exists())

    def test_add_edit_delete_comment(self):
        detail_url = reverse('publications:publication-detail', args=[self.free_pub.pk])

        # Логинимся подписчиком
        self.client.login(phone_number='79004445566', password='pass')

        # Добавляем комментарий
        add_url = reverse('publications:add-commentary', args=[self.free_pub.pk])
        response = self.client.post(add_url, {'body': 'Тестовый'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Commentary.objects.filter(body='Тестовый', author=self.subscriber).exists()
        )

        # Редактируем свой комментарий
        comment = Commentary.objects.get(body='Тестовый')
        edit_url = reverse('publications:edit-commentary', args=[comment.pk])
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(edit_url, {'body': 'Изменён'})
        self.assertEqual(response.status_code, 302)
        comment.refresh_from_db()
        self.assertEqual(comment.body, 'Изменён')

        # Удаляем свой комментарий
        delete_url = reverse('publications:delete-commentary', args=[comment.pk])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Commentary.objects.filter(pk=comment.pk).exists())

    def test_toggle_likes(self):
        self.client.login(phone_number='79004445566', password='pass')

        # Лайк публикации
        like_pub_url = reverse('publications:toggle-publication-like', args=[self.free_pub.pk])
        response = self.client.post(like_pub_url)
        self.assertEqual(response.status_code, 302)
        self.free_pub.refresh_from_db()
        self.assertIn(self.subscriber, self.free_pub.likes.all())

        # Убираем лайк
        response = self.client.post(like_pub_url)
        self.assertEqual(response.status_code, 302)
        self.free_pub.refresh_from_db()
        self.assertNotIn(self.subscriber, self.free_pub.likes.all())

        # Лайк комментария
        like_comment_url = reverse('publications:toggle-comment-like', args=[self.comment.pk])
        response = self.client.post(like_comment_url)
        self.assertEqual(response.status_code, 302)
        self.comment.refresh_from_db()
        self.assertIn(self.subscriber, self.comment.likes.all())

        # Убираем лайк комментария
        response = self.client.post(like_comment_url)
        self.assertEqual(response.status_code, 302)
        self.comment.refresh_from_db()
        self.assertNotIn(self.subscriber, self.comment.likes.all())
