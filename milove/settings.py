"""
Django settings for milove project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ej30v$ipwpnsr&vhn4tx0$w(5i79jagrtnnj3u_eelo)q7^q!8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ADMINS = []

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'milove.shop',
    'imagekit',
    'rest_framework',
    'corsheaders',
    'flat_responsive',
    'django_filters',
    'solo',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'milove.urls'

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

WSGI_APPLICATION = 'milove.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

# Authentication

AUTH_USER_MODEL = 'shop.User'
AUTHENTICATION_BACKENDS = ['milove.shop.auth.Backend']

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# REST framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ],
    'ORDERING_PARAM': 'o',
    'SEARCH_PARAM': 's',
}

# CSRF

CSRF_TRUSTED_ORIGINS = []

# CORS

CORS_ORIGIN_WHITELIST = []
CORS_URLS_REGEX = r'^/api/.*$'
CORS_ALLOW_CREDENTIALS = True

# Clickjacking protection

X_FRAME_OPTIONS = 'DENY'

# Mail

EMAIL_BACKEND = 'milove.mail.backends.HybridEmailBackend'
DEFAULT_FROM_EMAIL = 'no-reply@notification.milove.com'
MAIL_FROM_NAME = 'Milove'
SENDGRID_API_KEY = ''
SENDCLOUD_API_USER = ''
SENDCLOUD_API_KEY = ''

SERVER_EMAIL = 'server@notification.milove.com'

# Payment methods

STRIPE_API_KEY = ''
PAYPAL_MODE = 'sandbox'
PAYPAL_CLIENT_ID = ''
PAYPAL_CLIENT_SECRET = ''

# Thread pool

THREAD_POOL_MAX_WORKER = 20

# Shop configuration

ORDER_NOTIFICATION_GROUP_NAME = '订单管理员'
SELL_REQUEST_NOTIFICATION_GROUP_NAME = '出售请求管理员'
AMOUNT_TO_POINT = lambda x: int(x / 10.0)
POINT_TO_AMOUNT = lambda x: x / 100.0
POINT_TO_AMOUNT_REVERSE = lambda x: x * 100.0
MAX_ADDRESSES = 10  # the max number of addresses of a single user
PRODUCT_ADMIN_CATEGORY_LEVEL = 3

MAX_UPLOAD_SIZE = 5242880
