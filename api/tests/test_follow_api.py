from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from api.serializers import AccountSerializer
from follow.models import Following, Followers
from users.models import Account

class TestFollowPublicApi(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = baker.make(Account)

        self.following_url = reverse('api:api-following-list', kwargs={'username': self.user.username})
        self.followers_url = reverse('api:api-followers-list', kwargs={'username': self.user.username})

    def test_following_list_auth_required(self):
        response = self.client.get(self.following_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_followers_list_auth_required(self):
        response = self.client.get(self.following_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestFollowPrivateApi(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = baker.make(Account)
        self.other_user = baker.make(Account)
        self.client.force_authenticate(self.user)

        self.user_following_model = Following.objects.get(user=self.user)
        self.other_user_followers_model = Followers.objects.get(user=self.other_user)

        self.following_url = reverse('api:api-following-list', kwargs={'username': self.user.username})
        self.other_followers_url = reverse('api:api-followers-list', kwargs={'username': self.other_user.username})

    def test_following_list(self):
        response = self.client.get(self.following_url)
        serializer = AccountSerializer(self.user_following_model.users_following.all(), many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_followers_list(self):
        response = self.client.get(self.other_followers_url)
        serializer = AccountSerializer(self.other_user_followers_model.users_followers.all(), many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
