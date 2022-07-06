from django.conf import settings
from django.contrib.contenttypes.fields import ContentType
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse

from .models import PostImage, Comment, PostLike

@receiver(post_delete, sender=PostImage)
def post_cascade_delete_image(sender, instance, *args, **kwargs):
    try:
        instance.image.delete(save=False)
    except Exception:
        pass

@receiver(post_save, sender=Comment)
def create_post_comment_notification(sender: Comment, instance: Comment, created, **kwargs):
    if created and instance.user != instance.post.user:
        instance.notifications.create(
            sender=instance.user,
            receiver=instance.post.user,
            action_name="post_comment",
            message=f"commented your post",
            redirect_url=f"{settings.BASE_URL}{reverse('post:post-page', kwargs={'post_id': instance.post.id})}",
            content_type=ContentType.objects.get_for_model(instance),
        )

@receiver(post_save, sender=PostLike)
def create_post_like_notification(sender: PostLike, instance: PostLike, created, **kwargs):
    if instance.is_liked and instance.user != instance.post.user:
        instance.notifications.create(
            sender=instance.user,
            receiver=instance.post.user,
            action_name="post_like",
            message=f"liked your post",
            redirect_url=f"{settings.BASE_URL}{reverse('post:post-page', kwargs={'post_id': instance.post.id})}",
            content_type=ContentType.objects.get_for_model(instance),
        )

