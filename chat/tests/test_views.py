from django.test import TestCase, Client
from django.urls import reverse
from model_bakery import baker

from users.models import Account
from chat.models import ChatRoom

class TestChatPublicViews(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.user = baker.make(Account)
        self.other_user = baker.make(Account)

        self.chat_general_url = reverse('chat:chat-general-page')
        self.chat_url = reverse('chat:chat-page', kwargs={'username': self.other_user.username})

    def test_chat_general_get_request(self):
        response = self.client.get(self.chat_general_url)
        self.assertEqual(response.status_code, 302)

    def test_chat_get_request(self):
        response = self.client.get(self.chat_url)
        self.assertEqual(response.status_code, 302)


class TestChatPrivateViews(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.pwd = '21b4f6bcb67f57ce9487cfbd0eb91265'
        self.user = baker.make(Account)
        self.user.set_password(self.pwd)
        self.user.save()
        self.client.login(email=self.user.email, password=self.pwd)

        self.other_user = baker.make(Account)

        self.chat_general_url = reverse('chat:chat-general-page')
        self.chat_url = reverse('chat:chat-page', kwargs={'username': self.other_user.username})

    def test_chat_general_get_request(self):
        response = self.client.get(self.chat_general_url)
        self.assertEqual(response.status_code, 200)

    def test_chat_user_not_exists_get_request(self):
        url = reverse('chat:chat-page', kwargs={'username': "nonexisting"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_chat_get_request(self):
        response = self.client.get(self.chat_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ChatRoom.objects.filter(user1=self.user, user2=self.other_user).count(), 1)




