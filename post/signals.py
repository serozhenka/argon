from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import PostImage

@receiver(post_delete, sender=PostImage)
def post_cascade_delete_image(sender, instance, *args, **kwargs):
    try:
        instance.image.delete(save=False)
    except Exception:
        pass
