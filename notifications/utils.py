from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.serializers.json import Serializer
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.conf import settings
from django.urls import reverse

from .models import Notification


channel_layer = get_channel_layer()

def send_notification_to_channel_layer(notification, notifications_to_delete_id_list):
    async_to_sync(channel_layer.group_send)(f"notifications_{notification.receiver.username}", {
        'type': 'notification.send_new',
        'notification': NotificationsSerializer().serialize([notification]),
        'notifications_to_delete_id_list': notifications_to_delete_id_list,
    })


class NotificationsSerializer(Serializer):

    def get_dump_object(self, obj: Notification) -> dict:
        dump_object = {
            'sender': {
                'username': obj.sender.username,
                'image': obj.sender.image.url,
                'url': f"{settings.BASE_URL}{reverse('account:account', kwargs={'username': obj.sender.username})}",
            },
            'action_name': obj.action_name,
            'message': obj.message,
            'redirect_url': str(obj.redirect_url),
            'natural_timestamp': str(naturaltime(obj.timestamp)),
            'id': str(obj.id),
            'content_type': str(obj.content_type),
        }

        if obj.content_type.model in ['comment', 'postlike']:
            dump_object.update({
                'post': {
                    'image': obj.content_object.post.get_first_image_url,
                }
            })

        if obj.content_type.model == 'comment':
            dump_object.update({
                'comment': {
                    'body': obj.content_object.description,
                }
            })

        return dump_object