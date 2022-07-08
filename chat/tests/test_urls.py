from django.test import TestCase
from django.urls import resolve, reverse
from model_bakery import baker

from chat import views
from users.models import Account

class TestUserUrls(TestCase):

    def setUp(self) -> None:
        self.user = baker.make(Account)

    def test_chat_general_url_resolved(self):
        url = reverse('chat:chat-general-page')
        self.assertEqual(resolve(url).func, views.chat_page)

    def test_chat_url_resolved(self):
        url = reverse('chat:chat-page', kwargs={'username': self.user.username})
        self.assertEqual(resolve(url).func, views.chat_page)
