from django.contrib.contenttypes.fields import ContentType
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from .models import ChatRoomMessage, ChatRoom, ChatRoomMessageBody
from .utils import clear_previous_message_notifications
from notifications.utils import (
    send_chat_message_notification_to_channel_layer,
    send_chat_message_edit_notification_to_channel_layer,
    send_room_empty_notification_to_channel_layer
)


@receiver(post_save, sender=ChatRoomMessage)
def set_first_unread_message_and_create_notification_if_created(sender, instance: ChatRoomMessage, created, **kwargs):
    if created:
        instance.room.last_message = instance
        instance.room.save()

        clear_previous_message_notifications(sender=instance.user, receiver=instance.room.other_user(instance.user))

        for user in [instance.user, instance.room.other_user(instance.user)]:
            notification = instance.notifications.create(
                sender=instance.user,
                receiver=user,
                action_name="chat_message_new",
                content_type=ContentType.objects.get_for_model(instance),
            )

            send_chat_message_notification_to_channel_layer(notification)

@receiver(post_save, sender=ChatRoomMessageBody)
def create_message_edited_notification(sender: ChatRoomMessageBody, instance: ChatRoomMessageBody, created, **kwargs):

    if not created and instance.message.room.last_message == instance.message:
        clear_previous_message_notifications(
            sender=instance.message.user,
            receiver=instance.message.room.other_user(instance.message.user)
        )

        for user in [instance.message.user, instance.message.room.other_user(instance.message.user)]:
            notification = instance.message.notifications.create(
                sender=instance.message.user,
                receiver=user,
                action_name="chat_message_edit",
                content_type=ContentType.objects.get_for_model(instance.message),
            )

            send_chat_message_edit_notification_to_channel_layer(notification)


@receiver(pre_delete, sender=ChatRoomMessage)
def set_chat_room_last_message_and_create_notification_if_last_message_deleted(sender: ChatRoomMessage, instance: ChatRoomMessage, **kwargs):
    if instance.room.last_message == instance:
        room_messages = sender.objects.filter(room=instance.room).order_by('-timestamp')
        instance.room.last_message = room_messages[1] if room_messages.count() > 1 else None
        instance.room.save()

        clear_previous_message_notifications(sender=instance.user, receiver=instance.room.other_user(instance.user))

        for user in [instance.user, instance.room.other_user(instance.user)]:
            if instance.room.last_message:
                notification = instance.room.last_message.notifications.create(
                    sender=instance.user,
                    receiver=user,
                    action_name="chat_message_edit",
                    content_type=ContentType.objects.get_for_model(instance.room.last_message),
                )

                send_chat_message_edit_notification_to_channel_layer(notification)
            else:
                send_room_empty_notification_to_channel_layer(user.username, instance.room.other_user(user).username)

@receiver(post_delete, sender=ChatRoomMessage)
def delete_chat_room_message_body(sender: ChatRoomMessage, instance, **kwargs):
    try:
        instance.body.delete()
    except Exception:
        pass









