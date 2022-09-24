import os
import sys

from decouple import config
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', cast=bool)

ALLOWED_HOSTS = [
    "argon-social.herokuapp.com",
    'www.argon-social.com',
    'argon-social.com',
    'localhost',
    '127.0.0.1',
]

# Application definition

DEFAULT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

EXTERNAL_APPS = [
    'rest_framework',
    'algoliasearch_django',
    'channels',
    'storages',
    'django_celery_results',
    'djcelery_email',
    'celery_progress',
]

INTERNAL_APPS = [
    'users.apps.UsersConfig',
    'follow.apps.FollowConfig',
    'api.apps.ApiConfig',
    'post.apps.PostConfig',
    'chat.apps.ChatConfig',
    'notifications.apps.NotificationsConfig',
]

INSTALLED_APPS = DEFAULT_APPS + EXTERNAL_APPS + INTERNAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'config.middleware.LoginRequiredMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'chat.context_processors.debug_mode',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': '5432',
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files

USE_S3 = config('USE_S3', cast=bool)

if USE_S3:
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    # s3 static settings
    AWS_LOCATION = 'static'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    AWS_MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'config.storage_backends.MediaStorage'
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles/'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media/'

STATICFILES_DIRS = [BASE_DIR / 'static/', ]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.Account'

POST_IMAGE_TEMP = 'static/tmp/'
DEFAULT_PROFILE_IMAGE_FILEPATH = 'profile_images/default.png'
DEFAULT_POST_IMAGE_FILEPATH = 'post_images/'
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 10
POST_COMPRESSED_IMAGE_SIZE = 1400

if DEBUG:
    BASE_URL = "http://localhost:8000"
else:
    BASE_URL = "https://www.argon-social.com"

TEMP = os.path.join(BASE_DIR, 'media/profile_images/temp')


# Email backend configuration

EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')


# Django Rest Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}


# Algolia Search Client configuration
ALGOLIA = {
    'APPLICATION_ID': config('ALGOLIA_APPLICATION_ID'),
    'API_KEY': config('ALGOLIA_API_KEY'),
    'INDEX_PREFIX': 'argon',
}


# Redis configuration

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [config('REDIS_URL')],
        },
    },
}


CSRF_TRUSTED_ORIGINS = [
    "https://argon-social.herokuapp.com",
    "http://argon-social.herokuapp.com",
    'https://www.argon-social.com',
    'http://www.argon-social.com',
    'https://argon-social.com',
]


# Celery configuration

CELERY_BROKER_URL = config('REDIS_URL')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_RESULT_EXTENDED = True
CELERY_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

AUTH_ROUTES = ('register', 'login')
AUTH_EXEMPT_ROUTES = (
    'register', 'login',
    'password_change', 'password_change_done',
    'password_reset', 'password_reset_done', 'password_reset_confirm', 'password_reset_complete',
)
AUTH_REDIRECT = 'post:feed'
AUTH_LOGIN_ROUTE = 'account:login'
DEFAULT_REDIRECT_ROUTE = 'post:feed'
