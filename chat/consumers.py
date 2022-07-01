from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from typing import Optional

from .constants import MsgType
from .exceptions import ClientError
from .models import ChatRoom


class ChatConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        self.room_id = None
        self.group_name = None
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
            if message and room_id == self.room_id:
                await self.channel_layer.group_send(self.group_name, {
                    'type': 'chat.message',
                    'message': message,
                    'username': self.scope['user'].username,
                })

        print("receiving json")

    async def disconnect(self, code: int):
        """Called when client disconnects or connection is lost."""
        await self.leave_room(self.room_id) if self.room_id else None
        await self.close(code)

    async def chat_message(self, event):
        await self.send_json({
            'msg_type': MsgType.STANDARD_MESSAGE,
            'message': event.get('message'),
            'username': event.get('username'),
        })

    # helper functions
    async def join_room(self, room_id: str):
        """Called when client send a text frame with join command."""

        try:
            room = await self.get_chat_room_or_error(room_id)
            self.room_id = str(room.id)
            self.group_name = room.group_name
            await self.channel_layer.group_add(room.group_name, self.channel_name)
            await self.send_json({'msg_type': MsgType.JOIN, 'room_id': room.id})

        except ClientError as e:
            await self.handle_error(e)

    async def leave_room(self, room_id):
        """Called when client disconnects or connection is lost."""

        try:
            room = await self.get_chat_room_or_error(room_id)
            self.room_id, self.group_name = None, None
            await self.channel_layer.group_discard(room.group_name, self.channel_name)

        except ClientError as e:
            await self.handle_error(e)

    async def handle_error(self, e):
        """Handling incoming errors."""

        e.__dict__.update({'msg_type': MsgType.ERROR})
        await self.send_json(e.__dict__)

    @database_sync_to_async
    def get_chat_room_or_error(self, room_id: str) -> Optional[ChatRoom]:
        if not room_id:
            raise ClientError(1000, "No room id given")
        try:
            room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            raise ClientError(1000, "Room with this id does not exist")

        if self.scope['user'] not in [room.user1, room.user2]:
            raise ClientError(1000, "You have no permission to join this room")

        return room






