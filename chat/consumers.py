from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .constants import MsgType
from .exceptions import ClientError


class ChatConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        self.room_id = None
        super().__init__(*args, **kwargs)

    async def connect(self):
        """Called when client instantiates a handshake."""

        await self.accept()

    async def receive_json(self, content, **kwargs):
        """Called when client sends a text frame."""

        command = content.get('command')

        if command == "join":
            await self.join_room(room_id=content.get('room_id'))
        elif command == "send":
            if content.get('message'):
                await self.send_json({
                    'msg_type': MsgType.STANDARD_MESSAGE,
                    'message': content.get('message'),
                    'username': self.scope['user'].username,
                })

        print("receiving json")

    async def disconnect(self, code):
        """Called when client disconnects or connection is lost."""
        await self.close(code)

    # helper functions
    async def join_room(self, room_id):
        try:
            if not room_id:
                raise ClientError(1000, "No room id given")
        except ClientError as e:
            await self.handle_error(e)

    async def handle_error(self, e):
        """Handling incoming errors."""

        e.__dict__.update({'msg_type': MsgType.ERROR})
        await self.send_json(e.__dict__)




