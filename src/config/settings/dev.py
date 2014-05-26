from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

INSTALLED_APPS += (
#     'debug_toolbar',
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

