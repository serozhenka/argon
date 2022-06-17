from datetime import datetime
from django.conf import settings
from django.db import models
from django.db.models import QuerySet
from typing import Union, List

from users.models import Account


class Following(models.Model):
    user: Account = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    users_following: Union[QuerySet, List[Account]] = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='users_following'
    )

    def __str__(self):
        return self.user.email

    def is_following(self, user) -> bool:
        return user in self.users_following.all()

    def add_following(self, user: settings.AUTH_USER_MODEL):
        """
        First user subscribes from second user
            1. second user is added to first's user following list
            2. first user is added to second's user followers list
        """

        if user not in self.users_following.all():
            self.users_following.add(user)

        other_user_followers = Followers.objects.get(user=user).users_followers.all()

        if self.user not in other_user_followers.users_followers.all():
            other_user_followers.add(self.user)

    def remove_following(self, user: settings.AUTH_USER_MODEL):
        """
        First user unsubscribes from second user
            1. second user is removed from first's user following list
            2. first user is removed from second's user followers list
        """

        if user in self.users_following.all():
            self.users_following.remove(user)

        other_user_followers = Followers.objects.get(user=user).users_followers.all()

        if self.user in other_user_followers.users_followers.all():
            other_user_followers.remove(self.user)


class Followers(models.Model):
    user: Account = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    users_followers: Union[QuerySet, List[Account]] = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='users_followers'
    )

    class Meta:
        verbose_name_plural = 'Followers'

    def __str__(self):
        return self.user.email

    def is_follower(self, user) -> bool:
        return user in self.users_followers.all()

    # def add_follower(self, user: settings.AUTH_USER_MODEL):
    #     if user not in self.users_followers.all():
    #         self.users_followers.add(user)

    def remove_follower(self, user: settings.AUTH_USER_MODEL):
        """
        First user removes second user from it's followers
            1. second user is removed from first's user followers list
            2. first user is removed from second's user following list
        """

        if user in self.users_followers.all():
            self.users_followers.remove(user)

        other_user_following = Following.objects.get(user=user).users_following.all()

        if self.user in other_user_following.users_following.all():
            other_user_following.remove(user)


class FollowingRequest(models.Model):
    sender: Account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sender')
    receiver: Account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='receiver')
    is_active: bool = models.BooleanField(default=True)
    created: datetime = models.DateTimeField()

    def accept(self):
        """
        Receiver accepts sender's following request
            1. receiver is added to sender user following list
            2. sender is added to receiver user followers list
        """

        sender_following = Following.objects.get(user=self.sender)
        sender_following.add_following(self.receiver)
        self.is_active = False

    def decline(self):
        """
        Receiver declines sender's following request
            1. following request is made inactive
        """

        self.is_active = False

    def cancel(self):
        """
        Sender cancels following request to the receiver
            1. following request is made inactive
        """

        self.is_active = False

















