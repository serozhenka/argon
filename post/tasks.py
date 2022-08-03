from celery import shared_task
from celery_progress.backend import ProgressRecorder
from django.apps import apps

from .models import PostCreateTask
from .utils import (
    compress_pil_image,
    get_s3_resource,
    bucket_image_to_pil,
    bucket_delete_object,
    get_image_key,
)


@shared_task(bind=True)
def process_new_post_images(self, pkeys, post_id):
    """
        Arguments:
            - filename: tuple[tuple[absolute_url, relative_url]]
            - post_id: int
        Task to compress image on the background and then remove them
    """
    progress_recorder = ProgressRecorder(self)
    s3_resource = get_s3_resource()

    for i in range(len(pkeys)):
        pil_image = bucket_image_to_pil(s3_resource, pkeys[i])
        PostImage = apps.get_model(app_label='post', model_name='postimage')
        PostImage.objects.create(
            post_id=post_id,
            image=compress_pil_image(pil_image, pkeys[i]),
            order=i
        )
        progress_recorder.set_progress((i + 1) / len(pkeys) * 100, 100)

        try:
            bucket_delete_object(s3_resource, get_image_key(pkeys[i]))
        except Exception:
            pass

        del pil_image, PostImage

    PostCreateTask.objects.filter(task_id=self.request.id).delete()
    return self.request.id


@shared_task
def post_make_posted(post_id):
    """
        Updates Post instance is_posted field
        to make sure user does not access post before all the
        images has been fully processed.
    """
    Post = apps.get_model(app_label='post', model_name='post')
    Post.objects.filter(id=post_id).update(is_posted=True)


# @shared_task
# def process_new_post_image(b64image, filename, post_id, img_order):
#     """
#     Decodes image form base64 string.
#     Compresses and resizes it.
#     Creates new PostImage model instance.
#     """
#     pil_image = Image.open(BytesIO(decode_image_from_base64_string(b64image)))
#
#     PostImage = apps.get_model(app_label='post', model_name='postimage')
#     PostImage.objects.create(post_id=post_id, image=compress_pil_image(pil_image, filename), order=img_order)
#
#     del pil_image, PostImage


# @shared_task
# def process_new_post_images(filenames, post_id):
#     """
#         Arguments:
#             - filename: tuple[tuple[absolute_url, relative_url]]
#             - post_id: int
#         Task to compress image on the background and then remove them
#     """
#
#     for i in range(len(filenames)):
#         pil_image = Image.open(filenames[i][0])
#         PostImage = apps.get_model(app_label='post', model_name='postimage')
#         PostImage.objects.create(
#             post_id=post_id,
#             image=compress_pil_image(pil_image, filenames[i][1]),
#             order=i
#         )
#
#         os.remove(filenames[i][0])
#         del pil_image, PostImage
