from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class CoreViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.csrf_client = Client(enforce_csrf_checks=True)

    def test_page_not_found(self):
        """Проверка корректной обработки ошибки 404."""
        response = self.guest_client.get('/unexisting_url/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_csrf_failure(self):
        """Проверка корректной обработки ошибки 403csrf."""
        response = self.csrf_client.post(
            reverse('users:signup'),
            data={
                'first_name': 'test_first_name',
                'last_name': 'test_last_name',
                'username': 'test_username',
                'email': 'test@email.net'
            }
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
