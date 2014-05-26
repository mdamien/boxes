from .base import *

#this file is unversionned and contains secrets such SECRET_KEY or database credentials
import config.settings.secrets as secrets

SECRET_KEY = secrets.SECRET_KEY
ALLOWED_HOSTS = ['*']

USE_X_FORWARDED_HOST = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'mail.gandi.net'
EMAIL_HOST_USER = 'damien@kioto.io'
EMAIL_HOST_PASSWORD = secrets.EMAIL_HOST_PASSWORD
EMAIL_USE_SSL = True
