from .models import PostLike

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
        not user.is_public and
        not post_user.following.is_following(user) and
        not user == post_user
    ):
        return False
    return True