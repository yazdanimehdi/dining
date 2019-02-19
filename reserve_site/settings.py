"""
Django settings for reserve_site project.

Generated by 'django-admin startproject' using Django 2.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from datetime import timedelta

from celery.schedules import crontab

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^(*nwl^zk-n6v5q5u_6zua^3n&sf%j$z^p8ck7fus=fqa1^k46'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dining',
    'order',
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

CELERY_BROKER_URL = "amqp://localhost"

CELERY_TIMEZONE = "Asia/Tehran"

CELERY_BEAT_SCHEDULE = {
    'sharif_reserve_get': {
        'task': 'dining.tasks.sharif_get_reserved_food.get_reserved_sharif',
        'schedule': crontab(hour=6, minute=00, day_of_week='sat,tue'),
    },
    'bot_reserve_announcement_task': {
        'task': 'dining.tasks.reserve_announcement.reserve_announcement',
        'schedule': crontab(hour=9, minute=00),
    },
    'bot_credit_announcement_task': {
        'task': 'dining.tasks.credit_announcement.credit_announcement',
        'schedule': crontab(hour=19, minute=00, day_of_week=2),
    },
    'bot_credit_insufficient_task': {
        'task': 'dining.tasks.credit_insufficient.credit_insufficient',
        'schedule': crontab(hour=19, minute=15, day_of_week=2),
    },
    'sharif_reserve_task': {
        'task': 'dining.tasks.reservation_sharif.reserve_function',
        'schedule': crontab(hour=12, minute=00, day_of_week=3),
    },
    'tehran_reserve_task': {
        'task': 'dining.tasks.tehran_reserve_function.tehran_reserve_function',
        'schedule': crontab(hour=12, minute=00, day_of_week=2),
    },
    'samadv1_reserve_task': {
        'task': 'dining.tasks.samadv1.samadv1_reserve_function',
        'schedule': crontab(hour=19, minute=20, day_of_week=2),
    },
    'yas_reserve_task': {
        'task': 'dining.tasks.reservation_yas.reservation_yas',
        'schedule': crontab(hour=11, minute=00, day_of_week=3),
    },

}


ROOT_URLCONF = 'reserve_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'reserve_site.wsgi.application'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'MR.Zorro Admin <info@mrzoro.ir>'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'diningdb',
        'USER': 'admin',
        'PASSWORD': '99&3M+p`gw5{v%Jv',
        # 'USER': 'postgres',
        # 'PASSWORD': 'salam1392',
        'HOST': 'localhost',
        'port': '5432'
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

# Authentication backends
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)
# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/root/dining/static/'
AUTH_USER_MODEL = 'dining.CustomUser'
LOGIN_REDIRECT_URL = "/dashboard"
AUTH_PROFILE_MODULE = 'dining.dashboard'
LOGIN_URL = '/login'
