import os
from os.path import join
import logging
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)

SECRET_KEY = 'hldpr%r=(c=58n*tp6!vk#t$dhwqanx(^-d==z#okpijd&70xd'

DEBUG = False
TEMPLATE_DEBUG = DEBUG
DOMAIN_NAME = 'kioto.io'
ALLOWED_HOSTS = [DOMAIN_NAME]

SESSION_SAVE_EVERY_REQUEST = True

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'boxes',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
        "django.contrib.auth.context_processors.auth",
        "django.core.context_processors.debug",
        "django.core.context_processors.i18n",
        "django.core.context_processors.media",
        "django.core.context_processors.static",
        "django.core.context_processors.tz",
        "django.contrib.messages.context_processors.messages",
        "django.core.context_processors.request",
)

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = join(PROJECT_DIR,'static')


SOCIAL_AUTH_AUTHENTICATION_BACKENDS = (
    'social.backends.google.GoogleOAuth2',
)

try:
    #this file is unversionned and contains secrets such SECRET_KEY or database credentials
    import config.settings.secrets as secrets
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = secrets.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = secrets.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
except ImportError:
    logger.warning('secrets.py not found, Google auth won\'t work')


