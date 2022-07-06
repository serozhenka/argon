from django.core.serializers.json import Serializer
from django.contrib.humanize.templatetags.humanize import naturaltime

from .models import Notification


class NotificationsSerializer(Serializer):

    def get_dump_object(self, obj: Notification) -> dict:
        return {
            'sender': {
                'username': obj.sender.username,
                'image': obj.sender.image.url,
            },
            'action_name': obj.action_name,
            'message': obj.message,
            'redirect_url': str(obj.redirect_url),
            'natural_timestamp': str(naturaltime(obj.timestamp)),
            'id': str(obj.id),
            'content_type': str(obj.content_type),
        }