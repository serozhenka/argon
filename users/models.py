from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

def get_profile_image_path(instance: 'Account', filename: str) -> str:
    return f'profile_images/{str(instance.pk)}_{filename}'


class AccountManager(BaseUserManager):
    """Account model manager to handle user/superuser objects creation."""

    def create_user(self, email: str, username: str, password: str, **kwargs) -> 'Account':
        """Creating basic user and returning it."""

        if not email:
            raise ValueError('User should have valid email address')
        if not username:
            raise ValueError('User should have valid username')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username.lower(), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, username: str, password: str, **kwargs) -> 'Account':
        """Creating superuser and returning it."""

        user = self.create_user(email, username, password, **kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model to use email field instead of
    username field when logging in.
    """

    email: str = models.EmailField(max_length=255, unique=True)
    username: str = models.CharField(max_length=64, unique=True, db_index=True)
    name: str = models.CharField(max_length=128, blank=True)
    bio: str = models.TextField(max_length=128, blank=True)
    image = models.ImageField(
        upload_to=get_profile_image_path,
        default=settings.DEFAULT_PROFILE_IMAGE_FILEPATH,
        null=True, blank=True
    )
    is_online: int = models.PositiveSmallIntegerField(default=0, blank=True)
    is_public: bool = models.BooleanField(default=True)
    last_activity: datetime = models.DateTimeField(null=True, blank=True)
    joined: datetime = models.DateTimeField(auto_now_add=True)

    is_active: bool = models.BooleanField(default=True)
    is_staff: bool = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = AccountManager()

    def __str__(self) -> str:
        return self.email
