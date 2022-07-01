from django.db import models
from django.db.models import Q
from django.conf import settings
from typing import Optional

def get_message_body_image_path(instance: 'ChatRoomMessageBody', filename: str) -> str:
    return f'chat_message_images/{str(instance.pk)}_{filename}'

class ChatRoomManager(models.Manager):

    def get_create(self, user1, user2):
        room = self.model.objects.filter(
            (Q(user1=user1) & Q(user2=user2)) |
            (Q(user1=user2) & Q(user2=user1))
        )
        if not room.exists:
            return self.model.objects.create(user1=user1, user2=user2)
        return room.first()


class ChatRoom(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user2')

    objects = ChatRoomManager()

    def __str__(self) -> str:
        return f"Chat room {self.user1.username} - {self.user2.username}"

    @property
    def group_name(self) -> str:
        return f'chatroom_{self.pk}'

    def other_user(self, user) -> Optional[settings.AUTH_USER_MODEL]:
        if user in [self.user1, self.user2]:
            return self.user1 if user == self.user2 else self.user2
        return None


class ChatRoomMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    body = models.OneToOneField('ChatRoomMessageBody', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


class ChatRoomMessageBody(models.Model):
    text = models.TextField(max_length=800)
    image = models.ImageField(upload_to=get_message_body_image_path, blank=True, null=True)
    is_edited = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Chat room message bodies'

    def __str__(self) -> str:
        return str(self.pk)
