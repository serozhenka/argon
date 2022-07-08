from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.contenttypes.fields import ContentType
from django.urls import reverse

from .models import FollowingRequest
from .utils import clear_send_fr_notifications
from notifications.models import Notification
from notifications.utils import send_notification_to_channel_layer

@receiver(post_save, sender=FollowingRequest)
def create_send_fr_notification(sender: FollowingRequest, instance: FollowingRequest, created, **kwargs):

    if instance.is_active:
        # clear previous notifications
        notifications_to_delete_id_list = clear_send_fr_notifications(instance.sender, instance.receiver)

        notification = instance.notifications.create(
            sender=instance.sender,
            receiver=instance.receiver,
            action_name="send_fr",
            message=f"send your following request",
            redirect_url=f"{settings.BASE_URL}{reverse('account:account', kwargs={'username': instance.sender.username})}",
            content_type=ContentType.objects.get_for_model(instance),
        )

        send_notification_to_channel_layer(notification, notifications_to_delete_id_list)