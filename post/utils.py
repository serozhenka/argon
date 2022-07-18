import boto3
import cv2
import numpy as np

from django.conf import settings
from django.contrib.contenttypes.fields import ContentType
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
    if extension in ["jpg", "jpeg"]:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 25]
    else:
        encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), 7]

    encoded_img = cv2.imencode(f".{extension}", image_array, encode_param)[1]
    decoded_img = cv2.imdecode(encoded_img, 1)
    return decoded_img

def write_image_to_bucket(bucket_object, image_array, extension, exif):
    if extension == "jpg":
        extension = "jpeg"
    file_stream = BytesIO()
    img = Image.fromarray(image_array)
    img.save(file_stream, exif=exif if exif else b'', format=extension)
    bucket_object.put(Body=file_stream.getvalue(), ContentType=f"image/{extension}")