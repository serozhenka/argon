from django.test import SimpleTestCase
from django.urls import resolve, reverse

from users import views

class TestUserUrls(SimpleTestCase):

    def test_login_url_resolved(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func, views.login_page)

    def test_register_url_resolved(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func, views.register_page)

    def test_logout_url_resolved(self):
        url = reverse('logout')
        self.assertEqual(resolve(url).func, views.logout_page)