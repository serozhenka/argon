from django.conf import settings
from django.contrib.contenttypes.fields import ContentType
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from django.urls import reverse

from .models import ChatRoomMessage, ChatRoom

@receiver(pre_delete, sender=ChatRoomMessage)
def set_chat_room_last_message_if_last_message_deleted(sender: ChatRoomMessage, instance: ChatRoomMessage, **kwargs):
    if instance.room.last_message == instance:
        room_messages = sender.objects.filter(room=instance.room).order_by('-timestamp')
        instance.room.last_message = room_messages[1] if room_messages.count() > 1 else None
        instance.room.save()

@receiver(post_save, sender=ChatRoomMessage)
def set_first_unread_message_and_create_notification_if_created(sender, instance: ChatRoomMessage, created, **kwargs):
    if created:
        instance.room.last_message = instance
        instance.room.save()

        instance.notifications.create(
            sender=instance.user,
            receiver=instance.room.other_user(instance.user),
            action_name="chat_message",
            message=f"{instance.user.username} send you a message",
            redirect_url=f"{settings.BASE_URL}{reverse('chat:chat-page', kwargs={'username': instance.user.username})}",
            content_type=ContentType.objects.get_for_model(instance),
        )

@receiver(post_delete, sender=ChatRoomMessage)
def delete_chat_room_message_body(sender: ChatRoomMessage, instance, **kwargs):
    try:
        instance.body.delete()
    except Exception:
        pass









