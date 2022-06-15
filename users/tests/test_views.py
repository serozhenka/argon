from django.test import TestCase, Client
from django.urls import reverse

from users.models import Account

class TestUserViews(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.login_url = reverse('login')
        self.register_url = reverse('register')

    def test_login_get_request(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_register_post_request(self):
        response = self.client.post(self.register_url, {
            'email': 'testing@gmail.com',
            'username': 'testing',
            'password1': '21b4f6bcb67f57ce9487cfbd0eb91265',
            'password2': '21b4f6bcb67f57ce9487cfbd0eb91265'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Account.objects.count(), 1)

    def test_register_get_request(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
