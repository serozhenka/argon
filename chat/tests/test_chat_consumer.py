from channels.testing import WebsocketCommunicator
from django.test import TestCase
from model_bakery import baker

from chat.models import ChatRoom
from config.asgi import application
from users.models import Account


class TestChatConsumer(TestCase):

    def setUp(self) -> None:
        self.user1 = baker.make(Account)
        self.user2 = baker.make(Account)
        self.room = ChatRoom.objects.create(user1=self.user1, user2=self.user2)

    async def test_communicator_connects(self):
        communicator = WebsocketCommunicator(application, f"chat/{self.room.id}/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()
