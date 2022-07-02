from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import ChatRoomMessage, ChatRoom

@receiver(post_save, sender=ChatRoomMessage)
def set_chat_room_last_message(sender, instance: ChatRoomMessage, created, **kwargs):
    if created:
        instance.room.last_message = instance
        instance.room.save()

@receiver(pre_delete, sender=ChatRoomMessage)
def set_chat_room_last_message_if_last_message_deleted(sender: ChatRoomMessage, instance: ChatRoomMessage, **kwargs):
    if instance.room.last_message == instance:
        room_messages = sender.objects.filter(room=instance.room).order_by('-timestamp')
        instance.room.last_message = room_messages[1] if room_messages.count() > 2 else None
        instance.room.save()









