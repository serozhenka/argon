from datetime import datetime, timedelta
from django.db import models
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils import timezone
from django.utils.dateparse import parse_datetime

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

    @property
    def likes_count(self):
        return PostLike.objects.filter(post=self, is_liked=True).count()

    @property
    def timestamp(self):
        if self.created > timezone.now() - timedelta(1):
            return str(naturaltime(self.created))
        return f"{self.created.strftime('%d %b, %Y')}"


class PostImage(models.Model):
    """Like model to Post model."""
    post: Post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_images')
    image = models.ImageField(upload_to=get_post_image_path)
    order: int = models.PositiveSmallIntegerField(default=0)

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

    @property
    def likes_count(self):
        return CommentLike.objects.filter(comment=self, is_liked=True).count()

    @property
    def timestamp(self):
        return str(naturaltime(self.created))


class CommentLike(models.Model):
    """Like model to Comment model."""
    user: Account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment: Comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    is_liked: bool = models.BooleanField(default=True)

