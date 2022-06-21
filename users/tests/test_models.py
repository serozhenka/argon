from PIL import Image
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from model_bakery import baker
from tempfile import NamedTemporaryFile

from users.models import Account, get_profile_image_path


class TestUserModel(TestCase):
    """Testing custom user model"""

    def setUp(self) -> None:
        self.user = baker.make(Account)

    def test_account_created(self):
        self.assertTrue(isinstance(self.user, Account))
        self.assertEqual(str(self.user), self.user.email)

    def test_default_profile_image_url(self):
        self.assertEqual(self.user.image.url, settings.MEDIA_URL + settings.DEFAULT_PROFILE_IMAGE_FILEPATH)

    def test_image_url(self):
        filename = 'test.jpg'

        with NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (1, 1))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.user.image.save(filename, ntf)

        self.user.refresh_from_db()
        self.assertEqual(self.user.image.url, settings.MEDIA_URL + get_profile_image_path(self.user, filename))
        self.user.image.delete(save=False)

    def test_default_user_is_not_superuser(self):
        self.assertFalse(self.user.is_staff, True)

    def test_invalid_email_address(self):
        user = Account(email="test", username="test", password='test')
        with self.assertRaises(ValidationError):
            user.clean_fields()

    def test_blank_email_address(self):
        user = Account(username="test", password='test')
        with self.assertRaises(ValidationError):
            user.clean_fields()
