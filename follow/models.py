from datetime import datetime
from django.conf import settings
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from typing import Union, List

from users.models import Account


class Following(models.Model):
    user: Account = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    users_following: Union[QuerySet, List[Account]] = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='users_following', blank=True
    )

    def __str__(self):
        return self.user.email

    def count(self):
        return self.users_following.count()

    def is_following(self, other_user) -> bool:
        return other_user in self.users_following.all()

    def add_following(self, other_user: settings.AUTH_USER_MODEL):
        """
        First user subscribes from second user
            1. second user is added to first's user following list
            2. first user is added to second's user followers list
        """

        if other_user not in self.users_following.all():
            self.users_following.add(other_user)

        ou_followers_model = Followers.objects.get(user=other_user)

        if self.user not in ou_followers_model.users_followers.all():
            ou_followers_model.users_followers.add(self.user)

    def remove_following(self, other_user: settings.AUTH_USER_MODEL):
        """
        First user unsubscribes from second user
            1. second user is removed from first's user following list
            2. first user is removed from second's user followers list
        """

        if other_user in self.users_following.all():
            self.users_following.remove(other_user)

        ou_followers_model = Followers.objects.get(user=other_user)

        if self.user in ou_followers_model.users_followers.all():
            ou_followers_model.users_followers.remove(self.user)


class Followers(models.Model):
    user: Account = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    users_followers: Union[QuerySet, List[Account]] = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='users_followers', blank=True
    )

    class Meta:
        verbose_name_plural = 'Followers'

    def __str__(self):
        return self.user.email

    def count(self):
        return self.users_followers.count()

    def is_follower(self, other_user) -> bool:
        return other_user in self.users_followers.all()

    # def add_follower(self, user: settings.AUTH_USER_MODEL):
    #     if user not in self.users_followers.all():
    #         self.users_followers.add(user)

    def remove_follower(self, other_user: settings.AUTH_USER_MODEL):
        """
        First user removes second user from it's followers
            1. second user is removed from first's user followers list
            2. first user is removed from second's user following list
        """

        if other_user in self.users_followers.all():
            self.users_followers.remove(other_user)

        ou_following_model = Following.objects.get(user=other_user)

        if self.user in ou_following_model.users_following.all():
            ou_following_model.users_following.remove(other_user)


class FollowingRequest(models.Model):
    sender: Account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sender')
    receiver: Account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='receiver')
    is_active: bool = models.BooleanField(default=True)
    created: datetime = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.created = timezone.now()
        return super(FollowingRequest, self).save(*args, **kwargs)

    def accept(self):
        """
        Receiver accepts sender's following request
            1. receiver is added to sender user following list
            2. sender is added to receiver user followers list
        """
        if self.is_active:
            sender_following = Following.objects.get(user=self.sender)
            sender_following.add_following(self.receiver)
            self.is_active = False
            self.save()

    def decline(self):
        """
        Receiver declines sender's following request
            1. following request is made inactive
        """

        if self.is_active:
            self.is_active = False
            self.save()

    def cancel(self):
        """
        Sender cancels following request to the receiver
            1. following request is made inactive
        """
        if self.is_active:
            self.is_active = False
            self.save()

















