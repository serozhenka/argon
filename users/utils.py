import base64
import cv2
import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage


TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"


def save_temp_profile_image_from_base64String(image_string, user):
    INCORRECT_PADDING_EXCEPTION = "Incorrect padding"

    try:
        if not os.path.exists(settings.TEMP):
            os.mkdir(settings.TEMP)

        if not os.path.exists(f"{settings.TEMP}/{str(user.id)}"):
            os.mkdir(f"{settings.TEMP}/{str(user.id)}")

        url = os.path.join(f"{settings.TEMP}/{str(user.id)}", TEMP_PROFILE_IMAGE_NAME)
        storage = FileSystemStorage(location=url)
        image = base64.b64decode(image_string)

        with storage.open("", 'wb+') as destination:
            destination.write(image)
            destination.close()

        return url

    except Exception as e:
        if str(e) == INCORRECT_PADDING_EXCEPTION:
            image_string += "=" * ((4 - len(image_string) % 4) % 4)
            return save_temp_profile_image_from_base64String(image_string, user)

    return None

def crop_image_from_url(url, x, y, width, height, max_dimension):
    img = cv2.imread(url)
    x = 0 if x < 0 else x
    y = 0 if y < 0 else y
    cropped_image = img[y:(y + height), x:(x + width)]

    if cropped_image.shape[0] > max_dimension:
        cropped_image = cv2.resize(cropped_image, (300, 300), interpolation=cv2.INTER_AREA)

    cv2.imwrite(url, cropped_image)
