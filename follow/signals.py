from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.contenttypes.fields import ContentType
from django.urls import reverse

from .models import FollowingRequest
from notifications.models import Notification

@receiver(pre_save, sender=FollowingRequest)
def create_send_fr_notification(sender: FollowingRequest, instance: FollowingRequest, **kwargs):
    to_send = not instance.id

    if instance.id:
        previous = sender.objects.get(id=instance.id)
        if not previous.is_active and instance.is_active:
            to_send = True

    if to_send:
        # clear previous notifications
        Notification.objects.filter(sender=instance.sender, receiver=instance.receiver, action_name="send_fr").delete()

        instance.notifications.create(
            sender=instance.sender,
            receiver=instance.receiver,
            action_name="send_fr",
            message=f"{instance.sender.username} send your following request",
            redirect_url=f"{settings.BASE_URL}{reverse('account:account', kwargs={'username': instance.sender.username})}",
            content_type=ContentType.objects.get_for_model(instance),
        )