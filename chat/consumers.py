from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from typing import Tuple, List, Union, Optional

from .constants import MsgType, CHAT_ROOM_MESSAGE_PAGE_SIZE
from .exceptions import ClientError
from .models import ChatRoom, ChatRoomMessage, ChatRoomMessageBody
from .utils import calculate_timestamp, ChatRoomMessageSerializer
from users.models import Account


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
            await self.display_loading_spinner(True)
            await self.join_room(room_id=room_id)
            await self.display_loading_spinner(False)

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
            await self.display_loading_spinner(True)

            if self.room and room_id == str(self.room.id) and page_number:
                messages, new_page_number = await self.get_chat_room_messages(page_number)
                if messages:
                    await self.load_messages(messages, new_page_number)
                else:
                    await self.pagination_exhausted()

            await self.display_loading_spinner(False)

        elif command == "delete_message":
            message_id = content.get('message_id')

            if self.room and room_id == str(self.room.id) and message_id:
                if deleted_msg_id := await self.delete_chat_room_message(message_id):
                    await self.channel_layer.group_send(self.group_name, {
                        'type': 'chat.message.delete',
                        "message_id": deleted_msg_id,
                    })

        elif command == "edit_message":
            message_id = content.get('message_id')
            text = content.get('text')

            if self.room and room_id == str(self.room.id) and message_id and text:
                edited_msg_id = await self.edit_chat_room_message(message_id, text)
                if edited_msg_id:

                    await self.channel_layer.group_send(self.group_name, {
                        'type': 'chat.message.edit',
                        'text': text,
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

    # Methods sending text frame to the client

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
            "message_id": event.get('message_id'),
        })

    async def chat_message_edit(self, event):
        """Method to send edited message id to the group."""

        await self.send_json({
            'msg_type': MsgType.EDIT_MESSAGE,
            'text': event.get('text'),
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
    def delete_chat_room_message(self, message_id) -> Optional[str]:
        """
            Method to delete chat room message.
            If found and message user is current user returns message id, else None
        """

        try:
            msg = ChatRoomMessage.objects.get(id=message_id)
        except ChatRoomMessage.DoesNotExist:
            return None

        if msg.user.username == self.scope['user'].username:
            msg.delete()
            return message_id

        return None

    @database_sync_to_async
    def edit_chat_room_message(self, message_id, text) -> Optional[str]:
        """
            Method to edit chat room message.
            If found and message user is current user returns message id, else None.
        """

        try:
            msg = ChatRoomMessage.objects.get(id=message_id)
        except ChatRoomMessage.DoesNotExist:
            return None

        if msg.user.username == self.scope['user'].username:
            msg.body.text = text
            msg.body.save()
            return message_id

        return None

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

    async def display_loading_spinner(self, display):
        await self.send_json({
            'msg_type': MsgType.DISPLAY_LOADING_SPINNER,
            'display': display,
        })


class OnlineUserStatusConsumer(AsyncJsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name: Optional[str] = None
        self.chat_rooms_usernames = Optional[list]

    async def connect(self) -> None:
        """Method to create connection when client instantiates a handshake."""

        if not self.scope['user'].is_authenticated:
            await self.disconnect(1000)
            return

        self.group_name = self.scope['user'].username
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.update_user_status("connect")
        await self.accept()

    async def disconnect(self, code) -> None:
        """Method to terminate the connection when client disconnects or connection is lost."""

        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.update_user_status('disconnect')
        await self.close(code)

    async def user_online_message(self, event) -> None:
        """Method to send online user status message to the group."""

        await self.send_json({
            'msg_type': "user_online",
            'username': event.get('username'),
            'is_online': event.get('is_online'),
        })

    @database_sync_to_async
    def update_user_status(self, status: str) -> None:
        """
        Method to update user online status and notify users
        if client connects or disconnects.
        """

        user = Account.objects.get(id=self.scope['user'].id)

        if status == "connect":
            async_to_sync(self.notify_online_status)(True) if user.is_online == 0 else None
            user.is_online += 1

        elif status == "disconnect":
            async_to_sync(self.notify_online_status)(False) if user.is_online == 1 else None
            user.is_online -= 1
        user.save()

    async def notify_online_status(self, is_online: bool) -> None:
        """
        Method to notify users, who current user have active chat room with,
        that current user online status has changed.
        """

        self.chat_rooms_usernames = await self.get_chatroom_username_list()

        for username in self.chat_rooms_usernames:
            await self.channel_layer.group_send(username, {
                'type': 'user.online.message',
                'username': self.scope['user'].username,
                'is_online': is_online,
            })

    @database_sync_to_async
    def get_chatroom_username_list(self) -> list:
        """Method to get the list of usernames who current user have active chat room with."""

        user = self.scope['user']
        usernames = []

        usernames_tuple = ChatRoom.objects.filter(
            (Q(user1=user) | Q(user2=user)),
            last_message__isnull=False
        ).values_list('user1__username', 'user2__username')

        for username1, username2 in usernames_tuple:
            usernames.append(username1 if username1 != user.username else username2)

        return usernames
