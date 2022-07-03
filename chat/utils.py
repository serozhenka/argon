from django.core.serializers.json import Serializer

from .models import ChatRoomMessage

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