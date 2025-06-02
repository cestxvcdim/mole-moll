from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.urls import reverse

from users.models import User, Subscription
from publications.models import Publication


class UserViewsTestCase(TestCase):
    def setUp(self):
        # Создаём автора и подписчика
        self.author = User(
            phone_number='79001112233',
            first_name='Автор',
            last_name='Тест'
        )
        self.author.set_password('pass')
        self.author.save()

        self.other_user = User(
            phone_number='79004445566',
            first_name='Пользователь',
            last_name='Тест'
        )
        self.other_user.set_password('pass')
        self.other_user.save()

        # Создаем бесплатную и платную публикации автора
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

        self.client = Client()

    def test_register_creates_user_and_redirects(self):
        register_url = reverse('users:register')
        response = self.client.get(register_url)
        self.assertEqual(response.status_code, 200)

        data = {
            'phone_number': '79009990000',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(register_url, data)
        # После успешной регистрации — редирект на login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(phone_number='79009990000').exists())


    def test_user_list_requires_login_and_search(self):
        url = reverse('users:user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Логинимся
        self.client.login(phone_number='79001112233', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        users = response.context['object_list']
        self.assertIn(self.author, users)
        self.assertIn(self.other_user, users)

        # Поиск по first_name
        response = self.client.get(url + '?q=Автор')
        users = response.context['object_list']
        self.assertIn(self.author, users)
        self.assertNotIn(self.other_user, users)

    def test_user_detail_shows_free_or_all_based_on_subscription(self):
        detail_url = reverse('users:user-detail', args=[self.author.pk])

        # Без логина → редирект
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 302)

        # Логинимся как other_user
        self.client.login(phone_number='79004445566', password='pass')
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        pubs = response.context['user_publications']
        # Должна быть только бесплатная
        self.assertEqual(list(pubs), [self.free_pub])

        # Оформляем подписку
        Subscription.objects.create(subscriber=self.other_user, author=self.author, price=Decimal('50'))
        response = self.client.get(detail_url)
        pubs = response.context['user_publications']
        # Должны быть обе
        self.assertEqual(set(pubs), {self.free_pub, self.paid_pub})

    def test_user_update_permissions(self):
        update_url = reverse('users:user-update', args=[self.author.pk])

        # Логинимся другим пользователем → отказ
        self.client.login(phone_number='79004445566', password='pass')
        response = self.client.get(update_url)
        self.assertNotEqual(response.status_code, 200)

        # Логинимся самим собой
        self.client.logout()
        self.client.login(phone_number='79001112233', password='pass')
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 200)

        # Обновляем first_name
        response = self.client.post(update_url, {
            'first_name': 'Изменено',
            'last_name': self.author.last_name,
            'phone_number': self.author.phone_number,
        })
        self.assertEqual(response.status_code, 302)
        self.author.refresh_from_db()
        self.assertEqual(self.author.first_name, 'Изменено')


    def test_subscription_success_creates_subscription_and_redirects(self):
        success_url = reverse('users:subscription-success', args=[self.author.pk])

        # Логинимся
        self.client.login(phone_number='79004445566', password='pass')

        # Вызываем success без существующей подписки
        response = self.client.get(success_url + '?amount_rub=150')
        self.assertEqual(response.status_code, 302)
        sub_exists = Subscription.objects.filter(
            subscriber=self.other_user, author=self.author, price=Decimal('150')
        ).exists()
        self.assertTrue(sub_exists)

        # Повторный заход (подписка уже есть) — просто редирект, но не дублирует
        response = self.client.get(success_url + '?amount_rub=150')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Subscription.objects.filter(subscriber=self.other_user, author=self.author).count(), 1)
