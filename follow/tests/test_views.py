import json

from django.contrib.auth import get_user
from django.test import TestCase, Client
from django.urls import reverse
from model_bakery import baker

from users.models import Account
from follow.models import Following, Followers, FollowingRequest

class TestFollowPublicViews(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.user = baker.make(Account)

        self.follow_general_url = reverse('follow:follow-action', kwargs={'username': self.user.username})

    def test_follow_general_get_request(self):
        response = self.client.get(self.follow_general_url)
        self.assertEqual(response.status_code, 302)

class TestUserPrivateViews(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.pwd = '21b4f6bcb67f57ce9487cfbd0eb91265'
        self.user = baker.make(Account)
        self.other_user = baker.make(Account)
        self.user.set_password(self.pwd)
        self.user.save()
        self.client.login(email=self.user.email, password=self.pwd)

        self.user_following_model = Following.objects.get(user=self.user)
        self.other_user_followers_model = Followers.objects.get(user=self.other_user)

        self.follow_general_self_url = reverse('follow:follow-action', kwargs={'username': self.user.username})
        self.follow_general_url = reverse('follow:follow-action', kwargs={'username': self.other_user.username})

    def test_follow_general_get_request(self):
        response = self.client.get(self.follow_general_url)

        self.assertEqual(response.status_code, 302)

    def test_follow_general_post_request_on_self(self):
        response = self.client.post(self.follow_general_self_url, {'action': 'follow'})

        self.assertEqual(response.status_code, 302)

    def test_follow_general_blank_post_request(self):
        response = self.client.post(self.follow_general_url, {})
        response_content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content['response_result'], 'error')

    def test_follow_general_follow_post_request(self):
        response = self.client.post(self.follow_general_url, {'action': 'follow'})
        response_content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content['response_result'], 'success')
        self.assertTrue(self.user_following_model.is_following(self.other_user))
        self.assertTrue(self.other_user_followers_model.is_follower(self.user))

    def test_follow_general_unfollow_post_request(self):
        self.user_following_model.add_following(self.other_user)
        response = self.client.post(self.follow_general_url, {'action': 'unfollow'})
        response_content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content['response_result'], 'success')
        self.assertFalse(self.user_following_model.is_following(self.other_user))
        self.assertFalse(self.other_user_followers_model.is_follower(self.user))

    def test_follow_general_follow_private_post_request(self):
        self.other_user.is_public = False
        self.other_user.save()
        response = self.client.post(self.follow_general_url, {'action': 'follow'})
        response_content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content['response_result'], 'success')
        self.assertTrue(FollowingRequest.objects.filter(sender=self.user, receiver=self.other_user).exists())
