from PIL import Image
from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase
from model_bakery import baker

from chat.models import ChatRoom, ChatRoomMessage, ChatRoomMessageBody
from users.models import Account
from notifications.models import Notification


class TestChatRoomModel(TestCase):
    """Testing chat room model."""

    def setUp(self) -> None:
        self.user = baker.make(Account)
        self.other_user = baker.make(Account)

        self.chat_room = ChatRoom.objects.create(user1=self.user, user2=self.other_user)

    def test_chat_room_model_created(self):
        self.assertTrue(isinstance(self.chat_room, ChatRoom))
        self.assertEqual(str(self.chat_room), f"Chat room {self.user.username} - {self.other_user.username}")

    def test_chat_room_group_name_method(self):
        self.assertEqual(self.chat_room.group_name, f'chatroom_{self.chat_room.pk}')

    def test_chat_room_other_user_method(self):
        self.assertEqual(self.chat_room.other_user(self.user), self.other_user)
        self.assertEqual(self.chat_room.other_user(self.other_user), self.user)


class TestChatRoomMessageModel(TestCase):
    """Testing chat room message model."""

    def setUp(self) -> None:
        self.user = baker.make(Account)
        self.other_user = baker.make(Account)
        self.chat_room = ChatRoom.objects.create(user1=self.user, user2=self.other_user)

        self.text = "hello world"
        self.chat_room_message_body = ChatRoomMessageBody.objects.create(text=self.text)

        self.chat_room_message = ChatRoomMessage.objects.create(
            user=self.user,
            room=self.chat_room,
            body=self.chat_room_message_body,
        )

    def test_chat_room_message_body_created(self):
        self.assertTrue(isinstance(self.chat_room_message_body, ChatRoomMessageBody))
        self.assertEqual(str(self.chat_room_message_body), str(self.chat_room_message_body.pk))

    def test_chat_room_message_created(self):
        self.assertTrue(isinstance(self.chat_room_message, ChatRoomMessage))
        self.assertEqual(str(self.chat_room_message), str(self.chat_room_message.id))
        self.assertEqual(self.chat_room_message.user, self.user)
        self.assertEqual(self.chat_room_message.room, self.chat_room)
        self.assertEqual(self.chat_room_message.body, self.chat_room_message_body)

    def test_chat_room_last_message_set(self):
        self.assertEqual(self.chat_room_message.room.last_message, self.chat_room_message)

    def test_chat_room_new_message_notification_created(self):
        for user in [self.chat_room_message.user, self.chat_room_message.room.other_user(self.chat_room_message.user)]:
            self.assertTrue(
                Notification.objects.filter(
                    sender=self.chat_room_message.user,
                    receiver=user,
                    action_name="chat_message_new"
                ).exists()
            )

    def test_edit_chat_room_last_message_body(self):
        self.chat_room_message_body.text = "new text"
        self.chat_room_message_body.save()

        for user in [self.chat_room_message.user, self.chat_room_message.room.other_user(self.chat_room_message.user)]:
            self.assertFalse(
                Notification.objects.filter(
                    sender=self.chat_room_message.user,
                    receiver=user,
                    action_name="chat_message_new"
                ).exists()
            )

            self.assertTrue(
                Notification.objects.filter(
                    sender=self.chat_room_message.user,
                    receiver=user,
                    action_name="chat_message_edit"
                ).exists()
            )

    def test_delete_chat_room_last_message(self):
        chat_room_message_body2 = ChatRoomMessageBody.objects.create(text=self.text)
        chat_room_message2 = ChatRoomMessage.objects.create(
            user=self.user,
            room=self.chat_room,
            body=chat_room_message_body2,
        )

        self.assertEqual(self.chat_room_message.room.last_message, chat_room_message2)
        chat_room_message2.delete()
        self.assertEqual(self.chat_room_message.room.last_message, self.chat_room_message)

        for user in [self.chat_room_message.user, self.chat_room_message.room.other_user(self.chat_room_message.user)]:
            self.assertTrue(
                Notification.objects.filter(
                    sender=self.chat_room_message.user,
                    receiver=user,
                    action_name="chat_message_edit"
                ).exists()
            )

    def test_chat_room_empty(self):
        self.chat_room_message.delete()
        self.assertEqual(self.chat_room.last_message, None)

        for user in [self.chat_room_message.user, self.chat_room_message.room.other_user(self.chat_room_message.user)]:
            self.assertFalse(
                Notification.objects.filter(
                    sender=self.chat_room_message.user,
                    receiver=user,
                    action_name="chat_message_edit"
                ).exists()
            )




















