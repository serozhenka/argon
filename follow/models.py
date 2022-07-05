from datetime import datetime
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation, ContentType
from django.db import models
from django.db.models import QuerySet
from django.urls import reverse
from django.utils import timezone
from typing import Union, List

from notifications.models import Notification
from users.models import Account

class Following(models.Model):
    user: Account = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    users_following: Union[QuerySet, List[Account]] = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='users_following', blank=True
    )
    notifications = GenericRelation(Notification)

    def __str__(self):
        return self.user.email

    def count(self):
        return self.users_following.count()

    def is_following(self, other_user) -> bool:
        return other_user in self.users_following.all()

    def add_following(self, other_user: settings.AUTH_USER_MODEL):
        """
        First user subscribes to second user
            1. second user is added to first's user following list
            2. first user is added to second's user followers list
        """
        if other_user == self.user:
            return

        if other_user not in self.users_following.all():
            self.users_following.add(other_user)

        ou_followers_model = Followers.objects.get(user=other_user)

        if self.user not in ou_followers_model.users_followers.all():
            ou_followers_model.users_followers.add(self.user)

        self.create_following_notification(sender=self.user, receiver=other_user)

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

    def create_following_notification(self, sender: settings.AUTH_USER_MODEL, receiver: settings.AUTH_USER_MODEL):
        """Method to create notification when sender follows receiver."""

        # clear previous notifications
        Notification.objects.filter(sender=sender, receiver=receiver, action_name="follow").delete()

        self.notifications.create(
            sender=sender,
            receiver=receiver,
            action_name="follow",
            message=f"{sender.username} started following you",
            redirect_url=f"{settings.BASE_URL}{reverse('account:account', kwargs={'username': sender.username})}",
            content_type=ContentType.objects.get_for_model(self),
        )


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
            ou_following_model.users_following.remove(self.user)


class FollowingRequest(models.Model):
    sender: Account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sender')
    receiver: Account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='receiver')
    is_active: bool = models.BooleanField(default=True)
    created: datetime = models.DateTimeField()
    notifications = GenericRelation(Notification)

    def __str__(self):
        return f'{self.sender}-{self.receiver}'

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

            self.create_accept_fr_notification(sender=self.receiver, receiver=self.sender)

    def decline(self):
        """
        Receiver declines sender's following request
            1. following request is made inactive
        """

        if self.is_active:
            self.is_active = False
            self.save()

            self.create_declined_fr_notification(sender=self.receiver, receiver=self.sender)

    def cancel(self):
        """
        Sender cancels following request to the receiver
            1. following request is made inactive
        """
        if self.is_active:
            self.is_active = False
            self.save()

    def create_accept_fr_notification(self, sender: settings.AUTH_USER_MODEL, receiver: settings.AUTH_USER_MODEL):
        """Method to create notification when sender accepts receiver friend request."""

        # clear previous requests
        Notification.objects.filter(sender=receiver, receiver=sender, action_name="send_fr").delete()
        Notification.objects.filter(sender=sender, receiver=receiver, action_name="accept_fr").delete()

        self.notifications.create(
            sender=sender,
            receiver=receiver,
            action_name="accept_fr",
            message=f"{sender.username} accepted your following request",
            redirect_url=f"{settings.BASE_URL}{reverse('account:account', kwargs={'username': sender.username})}",
            content_type=ContentType.objects.get_for_model(self),
        )

    def create_declined_fr_notification(self, sender: settings.AUTH_USER_MODEL, receiver: settings.AUTH_USER_MODEL):
        """Method to create notification when sender declines receiver friend request."""

        # clear previous requests
        Notification.objects.filter(sender=receiver, receiver=sender, action_name="send_fr").delete()
        Notification.objects.filter(sender=sender, receiver=receiver, action_name="decline_fr").delete()

        self.notifications.create(
            sender=sender,
            receiver=receiver,
            action_name="decline_fr",
            message=f"{sender.username} declined your following request",
            redirect_url=f"{settings.BASE_URL}{reverse('account:account', kwargs={'username': sender.username})}",
            content_type=ContentType.objects.get_for_model(self),
        )

















