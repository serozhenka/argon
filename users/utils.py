import os
import base64

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from typing import Optional

from .models import Account

TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"

def user_exists_and_is_account_owner(request, username) -> (Optional[Account], bool):
    try:
        account = Account.objects.get(username=username)
    except Account.DoesNotExist:
        return None, False
    if account != request.user:
        return None, False

    return account, True

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