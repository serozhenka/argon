from django.conf import settings
from django.contrib.contenttypes.fields import ContentType
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from django.urls import reverse

from .models import PostImage, Comment, PostLike
from .utils import clear_post_like_notifications
from notifications.models import Notification
from notifications.utils import send_notification_to_channel_layer, send_notification_delete_to_channel_layer

@receiver(post_delete, sender=PostImage)
def post_cascade_delete_image(sender, instance, *args, **kwargs):
    try:
        instance.image.delete(save=False)
    except Exception:
        pass

@receiver(post_save, sender=Comment)
def create_post_comment_notification(sender: Comment, instance: Comment, created, **kwargs):
    if created and instance.user != instance.post.user:

        notification = instance.notifications.create(
            sender=instance.user,
            receiver=instance.post.user,
            action_name="post_comment",
            message=f"commented your post",
            redirect_url=f"{settings.BASE_URL}{reverse('post:post-page', kwargs={'post_id': instance.post.id})}",
            content_type=ContentType.objects.get_for_model(instance),
        )

        send_notification_to_channel_layer(notification, [])

@receiver(pre_delete, sender=Comment)
def delete_post_comment_send_delete_notification(sender: Comment, instance: Comment, **kwargs):
    if instance.user != instance.post.user:

        notification = Notification.objects.get(
            sender=instance.user,
            receiver=instance.post.user,
            action_name="post_comment",
            object_id=instance.id,
        )
        send_notification_delete_to_channel_layer(instance.post.user.username, [notification.id])

@receiver(post_save, sender=PostLike)
def create_post_like_notification(sender: PostLike, instance: PostLike, created, **kwargs):
    if instance.user == instance.post.user:
        return

    notifications_to_delete_id_list = clear_post_like_notifications(instance, instance.user, instance.post.user)

    if instance.is_liked:
        notification = instance.notifications.create(
            sender=instance.user,
            receiver=instance.post.user,
            action_name="post_like",
            message=f"liked your post",
            redirect_url=f"{settings.BASE_URL}{reverse('post:post-page', kwargs={'post_id': instance.post.id})}",
            content_type=ContentType.objects.get_for_model(instance),
        )

        send_notification_to_channel_layer(notification, notifications_to_delete_id_list)

    elif not instance.is_liked:
        send_notification_delete_to_channel_layer(instance.post.user.username, notifications_to_delete_id_list)



