from datetime import datetime
from django.db import models
from django.conf import settings

from users.models import Account

def get_post_image_path(instance: 'PostImage', filename: str) -> str:
    return f'post_images/{str(instance.post_id)}_{filename}'


class Post(models.Model):
    """Feed post model."""
    user: Account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description: str = models.CharField(max_length=164, blank=True)
    created: datetime = models.DateTimeField(auto_now_add=True)
    is_edited: bool = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class PostImage(models.Model):
    """Like model to Post model."""
    post: Post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_post_image_path)

    def __str__(self):
        return f"{self.post.user.username} post image"


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

    def __str__(self):
        return f'{self.id} by {self.user.username}'


class CommentLike(models.Model):
    """Like model to Comment model."""
    user: Account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment: Comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    is_liked: bool = models.BooleanField(default=True)

