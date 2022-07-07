from django.conf import settings
from django.core.serializers.json import Serializer

from .models import ChatRoomMessage
from notifications.models import Notification

def calculate_timestamp(timestamp):
    ts = timestamp.strftime("%H:%M, %b %e")
    return str(ts)


class ChatRoomMessageSerializer(Serializer):
    def get_dump_object(self, obj: ChatRoomMessage) -> dict:
        return {
            'message': obj.body.text,
            'username': obj.user.username,
            'timestamp': calculate_timestamp(obj.timestamp),
            'is_read': obj.is_read,
            'id': str(obj.id),
        }

def clear_previous_message_notifications(sender: settings.AUTH_USER_MODEL, receiver: settings.AUTH_USER_MODEL):
    for receive_user in [sender, receiver]:
        notifications_to_delete = Notification.objects.filter(
            sender=sender,
            receiver=receive_user,
            action_name__in=["chat_message_new", "chat_message_edit"],
        )
        notifications_to_delete.delete()