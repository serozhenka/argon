from django.test import TestCase
from django.urls import resolve, reverse
from model_bakery import baker

from users.models import Account
from follow import views

class TestFollowUrls(TestCase):

    def setUp(self) -> None:
        self.user = baker.make(Account)

    def test_login_url_resolved(self):
        url = reverse('follow:follow-action', kwargs={'username': self.user.username})
        self.assertEqual(resolve(url).func, views.follow_general_view)
