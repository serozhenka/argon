from datetime import datetime
from django.db import models
from django.conf import settings

from users.models import Account

def get_post_image_path(instance: 'Post', filename: str) -> str:
    return f'post_images/{str(instance.pk)}_{filename}'


class Post(models.Model):
    """Feed post model."""
    user: Account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description: str = models.CharField(max_length=164, blank=True)
    created: datetime = models.DateTimeField(auto_now_add=True)
    is_edited: bool = models.BooleanField(default=False)


class PostImage(models.Model):
    """Like model to Post model."""
    post: Post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_post_image_path)


class PostLike(models.Model):
    """Like model to Post model."""
    user: Account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post: Post = models.ForeignKey(Post, on_delete=models.CASCADE)
    is_liked: bool = models.BooleanField(default=True)


class Comment(models.Model):
    """Comment model to Post model"""
    user: Account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post: Post = models.ForeignKey(Post, on_delete=models.CASCADE)
    description: str = models.CharField(max_length=80, blank=True)
    created: datetime = models.DateTimeField(auto_now_add=True)


class CommentLike(models.Model):
    """Like model to Comment model."""
    user: Account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment: Comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    is_liked: bool = models.BooleanField(default=True)

