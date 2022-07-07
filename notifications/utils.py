from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.serializers.json import Serializer
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.conf import settings
from django.urls import reverse

from .models import Notification


channel_layer = get_channel_layer()

# sending general notifications to channel layer
def send_notification_to_channel_layer(notification, notifications_to_delete_id_list):
    async_to_sync(channel_layer.group_send)(f"notifications_{notification.receiver.username}", {
        'type': 'notification.send_new',
        'notification': NotificationsSerializer().serialize([notification]),
        'notifications_to_delete_id_list': notifications_to_delete_id_list,
    })

def send_notification_delete_to_channel_layer(username, notifications_to_delete_id_list):
    async_to_sync(channel_layer.group_send)(f"notifications_{username}", {
        'type': 'notification.delete',
        'notifications_to_delete_id_list': notifications_to_delete_id_list,
    })


# sending chat room message notifications to channel layer
def send_chat_message_notification_to_channel_layer(notification):
    async_to_sync(channel_layer.group_send)(f"notifications_{notification.receiver.username}", {
        'type': 'notification.new_chat_message',
        'notification': NotificationsSerializer().serialize([notification]),
    })


def send_chat_message_edit_notification_to_channel_layer(notification):
    async_to_sync(channel_layer.group_send)(f"notifications_{notification.receiver.username}", {
        'type': 'notification.edit_chat_message',
        'notification': NotificationsSerializer().serialize([notification]),
    })


def send_room_empty_notification_to_channel_layer(username, other_username):
    async_to_sync(channel_layer.group_send)(f"notifications_{username}", {
        'type': 'notification.room_empty',
        'other_username': other_username,
    })


class NotificationsSerializer(Serializer):
    """Class to serialize all kinds of notifications."""

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
            'is_read': obj.is_read,
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

        if obj.content_type.model == 'chatroommessage':
            other_user = obj.content_object.room.other_user(obj.receiver)

            dump_object.update({
                'message': {
                    'body': obj.content_object.body.text,
                    'username': obj.content_object.user.username,
                    'other_user': {
                        'username': other_user.username,
                        'image': other_user.image.url,
                    }
                },
                'room': {
                    'id': obj.content_object.room.id,
                }
            })

        if obj.action_name == 'chat_message_edit':
            last_message = obj.content_object.room.last_message
            dump_object.update({
                'last_message': {
                    'username': last_message.user.username,
                    'is_read': last_message.is_read,
                }
            })

        return dump_object