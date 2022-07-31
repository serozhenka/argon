from celery import shared_task
from django.apps import apps
from io import BytesIO
from PIL import Image

from .utils import compress_pil_image, decode_image_from_base64_string

@shared_task
def process_new_post_image(b64image, filename, post_id, img_order):
    """
    Decodes image form base64 string.
    Compresses and resizes it.
    Creates new PostImage model instance.
    """
    pil_image = Image.open(BytesIO(decode_image_from_base64_string(b64image)))
    image_file = compress_pil_image(pil_image, filename)

    Post = apps.get_model(app_label='post', model_name='post')
    PostImage = apps.get_model(app_label='post', model_name='postimage')
    post = Post.objects.get(id=post_id)
    PostImage.objects.create(post=post, image=image_file, order=img_order)

@shared_task
def post_make_posted(post_id):
    """
    Updates Poss instance is_posted field
    to make sure user does not access post before all the
    images has been fully processed.
    """
    Post = apps.get_model(app_label='post', model_name='post')
    Post.objects.filter(id=post_id).update(is_posted=True)
