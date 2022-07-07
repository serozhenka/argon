from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from typing import Union, Optional, Tuple
from django.core.paginator import Paginator

from .constants import NotificationType, NOTIFICATIONS_PAGE_SIZE
from .models import Notification
from .utils import NotificationsSerializer
from chat.exceptions import ClientError

class NotificationConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self) -> None:
        """Called when client instantiates a handshake."""
        await self.accept()
        await self.channel_layer.group_add(f"notifications_{self.scope['user'].username}", self.channel_name)

    async def receive_json(self, content, **kwargs):
        """Called when client sends a text frame."""

        command = content.get('command')

        if command == "load_notifications":
            page_number = content.get('page_number')
            notifications, new_page_number = await self.get_notifications_by_page(page_number)

            if notifications:
                await self.send_notifications_payload(notifications, new_page_number)

            if not new_page_number:
                await self.pagination_exhausted()

        elif command == "notifications_count":
            count = await self.get_unread_notifications_count()
            await self.notification_send_count(count)

        elif command == "read_notification":
            notification_id = content.get('notification_id')
            if read_notification_id := await self.set_notification_as_read(notification_id):
                await self.notification_send_read(read_notification_id)

    async def disconnect(self, code) -> None:
        """Called when client disconnects or connection is lost."""
        await self.channel_layer.group_discard(f"notifications_{self.scope['user'].username}", self.channel_name)
        await self.close(code)

    # methods to handle general notifications
    async def send_notifications_payload(self, notifications, new_page_number):
        await self.send_json({
            'msg_type': NotificationType.LOAD_NOTIFICATIONS,
            'notifications': notifications,
            'new_page_number': new_page_number,
        })

    async def notification_send_new(self, event):
        await self.send_json({
            'msg_type': NotificationType.NEW_NOTIFICATION,
            'notifications': event.get('notification'),
            'notifications_to_delete_id_list': event.get('notifications_to_delete_id_list'),
        })

    async def notification_delete(self, event):
        await self.send_json({
            'msg_type': NotificationType.DELETE_NOTIFICATION,
            'notifications_to_delete_id_list': event.get('notifications_to_delete_id_list'),
        })

    async def notification_send_count(self, count):
        await self.send_json({
            'msg_type': NotificationType.NOTIFICATIONS_COUNT,
            'count': count,
        })

    async def notification_send_read(self, notification_id):
        await self.send_json({
            'msg_type': NotificationType.READ_NOTIFICATION,
            'notification_id': notification_id,
        })

    # methods to handle chat room message notifications
    async def notification_new_chat_message(self, event):
        await self.send_json({
            'msg_type': NotificationType.NEW_CHAT_MESSAGE_NOTIFICATION,
            'notifications': event.get('notification'),
        })

    async def notification_edit_chat_message(self, event):
        await self.send_json({
            'msg_type': NotificationType.EDIT_CHAT_MESSAGE_NOTIFICATION,
            'notifications': event.get('notification'),
        })

    async def notification_room_empty(self, event):
        await self.send_json({
            'msg_type': NotificationType.ROOM_EMPTY,
            'other_username': event.get('other_username'),
        })

    @database_sync_to_async
    def get_notifications_by_page(self, page_number: Union[int, str]) -> Tuple[Optional[list], Optional[int]]:
        """
            Method to get old notifications, paginate them,
            serialize some of them based on page number. If page number does not
            exceed paginator page numbers returns Tuple(serialized_messages, next_page_number),
            else returns Tuple(None, None).
        """
        try:
            page_number = int(page_number)
        except ValueError:
            async_to_sync(self.handle_error)((ClientError(1000, "Page number is not an integer")))

        qs = Notification.objects.filter(receiver=self.scope['user']).exclude(content_type__model="chatroommessage").order_by('is_read', '-timestamp')
        paginator = Paginator(qs, NOTIFICATIONS_PAGE_SIZE)

        if page_number <= paginator.num_pages:
            serializer = NotificationsSerializer()
            serialized = serializer.serialize(paginator.page(page_number).object_list)
            new_page_number = page_number + 1 if page_number != paginator.num_pages else None
            return serialized, new_page_number

        return None, None

    async def pagination_exhausted(self):
        """Method sending pagination exhausted event to the client."""
        await self.send_json({'msg_type': NotificationType.PAGINATION_EXHAUSTED})

    @database_sync_to_async
    def get_unread_notifications_count(self) -> int:
        return Notification.objects.filter(receiver=self.scope['user'], is_read=False).exclude(content_type__model="chatroommessage").count()

    @database_sync_to_async
    def set_notification_as_read(self, notification_id) -> Optional[Union[str, int]]:
        """
            Method to set notification as read if user requesting method
            is notification receiver. If message exists returns notification id, else None.
        """

        try:
            notification = Notification.objects.get(id=notification_id)
        except Notification.DoesNotExist:
            return None

        if notification.receiver == self.scope['user']:
            notification.is_read = True
            notification.save()
            return notification_id

        return None

    async def handle_error(self, e):
        """Handling incoming errors."""
        e.__dict__.update({'msg_type': NotificationType.ERROR})
        await self.send_json(e.__dict__)


