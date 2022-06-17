from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Account
from follow.models import Following, Followers

@receiver(post_save, sender=Account)
def create_following_model(sender, instance, created, **kwargs):
    if created:
        Following.objects.create(user=instance)

@receiver(post_save, sender=Account)
def create_followers_model(sender, instance, created, **kwargs):
    if created:
        Followers.objects.create(user=instance)


