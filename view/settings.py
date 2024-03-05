"""
Django settings for view project.

Generated by 'django-admin startproject' using Django 4.2.10.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path
from boto3 import *
from dotenv import load_dotenv  # for python-dotenv method
load_dotenv()  # for python-dotenv method


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = os.environ.get('SECRET_KEY')
SECRET_KEY = 'django-insecure-kfb=+rej@*g)fb58b_&!o8vg4&!gn&6o6-(749bqdd@b+up9_0'

# # The `DYNO` env var is set on Heroku CI, but it's not a real Heroku app, so we have to
# # also explicitly exclude CI:
# # https://devcenter.heroku.com/articles/heroku-ci#immutable-environment-variables
# IS_HEROKU_APP = "DYNO" in os.environ and not "CI" in os.environ

# # SECURITY WARNING: don't run with debug turned on in production!
# if not IS_HEROKU_APP:
#     DEBUG = True
DEBUG = False

# # On Heroku, it's safe to use a wildcard for `ALLOWED_HOSTS``, since the Heroku router performs
# # validation of the Host header in the incoming HTTP request. On other platforms you may need
# # to list the expected hostnames explicitly to prevent HTTP Host header attacks. See:
# # https://docs.djangoproject.com/en/5.0/ref/settings/#std-setting-ALLOWED_HOSTS
# if IS_HEROKU_APP:
#     ALLOWED_HOSTS = ["*"]
# else:
#     ALLOWED_HOSTS = []

ALLOWED_HOSTS = ['127.0.0.1', 'view2-vd8vm.ondigitalocean.app',
                 'localhost', '127.0.0.1', '0.0.0.0']
# CSRF_TRUSTED_ORIGINS = ['https://*.herokuapp.com/']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'lidar.apps.LidarConfig',
    'storages',
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

ROOT_URLCONF = 'view.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'view.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases


DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lidar',
        'USER': 'view2user',
        'PASSWORD': 'scopesantosvolpe2023',
        'HOST': 'db-postgresql-nyc3-27521-do-user-15891455-0.c.db.ondigitalocean.com',
        'PORT': '25060',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# STATIC_URL = 'static/'


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'lidar/static/')

# print(f"Bucket type is {type(os.environ.get('AWS_STORAGE_BUCKET_NAME'))}")
AWS_S3_ACCESS_KEY_ID = os.environ.get('AWS_S3_ACCESS_KEY_ID')
AWS_S3_SECRET_ACCESS_KEY = os.environ.get('AWS_S3_SECRET_ACCESS_KEY')

# AWS_STORAGE_BUCKET_NAME = 'vehicle-scans'
# AWS_S3_REGION_NAME = os.environ.get('AWS_REGION_NAME')
# AWS_DEFAULT_ACL = os.environ.get('AWS_DEFAULT_ACL')
# AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')

AWS_STORAGE_BUCKET_NAME = 'vehicle-scans'
AWS_DEFAULT_ACL = None
AWS_S3_REGION_NAME = 'us-east-2'
AWS_S3_ENDPOINT_URL = 'https://vehicle-scans.nyc3.digitaloceanspaces.com'


AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400'
}

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'lidar/static'),
# ]

# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'view.storage_backends.StaticStorage'
AWS_STATIC_LOCATION = 'static'
STATIC_URL = '{}/{}/'.format(AWS_S3_ENDPOINT_URL, AWS_STATIC_LOCATION)
STATIC_ROOT = 'lidar/static/'


MEDIA_FILE_STORAGE = 'view.storage_backends.MediaStorage'
AWS_MEDIA_LOCATION = 'media'
PUBLIC_MEDIA_LOCATION = 'media/public'
MEDIA_ROOT = 'lidar/media/'
MEDIA_URL = '{}/{}/'.format(AWS_S3_ENDPOINT_URL, AWS_MEDIA_LOCATION)

# OLD Procfile CONTENT
# web: python3 manage.py runserver 0.0.0.0:"$PORT"
