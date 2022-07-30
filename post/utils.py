import boto3
import cv2
import numpy as np

from django.conf import settings
from django.contrib.contenttypes.fields import ContentType
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from PIL import Image

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


def get_bucket_object(image_url):
    relative_url = image_url[image_url.index(settings.AWS_S3_CUSTOM_DOMAIN) + len(settings.AWS_S3_CUSTOM_DOMAIN) + 1:]
    s3 = boto3.resource(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    bucket_object = bucket.Object(relative_url)

    return bucket_object


def read_image_from_bucket(bucket_object):
    file_stream = bucket_object.get()['Body']
    img = Image.open(file_stream)
    return np.array(img), img.size, img.info.get('exif')


def compress_image(image_array, extension):
    # compress image
    if extension in ["jpg", "jpeg"]:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 25]
    else:
        encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), 7]

    encoded_img = cv2.imencode(f".{extension}", image_array, encode_param)[1]
    decoded_img = cv2.imdecode(encoded_img, 1)

    # resize image
    width, height = decoded_img.shape[1], decoded_img.shape[0]
    if max(width, height) > 1400:
        scale_percent = (1400 / max(width, height)) * 100  # percent of original size

        resize_width = int(width * scale_percent / 100)
        resize_height = int(height * scale_percent / 100)
        dim = (resize_width, resize_height)

        decoded_img = cv2.resize(decoded_img, dim, interpolation=cv2.INTER_AREA)

    return decoded_img

def write_image_to_bucket(bucket_object, image_array, extension, exif):
    if extension == "jpg":
        extension = "jpeg"
    file_stream = BytesIO()
    img = Image.fromarray(image_array)
    img.save(file_stream, exif=exif if exif else b'', format=extension)
    bucket_object.put(Body=file_stream.getvalue(), ContentType=f"image/{extension}")


def compress_image_from_tempfile(img_tmp):
    filename = img_tmp.name
    ext = filename.split('.')[-1].lower()
    if ext == "jpg":
        ext = "jpeg"

    img = Image.open(img_tmp)

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