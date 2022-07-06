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

    async def disconnect(self, code) -> None:
        """Called when client disconnects or connection is lost."""
        await self.close(code)

    async def send_notifications_payload(self, notifications, new_page_number):
        await self.send_json({
            'msg_type': NotificationType.LOAD_NOTIFICATIONS,
            'notifications': notifications,
            'new_page_number': new_page_number,
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

        qs = Notification.objects.filter(receiver=self.scope['user']).order_by('is_read', 'timestamp')
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

    async def handle_error(self, e):
        """Handling incoming errors."""
        e.__dict__.update({'msg_type': NotificationType.ERROR})
        await self.send_json(e.__dict__)


