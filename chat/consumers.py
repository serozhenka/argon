import asyncio

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.paginator import Paginator
from django.utils import timezone
from typing import Tuple, List, Union, Optional

from .constants import MsgType, CHAT_ROOM_MESSAGE_PAGE_SIZE
from .exceptions import ClientError
from .models import ChatRoom, ChatRoomMessage, ChatRoomMessageBody
from .utils import calculate_timestamp, ChatRoomMessageSerializer


class ChatConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        self.room, self.group_name = None, None
        super().__init__(*args, **kwargs)

    async def connect(self):
        """Called when client instantiates a handshake."""

        await self.accept()

    async def receive_json(self, content, **kwargs):
        """Called when client sends a text frame."""

        command = content.get('command')
        room_id = content.get('room_id')

        if command == "join":
            await self.join_room(room_id=room_id)

        elif command == "send":
            message = content.get('message')
            
            if message and self.room and room_id == str(self.room.id):
                asyncio.create_task(self.save_chat_room_message(message=message))
                await self.channel_layer.group_send(self.group_name, {
                    'type': 'chat.message',
                    'message': message,
                    'username': self.scope['user'].username,
                    'other_username': self.room.other_user(self.scope['user']).username,
                    'timestamp': calculate_timestamp(timezone.now()),
                })

        elif command == "load_messages":
            page_number = content.get('page_number')

            if self.room and room_id == str(self.room.id) and page_number:
                messages, new_page_number = await self.get_chat_room_messages(page_number)
                if messages:
                    await self.load_messages(messages, new_page_number)
                else:
                    await self.pagination_exhausted()

        print("receiving json")

    async def disconnect(self, code: int):
        """Called when client disconnects or connection is lost."""
        await self.leave_room(self.room.id) if self.room else None
        await self.close(code)

    async def chat_message(self, event):
        """Method to send message to the client."""
        
        await self.send_json({
            'msg_type': MsgType.STANDARD_MESSAGE,
            'message': event.get('message'),
            'username': event.get('username'),
            'other_username': event.get('other_username'),
            'timestamp': event.get('timestamp'),
        })

    async def load_messages(self, messages, new_page_number):
        """Method to send new loaded messages to the client."""

        await self.send_json({
            'msg_type': MsgType.LOAD_MESSAGES,
            'messages': messages,
            'new_page_number': new_page_number,
        })

    async def pagination_exhausted(self):
        """Method called when no more chat room messages to load."""

        await self.send_json({'msg_type': MsgType.PAGINATION_EXHAUSTED})

    # helper functions
    async def join_room(self, room_id: str) -> None:
        """Called when client send a text frame with join command."""

        try:
            room = await self.get_chat_room_or_error(room_id)
            self.room = room
            self.group_name = room.group_name
            await self.channel_layer.group_add(room.group_name, self.channel_name)
            await self.send_json({'msg_type': MsgType.JOIN, 'room_id': room.id})

        except ClientError as e:
            await self.handle_error(e)

    async def leave_room(self, room_id: str) -> None:
        """Called when client disconnects or connection is lost."""

        try:
            room = await self.get_chat_room_or_error(room_id)
            self.room, self.group_name = None, None
            await self.channel_layer.group_discard(room.group_name, self.channel_name)

        except ClientError as e:
            await self.handle_error(e)

    async def handle_error(self, e):
        """Handling incoming errors."""

        e.__dict__.update({'msg_type': MsgType.ERROR})
        await self.send_json(e.__dict__)

    @database_sync_to_async
    def get_chat_room_or_error(self, room_id: str) -> ChatRoom:
        """Method to get a chat room or raise error."""

        if not room_id:
            raise ClientError(1000, "No room id given")
        try:
            room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            raise ClientError(1000, "Room with this id does not exist")

        if self.scope['user'] not in [room.user1, room.user2]:
            raise ClientError(1000, "You have no permission to join this room")

        return room

    @database_sync_to_async
    def save_chat_room_message(self, message) -> None:
        """Method creating chat room message along with chat room message body."""

        body = ChatRoomMessageBody.objects.create(text=message)
        ChatRoomMessage.objects.create(user=self.scope['user'], room=self.room, body=body)

    @database_sync_to_async
    def get_chat_room_messages(self, page_number: Union[str, int]) -> Tuple[Optional[List], Optional[int]]:
        """
        Method to get old chat room messages and return them based on page number
        and return them encoded in json.
        """
        try:
            page_number = int(page_number)
        except ValueError:
            self.handle_error(ClientError(1000, "Page number is not an integer"))

        try:
            qs = ChatRoomMessage.objects.filter(room_id=self.room.id).select_related('body').order_by('-timestamp')
            paginator = Paginator(qs, CHAT_ROOM_MESSAGE_PAGE_SIZE)

            if page_number <= paginator.num_pages:
                serializer = ChatRoomMessageSerializer()
                serialized = serializer.serialize(paginator.page(page_number).object_list)

                return serialized, page_number + 1
            else:
                raise ClientError(1000, "Unable to access that page")

        except ClientError as e:
            self.handle_error(e)

        return None, None



    
    






