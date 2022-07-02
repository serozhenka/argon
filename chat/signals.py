from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import ChatRoomMessage

@receiver(post_save, sender=ChatRoomMessage)
def set_chat_room_last_message(sender, instance: ChatRoomMessage, created, **kwargs):
    if created:
        instance.room.last_message = instance
        instance.room.save()

# @receiver(pre_delete, sender=ChatRoomMessage)
# def set_chat_room_last_message_if_last_message_deleted(sender, instance: ChatRoomMessage, **kwargs):
#     if instance.room.last_message == instance:
#         last_message = sender.objects









