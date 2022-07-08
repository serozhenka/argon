from django.conf import settings
from django.contrib.contenttypes.fields import ContentType

from .models import PostLike, Post
from notifications.models import Notification

def is_post_liked_by_user(user, post):
    try:
        return PostLike.objects.get(
            user=user,
            post=post,
        ).is_liked
    except PostLike.DoesNotExist:
        return False

def private_account_action_permission(user, post_user):
    if (
        not post_user.is_public and
        not user.following.is_following(post_user) and
        not user == post_user
    ):
        return False
    return True

def clear_post_like_notifications(post_like: PostLike, sender: settings.AUTH_USER_MODEL, receiver: settings.AUTH_USER_MODEL) -> list:
    notifications_to_delete = Notification.objects.filter(
        sender=sender,
        receiver=receiver,
        action_name="post_like",
        content_type=ContentType.objects.get_for_model(post_like),
        object_id=post_like.id,
    )
    notifications_to_delete_id_list = list(notifications_to_delete.values_list('id', flat=True))
    notifications_to_delete.delete()

    return notifications_to_delete_id_list