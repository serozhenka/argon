from django.test import TestCase
from django.utils import timezone
from model_bakery import baker

from users.models import Account
from follow.models import Following, Followers, FollowingRequest

from datetime import timedelta


class TestFollowingModel(TestCase):
    """Testing custom user model"""

    def setUp(self) -> None:
        self.user = baker.make(Account)
        self.other_user = baker.make(Account)

        self.following_model = Following.objects.filter(user=self.user).first()
        self.other_followers_model = Followers.objects.filter(user=self.other_user).first()

    def test_following_model_created(self):
        self.assertTrue(Following.objects.filter(user=self.user).exists())

        self.assertEqual(str(self.following_model), self.user.email)

    def test_adding_other_user_to_following(self):
        self.following_model.add_following(self.other_user)

        self.assertTrue(self.other_followers_model.is_follower(self.user))
        self.assertTrue(self.following_model.is_following(self.other_user))

    def test_is_following_method(self):
        self.following_model.add_following(self.other_user)

        self.assertTrue(self.following_model.is_following(self.other_user))

    def test_adding_self_to_following(self):
        self.following_model.add_following(self.user)

        self.assertFalse(self.other_followers_model.is_follower(self.user))

    def test_removing_follower(self):
        self.following_model.add_following(self.other_user)
        self.following_model.remove_following(self.other_user)

        self.assertFalse(self.other_followers_model.is_follower(self.user))
        self.assertFalse(self.following_model.is_following(self.other_user))

class TestFollowersModel(TestCase):
    """Testing custom user model"""

    def setUp(self) -> None:
        self.user = baker.make(Account)
        self.other_user = baker.make(Account)

        self.following_model = Following.objects.filter(user=self.user).first()
        self.other_followers_model = Followers.objects.filter(user=self.other_user).first()
        self.following_model.add_following(self.other_user)

    def test_following_model_created(self):
        self.assertTrue(Followers.objects.filter(user=self.user).exists())
        self.assertEqual(str(self.following_model), self.user.email)

    def test_is_following_method(self):
        self.assertTrue(self.other_followers_model.is_follower(self.user))

    def test_removing_user_from_followers(self):
        self.other_followers_model.remove_follower(self.user)

        self.assertFalse(self.other_followers_model.is_follower(self.user))
        self.assertFalse(self.following_model.is_following(self.other_user))


class TestFollowingRequestModel(TestCase):
    """Testing custom user model"""

    def setUp(self) -> None:
        self.sender = baker.make(Account)
        self.receiver = baker.make(Account)

        self.following_request = FollowingRequest.objects.create(
            sender=self.sender,
            receiver=self.receiver,
        )

        self.sender_following_model = Following.objects.get(user=self.sender)
        self.receiver_followers_model = Followers.objects.get(user=self.receiver)

    def test_following_model_created(self):
        self.assertEqual(str(self.following_request), f'{self.sender.email}-{self.receiver.email}')

    def test_following_model_timestamp(self):
        self.assertTrue(timezone.now() - timedelta(0, 120) < self.following_request.created)

    def test_accept_friend_request(self):
        self.following_request.accept()

        self.assertFalse(self.following_request.is_active)
        self.assertTrue(self.sender_following_model.is_following(self.receiver))
        self.assertTrue(self.receiver_followers_model.is_follower(self.sender))

    def test_decline_friend_request(self):
        self.following_request.decline()
        
        self.assertFalse(self.following_request.is_active)
        self.assertFalse(self.sender_following_model.is_following(self.receiver))
        self.assertFalse(self.receiver_followers_model.is_follower(self.sender))

    def test_cancel_friend_request(self):
        self.following_request.cancel()

        self.assertFalse(self.following_request.is_active)
        self.assertFalse(self.sender_following_model.is_following(self.receiver))
        self.assertFalse(self.receiver_followers_model.is_follower(self.sender))





