from django.db import models
from django.conf import settings

def get_message_body_image_path(instance: 'ChatRoomMessageBody', filename: str) -> str:
    return f'chat_message_images/{str(instance.pk)}_{filename}'


class ChatRoom(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user2')

    def __str__(self):
        return f"Chat room {self.user1.username} - {self.user2.username}"

    @property
    def group_name(self):
        return f'chatroom_{self.pk}'


class ChatRoomMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    body = models.OneToOneField('ChatRoomMessageBody')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


class ChatRoomMessageBody(models.Model):
    text = models.TextField(max_length=800)
    image = models.ImageField(upload_to=get_message_body_image_path, blank=True, null=True)
    is_edited = models.BooleanField(default=False)
