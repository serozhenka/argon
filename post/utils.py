import base64
import boto3
import cv2
import numpy as np
import secrets

from django.conf import settings
from django.contrib.contenttypes.fields import ContentType
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from PIL import Image


from .models import PostLike
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


def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )


def get_s3_resource():
    return boto3.resource(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )


def get_image_ext(filename):
    ext = filename.split('.')[-1].lower()
    ext = "jpeg" if ext == "jpg" else ext
    return ext


def compress_pil_image(img, filename):
    """
        Resizes* and compresses PIL image.
        Returns InMemoryUploadedFile instance which
        can be then passed to models.ImageField.

        * - if dimensions are to wide (high)
    """
    ext = get_image_ext(filename)
    exif = img.info.get('exif')
    width, height = img.size

    if height / width > 1.5:  # 3 / 2
        img = img.crop((0, int(height / 2 - 0.75 * width), width, int(height / 2 + 0.75 * width)))
    elif height / width < 0.67:  # 2 / 3
        img = img.crop((int(width / 2 - 0.75 * height), 0, int(width / 2 + 0.75 * height), height))

    width, height = img.size

    if max(width, height) > settings.POST_COMPRESSED_IMAGE_SIZE:
        scale_percent = (settings.POST_COMPRESSED_IMAGE_SIZE / max(width, height)) * 100  # percent of original size
        new_dimensions = (int(d * scale_percent / 100) for d in (width, height))
        img = img.resize(new_dimensions, Image.ANTIALIAS)

    out = BytesIO()
    img.save(out, format=ext, exif=exif if exif else b'', optimize=True)

    return InMemoryUploadedFile(ContentFile(out.getvalue()), None, filename, 'image/jpeg', img.tell, None)


def get_image_key(pkey):
    return f'{settings.POST_IMAGE_TEMP}{pkey}'


def put_new_image_to_s3(s3_client, image, pkeys):
    extension = get_image_ext(image.name)
    pkey = f'{secrets.token_hex(8)}_{image.name}'
    key = get_image_key(pkey)

    s3_client.put_object(
        Body=image.read(),
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=key,
        ContentType=f"image/{extension}",
    )
    pkeys.append(pkey)


def bucket_image_to_pil(s3_resource, pkey):
    key = get_image_key(pkey)
    bucket = s3_resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    bucket_object = bucket.Object(key)

    return Image.open(bucket_object.get()['Body'])


def bucket_delete_object(s3_resource, pkey):
    s3_resource.Object(settings.AWS_STORAGE_BUCKET_NAME, pkey).delete()


# def encode_image_to_base64_string(image):
#     return base64.b64encode(image).decode("utf-8")
#
# def decode_image_from_base64_string(base64str):
#     return base64.b64decode(base64str.encode("utf-8"))

# def tempfile_image_to_pil(img_tmp):
#     """
#     Converts tempfile image from POST request to PIL Image.
#     Accepts tempfile image. Returns tuple - (PIL image, filename, extension)
#     """
#     filename = img_tmp.name
#     return Image.open(img_tmp), filename, get_image_ext(filename)
