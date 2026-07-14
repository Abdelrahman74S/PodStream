import os
import drf_spectacular
import environ
from pathlib import Path
from datetime import timedelta
from boto3.s3.transfer import TransferConfig

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR.parent, '.env'))
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')


ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'config.apps.MongoDBAdminConfig',
    'config.apps.MongoDBAuthConfig',
    'config.apps.MongoDBContentTypesConfig',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'Accounts',
    'drf_spectacular',
    'podcasts',
    'interactions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'PodStream API',
    'DESCRIPTION': 'API documentation for the PodStream project.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # If using JWT (from your previous setup), this automatically links the Authorize button
    'SECURITY': [{'BearerAuth': []}],
    'COMPONENT_SPLIT_REQUEST': True,
}

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django_mongodb_backend',
        'NAME': 'podstream_db',
        'HOST': env('MONGO_URI'),
    }
}

DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"

MIGRATION_MODULES = {
    'admin': 'mongo_migrations.admin',
    'auth': 'mongo_migrations.auth',
    'contenttypes': 'mongo_migrations.contenttypes',
}

AUTH_USER_MODEL = 'Accounts.User'


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'

AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID').strip()
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY').strip()
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME').strip()
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-east-1')

if env.bool('DOCKER_ENV', default=False):
    # Inside Docker, Django connects internally to the minio container
    AWS_S3_ENDPOINT_URL = 'http://minio:9000'
else:
    # Outside Docker (local machine running python directly)
    AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL', default='http://127.0.0.1:9000')

# S3 Custom Domain: Forces generated URLs to point to localhost so the browser can load them
AWS_S3_CUSTOM_DOMAIN = f'localhost:9000/{AWS_STORAGE_BUCKET_NAME}'
AWS_S3_STYLE_URL_PATH = True 
AWS_S3_SIGNATURE_VERSION = 's3'
AWS_QUERYSTRING_AUTH = False
AWS_S3_URL_PROTOCOL = 'http:'  # Force http:// protocol instead of https:// for local development
AWS_S3_FILE_OVERWRITE = False

STATIC_URL = f'http://{AWS_S3_CUSTOM_DOMAIN}/static/'
MEDIA_URL = f'http://{AWS_S3_CUSTOM_DOMAIN}/media/'

STORAGES = {
    "default": {
        "BACKEND": "Accounts.storages.MediaStorage",
    },
    "staticfiles": {
        "BACKEND": "Accounts.storages.StaticStorage",
    },
}


AWS_S3_TRANSFER_CONFIG = TransferConfig(
    multipart_threshold=1024 * 25,   
    multipart_chunksize=1024 * 25,
    use_threads=True,
)

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY, 
    'AUTH_HEADER_TYPES': ('Bearer',),
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')  
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_PASSWORD')


# Celery Configuration
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE