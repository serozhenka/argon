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
        self.room: Optional[ChatRoom] = None
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
            
            if message and self.room and room_id == str(self.room.id):
                created_message = await self.save_chat_room_message(text=message)

                await self.channel_layer.group_send(self.group_name, {
                    'type': 'chat.message',
                    'message': message,
                    'username': self.scope['user'].username,
                    'other_username': self.room.other_user(self.scope['user']).username,
                    'timestamp': calculate_timestamp(timezone.now()),
                    'is_read': False,
                    'id': str(created_message.id),
                })

        elif command == "load_messages":
            page_number = content.get('page_number')

            if self.room and room_id == str(self.room.id) and page_number:
                messages, new_page_number = await self.get_chat_room_messages(page_number)
                if messages:
                    await self.load_messages(messages, new_page_number)
                else:
                    await self.pagination_exhausted()

        elif command == "delete_message":
            message_id = content.get('message_id')

            if self.room and room_id == str(self.room.id) and message_id:
                deleted_msg_id, is_last_message = await self.delete_chat_room_message(message_id)
                if deleted_msg_id:
                    other_username = self.room.other_user(self.scope['user']).username
                    last_message = await self.get_chat_room_last_message(room_id)

                    await self.channel_layer.group_send(self.group_name, {
                        'type': 'chat.message.delete',
                        'is_last_message': is_last_message,
                        'last_message': last_message,
                        'other_username': other_username,
                        "message_id": deleted_msg_id,
                    })

        elif command == "edit_message":
            message_id = content.get('message_id')
            text = content.get('text')

            if self.room and room_id == str(self.room.id) and message_id and text:
                edited_msg_id, is_last_message = await self.edit_chat_room_message(message_id, text)
                if edited_msg_id:

                    await self.channel_layer.group_send(self.group_name, {
                        'type': 'chat.message.edit',
                        'text': text,
                        'is_last_message': is_last_message,
                        'other_username': self.room.other_user(self.scope['user']).username,
                        "message_id": edited_msg_id,
                    })

        elif command == "set_message_read":
            message_id = content.get('message_id')

            if self.room and room_id == str(self.room.id) and message_id:
                if marked_message_id := await self.set_message_as_read(message_id):

                    await self.channel_layer.group_send(self.group_name, {
                        'type': 'chat.message.read',
                        "message_id": marked_message_id,
                    })

    async def disconnect(self, code: int):
        """Called when client disconnects or connection is lost."""
        await self.leave_room(str(self.room.id)) if self.room else None
        await self.close(code)

    # Functions sending text frame to the client

    async def chat_message(self, event):
        """Method to send message to the group."""
        
        await self.send_json({
            'msg_type': MsgType.STANDARD_MESSAGE,
            'message': event.get('message'),
            'username': event.get('username'),
            'other_username': event.get('other_username'),
            'timestamp': event.get('timestamp'),
            'is_read': event.get('is_read'),
            'id': event.get('id'),
        })

    async def chat_message_read(self, event):
        """Method to send read message id to the group."""

        await self.send_json({
            'msg_type': MsgType.SET_MESSAGE_READ,
            "message_id": event.get('message_id'),
        })

    async def chat_message_delete(self, event):
        """Method to send delete message id to the group."""

        await self.send_json({
            'msg_type': MsgType.DELETE_MESSAGE,
            'is_last_message': event.get('is_last_message'),
            'last_message': event.get('last_message'),
            'other_username': event.get('other_username'),
            "message_id": event.get('message_id'),
        })

    async def chat_message_edit(self, event):
        """Method to send edited message id to the group."""

        await self.send_json({
            'msg_type': MsgType.EDIT_MESSAGE,
            'text': event.get('text'),
            'is_last_message': event.get('is_last_message'),
            'other_username': event.get('other_username'),
            "message_id": event.get('message_id'),
        })

    async def load_messages(self, messages, new_page_number):
        """Method to send new loaded messages to the client."""

        await self.send_json({
            'msg_type': MsgType.LOAD_MESSAGES,
            'messages': messages,
            'new_page_number': new_page_number,
        })

    # End of functions sending text frame to the client

    # Functions called when user joins a chat room

    async def join_room(self, room_id: str) -> None:
        """Called when client send a text frame with join command."""

        try:
            room: ChatRoom = await self.get_chat_room_or_error(room_id)
            self.room: ChatRoom = room
            self.group_name = room.group_name
            first_unread_message = await self.get_first_unread_message(self.room)

            await self.channel_layer.group_add(room.group_name, self.channel_name)
            await self.send_json({
                'msg_type': MsgType.JOIN,
                'room_id': room.id,
                'first_unread_message': first_unread_message,
            })

        except ClientError as e:
            await self.handle_error(e)

    @database_sync_to_async
    def get_first_unread_message(self, room: ChatRoom):
        """
        Method to get first unread message, serialize it if exists and return it.
        If message does not exist returns None.
        """

        unread_messages = room.chatroommessage_set.filter(is_read=False).order_by('timestamp')
        if unread_messages.exists():
            serializer = ChatRoomMessageSerializer()
            return serializer.serialize([unread_messages.first()])
        return None

    # End of functions called when user joins a chat room

    async def leave_room(self, room_id: str) -> None:
        """Method called when client disconnects or connection is lost."""

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
    def save_chat_room_message(self, text) -> ChatRoomMessage:
        """Method creating chat room message along with chat room message body."""

        body = ChatRoomMessageBody.objects.create(text=text)
        message = ChatRoomMessage.objects.create(user=self.scope['user'], room=self.room, body=body)
        return message

    @database_sync_to_async
    def get_chat_room_messages(self, page_number: Union[str, int]) -> Tuple[Optional[List], Optional[int]]:
        """
            Method to get old chat room messages, paginate them,
            serialize some of them based on page number. If page number does not
            exceed paginator page numbers returns Tuple(serialized_messages, next_page_number),
            else returns Tuple(None, None).
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

    async def pagination_exhausted(self):
        """Method sending pagination exhausted event to the client."""
        await self.send_json({'msg_type': MsgType.PAGINATION_EXHAUSTED})

    @database_sync_to_async
    def delete_chat_room_message(self, message_id) -> Tuple[Optional[str], Optional[bool]]:
        """
            Method to delete chat room message.
            If found and message user is current user returns Tuple(message id, is_last_message), \
            else Tuple(None, Optional[bool]).
        """

        try:
            msg = ChatRoomMessage.objects.get(id=message_id)
        except ChatRoomMessage.DoesNotExist:
            return None, None

        is_last_message = msg.room.last_message == msg

        if msg.user.username == self.scope['user'].username:
            msg.delete()
            return message_id, is_last_message

        return None, is_last_message

    @database_sync_to_async
    def edit_chat_room_message(self, message_id, text) -> Tuple[Optional[str], Optional[bool]]:
        """
            Method to edit chat room message.
            If found and message user is current user returns Tuple(message id, is_last_message),
            else Tuple(None, Optional[bool]).
        """

        try:
            msg = ChatRoomMessage.objects.get(id=message_id)
        except ChatRoomMessage.DoesNotExist:
            return None, None

        is_last_message = msg.room.last_message == msg

        if msg.user.username == self.scope['user'].username:
            msg.body.text = text
            msg.body.save()
            return message_id, is_last_message

        return None, is_last_message

    @database_sync_to_async
    def set_message_as_read(self, message_id) -> Optional[str]:
        """
            Method to set message as read if user requesting method
            is not current user (user can not mark themselves message as read).
            If message exists returns message id, else None.
        """

        try:
            message = ChatRoomMessage.objects.get(id=message_id)
        except ChatRoomMessage.DoesNotExist:
            return None

        if message.user.username != self.scope['user'].username:
            message.is_read = True
            message.save()
            return message_id

        return None

    @database_sync_to_async
    def get_chat_room_last_message(self, room_id):
        """
        Method to get last message, serialize it if exists and return it.
        If message does not exist returns None.
        """
        room = ChatRoom.objects.get(id=room_id)
        if room.last_message:
            serializer = ChatRoomMessageSerializer()
            return serializer.serialize([room.last_message])
        return None



    
    






